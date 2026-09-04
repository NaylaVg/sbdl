from odoo import api, fields, models
from odoo.exceptions import ValidationError


class Frasco(models.Model):
    _name = 'caen.frasco'
    _description = 'Frasco de leche'

    name = fields.Char(string='Código QR', required=True, index=True)
    donor_id = fields.Many2one('caen.donante', string='Donante', required=True)
    center_id = fields.Many2one('res.partner', string='Centro')
    visit_id = fields.Many2one('caen.visita', string='Visita de donación', ondelete='restrict')
    volume_ml = fields.Integer(string='Volumen (ml)')
    extraction_date = fields.Datetime(string='Fecha de extracción')
    milk_stage = fields.Selection([
        ('colostrum', 'Calostro'),
        ('transition', 'Transición'),
        ('mature_low', 'Madura baja'),
        ('mature_high', 'Madura alta'),
    ], string='Etapa de la leche')
    target = fields.Selection([
        ('preterm', 'Prematuro'),
        ('term', 'Término'),
    ], string='Destino')
    state = fields.Selection([
        ('raw', 'Crudo'),
        ('pasteurized', 'Pasteurizado'),
        ('fractioned', 'Fraccionado'),
        ('delivered', 'Entregado'),
        ('discarded', 'Descartado'),
    ], string='Estado', default='raw')

    lot_id = fields.Many2one('stock.lot', string='Lote/QR Stock', readonly=True, copy=False)
    product_id = fields.Many2one('product.product', string='Producto', readonly=True, copy=False)
    current_location_id = fields.Many2one('stock.location', string='Ubicación actual', readonly=True, copy=False)
    donor_apta = fields.Boolean(string='Donante Apta', related='donor_id.apta_donar', readonly=True)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            product = self.env.ref('caen_banco_leche.product_leche_cruda').product_variant_id
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
        for frasco in frascos:
            location = self.env.ref('caen_banco_leche.stock_location_recepcion')
            frasco._quitar_stock()
            frasco._sumar_stock(location)
        return frascos

    def _qty_litros(self):
        self.ensure_one()
        return (self.volume_ml / 1000.0) if self.volume_ml else 0

    def _quitar_stock(self):
        """Quita todo el stock de este lote de la ubicación actual."""
        self.ensure_one()
        if not self.current_location_id:
            return
        qty = self._qty_litros()
        if qty <= 0:
            return
        self.env['stock.quant']._update_available_quantity(
            self.product_id, self.current_location_id, -qty, lot_id=self.lot_id)

    def _sumar_stock(self, location):
        """Suma stock de este lote en la ubicación destino."""
        self.ensure_one()
        qty = self._qty_litros()
        if qty <= 0:
            return
        self.env['stock.quant']._update_available_quantity(
            self.product_id, location, qty, lot_id=self.lot_id)
        self.current_location_id = location

    def _cambiar_producto(self, new_product):
        """Cambia el producto del lote y del frasco."""
        self.ensure_one()
        self.lot_id.product_id = new_product.id
        self.product_id = new_product

    def _bitacora(self, action_type, changes):
        """Registra un evento de este frasco en la bitácora."""
        self.env['caen.bitacora']._registrar(
            'caen.frasco', self.id, self.name, action_type, changes)

    def action_pasteurizar(self):
        self.ensure_one()
        if not self.donor_id.apta_donar:
            raise ValidationError(
                'No se puede pasteurizar esta leche todavía: la donante no está apta.\n'
                'Debe tener las 7 serologías en OK y un consentimiento vigente.')
        if self.state != 'raw':
            raise ValidationError('Solo los frascos crudos pueden pasteurizarse.')
        self._quitar_stock()
        self._cambiar_producto(self.env.ref('caen_banco_leche.product_leche_pasteurizada').product_variant_id)
        dest = self.env.ref('caen_banco_leche.stock_location_heladera_pasty')
        self._sumar_stock(dest)
        self.state = 'pasteurized'
        self._bitacora('stage', 'Pasteurizado el frasco crudo -> pasteurizado.')
        return True

    def action_fraccionar(self):
        self.ensure_one()
        if self.state != 'pasteurized':
            raise ValidationError('Solo los frascos pasteurizados pueden fraccionarse.')
        self._quitar_stock()
        dest = self.env.ref('caen_banco_leche.stock_location_fraccionamiento')
        self._sumar_stock(dest)
        self.state = 'fractioned'
        self._bitacora('stage', 'Fraccionado el frasco pasteurizado -> fraccionado.')
        return True

    def action_entregar(self):
        self.ensure_one()
        if self.state != 'fractioned':
            raise ValidationError('Solo los frascos fraccionados pueden entregarse.')
        self._quitar_stock()
        self._cambiar_producto(self.env.ref('caen_banco_leche.product_biberon').product_variant_id)
        dest = self.env.ref('caen_banco_leche.stock_location_distribucion')
        self._sumar_stock(dest)
        self.state = 'delivered'
        self._bitacora('stage', 'Entregado el frasco fraccionado -> entregado.')
        return True

    def action_descartar(self):
        self.ensure_one()
        self._quitar_stock()
        dest = self.env.ref('caen_banco_leche.stock_location_descarte')
        self._sumar_stock(dest)
        self.state = 'discarded'
        self._bitacora('stage', 'Descartado el frasco (baja).')
        return True
