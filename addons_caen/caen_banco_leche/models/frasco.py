from odoo import api, fields, models
from odoo.exceptions import ValidationError


class Frasco(models.Model):
    # el modelo central del banco, un frasco de leche donada
    # tiene un ciclo de vida (crudo -> pasteurizado -> fraccionado ->
    # entregado) y se integra con el inventario de odoo para llevar el
    # stock en litros en cada ubicacion del deposito
    _name = 'caen.frasco'
    _description = 'Frasco de leche'

    # el codigo qr identifica al frasco y tambien es el numero de lote
    # en stock, por eso es obligatorio y esta indexado
    name = fields.Char(string='Código QR', required=True, index=True)
    donor_id = fields.Many2one('caen.donante', string='Donante', required=True)
    center_id = fields.Many2one('res.partner', string='Centro')
    # vinculo a la visita donde se dono, con ondelete restrict para que
    # no se pueda borrar una visita que ya tenga frascos
    visit_id = fields.Many2one('caen.visita', string='Visita de donación', ondelete='restrict')
    volume_ml = fields.Integer(string='Volumen (ml)')
    extraction_date = fields.Datetime(string='Fecha de extracción')
    # etapa de la leche segun el tiempo del parto
    milk_stage = fields.Selection([
        ('colostrum', 'Calostro'),
        ('transition', 'Transición'),
        ('mature_low', 'Madura baja'),
        ('mature_high', 'Madura alta'),
    ], string='Etapa de la leche')
    # a que tipo de bebe va destinada, prematuro o termino
    target = fields.Selection([
        ('preterm', 'Prematuro'),
        ('term', 'Término'),
    ], string='Destino')
    # ciclo de vida del frasco, arranca en crudo
    state = fields.Selection([
        ('raw', 'Crudo'),
        ('pasteurized', 'Pasteurizado'),
        ('fractioned', 'Fraccionado'),
        ('delivered', 'Entregado'),
        ('discarded', 'Descartado'),
    ], string='Estado', default='raw')

    # campos de integracion con stock, de solo lectura porque los maneja
    # el sistema, no el usuario
    lot_id = fields.Many2one('stock.lot', string='Lote/QR Stock', readonly=True, copy=False)
    product_id = fields.Many2one('product.product', string='Producto', readonly=True, copy=False)
    current_location_id = fields.Many2one('stock.location', string='Ubicación actual', readonly=True, copy=False)
    # relacionado con la aptitud de la donante, lo muestro en el form
    # para que el personal sepa si puede pasteurizar
    donor_apta = fields.Boolean(string='Donante Apta', related='donor_id.apta_donar', readonly=True)

    # al crear el frasco genero el lote de stock y lo ingreso en recepcion,
    # asi queda registrado en el inventario apenas se crea, sin pasos manuales
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            # el frasco nuevo siempre es leche cruda
            product = self.env.ref('caen_banco_leche.product_leche_cruda').product_variant_id
            # si ya existe un lote con ese qr lo reutilizo, si no lo creo
            existing_lot = self.env['stock.lot'].search([
                ('name', '=', vals['name']),
            ], limit=1)
            if existing_lot:
                lot = existing_lot
            else:
                lot = self.env['stock.lot'].create({
                    'name': vals['name'],
                    'product_id': product.id,
                })
            vals['lot_id'] = lot.id
            vals['product_id'] = product.id
        frascos = super().create(vals_list)
        # ingreso el stock de cada frasco en recepcion
        for frasco in frascos:
            location = self.env.ref('caen_banco_leche.stock_location_recepcion')
            frasco._quitar_stock()
            frasco._sumar_stock(location)
        return frascos

    # paso el volumen de mililitros a litros, la unidad del inventario
    def _qty_litros(self):
        self.ensure_one()
        return (self.volume_ml / 1000.0) if self.volume_ml else 0

    # saco el stock de la ubicacion actual del lote
    def _quitar_stock(self):
        self.ensure_one()
        if not self.current_location_id:
            return
        qty = self._qty_litros()
        if qty <= 0:
            return
        self.env['stock.quant']._update_available_quantity(
            self.product_id, self.current_location_id, -qty, lot_id=self.lot_id)

    # sumo stock del lote en la ubicacion destino y actualizo la ubicacion
    def _sumar_stock(self, location):
        self.ensure_one()
        qty = self._qty_litros()
        if qty <= 0:
            return
        self.env['stock.quant']._update_available_quantity(
            self.product_id, location, qty, lot_id=self.lot_id)
        self.current_location_id = location

    # cambio el producto del lote y del frasco, para pasar de cruda a
    # pasteurizada o a biberon
    def _cambiar_producto(self, new_product):
        self.ensure_one()
        self.lot_id.product_id = new_product.id
        self.product_id = new_product

    # registro un evento del frasco en la bitacora
    def _bitacora(self, action_type, changes):
        self.env['caen.bitacora']._registrar(
            'caen.frasco', self.id, self.name, action_type, changes)

    # boton pasteurizar, paso de crudo a pasteurizado
    def action_pasteurizar(self):
        self.ensure_one()
        # regla de negocio principal, solo se pasteuriza si la donante
        # esta apta (7 serologias en ok y consentimiento vigente)
        if not self.donor_id.apta_donar:
            raise ValidationError(
                'No se puede pasteurizar esta leche todavía: la donante no está apta.\n'
                'Debe tener las 7 serologías en OK y un consentimiento vigente.')
        # no se puede saltar de etapa, solo se pasteuriza un crudo
        if self.state != 'raw':
            raise ValidationError('Solo los frascos crudos pueden pasteurizarse.')
        # saco stock de recepcion, cambio el producto a pasteurizada y lo
        # muevo a la heladera de pasteurizados
        self._quitar_stock()
        self._cambiar_producto(self.env.ref('caen_banco_leche.product_leche_pasteurizada').product_variant_id)
        dest = self.env.ref('caen_banco_leche.stock_location_heladera_pasty')
        self._sumar_stock(dest)
        self.state = 'pasteurized'
        self._bitacora('stage', 'Pasteurizado el frasco crudo -> pasteurizado.')
        return True

    # boton fraccionar, paso de pasteurizado a fraccionado
    def action_fraccionar(self):
        self.ensure_one()
        if self.state != 'pasteurized':
            raise ValidationError('Solo los frascos pasteurizados pueden fraccionarse.')
        # muevo el stock a la ubicacion de fraccionamiento
        self._quitar_stock()
        dest = self.env.ref('caen_banco_leche.stock_location_fraccionamiento')
        self._sumar_stock(dest)
        self.state = 'fractioned'
        self._bitacora('stage', 'Fraccionado el frasco pasteurizado -> fraccionado.')
        return True

    # boton entregar, paso de fraccionado a entregado
    def action_entregar(self):
        self.ensure_one()
        if self.state != 'fractioned':
            raise ValidationError('Solo los frascos fraccionados pueden entregarse.')
        # cambio el producto a biberon y lo muevo a distribucion
        self._quitar_stock()
        self._cambiar_producto(self.env.ref('caen_banco_leche.product_biberon').product_variant_id)
        dest = self.env.ref('caen_banco_leche.stock_location_distribucion')
        self._sumar_stock(dest)
        self.state = 'delivered'
        self._bitacora('stage', 'Entregado el frasco fraccionado -> entregado.')
        return True

    # boton descartar, disponible siempre, muevo el stock a descarte
    def action_descartar(self):
        self.ensure_one()
        self._quitar_stock()
        dest = self.env.ref('caen_banco_leche.stock_location_descarte')
        self._sumar_stock(dest)
        self.state = 'discarded'
        self._bitacora('stage', 'Descartado el frasco (baja).')
        return True
