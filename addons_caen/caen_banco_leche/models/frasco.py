from odoo import api, fields, models
from odoo.exceptions import ValidationError
from .qr_utils import generar_qr_imagen, construir_url_registro


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
    reception_date = fields.Datetime(string='Fecha de recepción')
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
    # tipo de leche segun edad gestacional y dias post-nacimiento (C/T/M)
    milk_type = fields.Selection([
        ('C', 'Calostro'),
        ('T', 'Transición'),
        ('M', 'Madura'),
    ], string='Tipo de leche')
    # dias desde el nacimiento del bebe hasta la extraccion
    days_from_birth = fields.Integer(string='Días desde nacimiento', compute='_compute_days')
    # dias desde la extraccion hasta la pasteurizacion
    days_to_pasteurization = fields.Integer(
        string='Días a pasteurización', compute='_compute_days')
    # tipo de leche como texto para reporte y etiqueta
    tipo_leche = fields.Char(string='Tipo de leche', compute='_compute_tipo_leche')
    # valores nutricionales por 100 ml del frasco (para seguimiento del bebe)
    hc = fields.Float(string='Hidratos (g/100ml)')
    protein = fields.Float(string='Proteína (g/100ml)')
    fat = fields.Float(string='Grasa (g/100ml)')
    calcium = fields.Float(string='Calcio (mg/100ml)')
    iron = fields.Float(string='Hierro (mg/100ml)')
    phosphorus = fields.Float(string='Fósforo (mg/100ml)')
    vit_c = fields.Float(string='Vit C (mg/100ml)')
    vit_d = fields.Float(string='Vit D (mcg/100ml)')
    # resultado de cultivos como texto
    total_col = fields.Float(string='Total colíneos')
    confirmation = fields.Selection([
        ('confirmado', 'Confirmado'),
        ('no_confirmado', 'No confirmado'),
    ], string='Confirmación')
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
    # imagen del codigo qr generada a partir del campo name
    qr_image = fields.Binary('Imagen QR', attachment=True, readonly=True)

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
        # genero el qr para cada frasco nuevo
        frascos._generar_qr_si_falta()
        # ingreso el stock de cada frasco en recepcion
        for frasco in frascos:
            location = self.env.ref('caen_banco_leche.stock_location_recepcion')
            frasco._quitar_stock()
            frasco._sumar_stock(location)
        return frascos

    def action_generar_qr(self):
        """Genera (o regenera) la imagen QR con la URL del registro en Odoo.
        Se llama desde el boton 'Generar QR' en el formulario."""
        for frasco in self:
            url = construir_url_registro(
                self.env, 'caen.frasco', frasco.id)
            if url:
                imagen = generar_qr_imagen(url)
                if imagen:
                    frasco.qr_image = imagen

    def _generar_qr_si_falta(self):
        """Genera el QR automaticamente si el campo esta vacio.
        Se llama desde create."""
        for frasco in self:
            if not frasco.qr_image and frasco.id:
                url = construir_url_registro(
                    self.env, 'caen.frasco', frasco.id)
                if url:
                    imagen = generar_qr_imagen(url)
                    if imagen:
                        frasco.qr_image = imagen

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

    # devuelve color CSS para el badge de estado en la ficha
    def get_state_color(self, state):
        colors = {
            'raw': '#dc3545',        # rojo - crudo
            'pasteurized': '#28a745', # verde - pasteurizado
            'fractioned': '#17a2b8', # azul claro - fraccionado
            'delivered': '#6c757d',  # gris - entregado
            'discarded': '#6f42c1',  # púrpura - descartado
        }
        return 'color: %s;' % colors.get(state, '#6c757d')

    # calcula dias desde nacimiento y dias a pasteurizacion
    @api.depends('extraction_date', 'donor_id.baby_birth_date')
    def _compute_days(self):
        for frasco in self:
            frasco.days_from_birth = 0
            frasco.days_to_pasteurization = 0
            if frasco.extraction_date and frasco.donor_id and frasco.donor_id.baby_birth_date:
                fecha_extraccion = frasco.extraction_date.date()
                fecha_nacimiento = frasco.donor_id.baby_birth_date
                frasco.days_from_birth = (fecha_extraccion - fecha_nacimiento).days
                if frasco.state == 'pasteurized':
                    # busca la fecha de pasteurizacion aproximada (estado cambiado)
                    frasco.days_to_pasteurization = (
                        fecha_extraccion - fecha_nacimiento).days

    # calcula tipo de leche segun edad gestacional y dias post-nacimiento
    # C: calostro, T: transicion, M: madura
    @api.depends('days_from_birth', 'donor_id.baby_eg_weeks')
    def _compute_milk_type(self):
        for frasco in self:
            frasco.milk_type = 'M'  # default madura
            if not frasco.days_from_birth:
                continue
            eg = frasco.donor_id.baby_eg_weeks or 40
            dias = frasco.days_from_birth
            if eg < 34:  # prematuro muy prematuro
                if dias <= 10:
                    frasco.milk_type = 'C'
                elif dias <= 21:
                    frasco.milk_type = 'T'
                else:
                    frasco.milk_type = 'M'
            elif eg < 37:  # pretemino
                if dias <= 7:
                    frasco.milk_type = 'C'
                elif dias <= 14:
                    frasco.milk_type = 'T'
                else:
                    frasco.milk_type = 'M'
            else:  # termino
                if dias <= 5:
                    frasco.milk_type = 'C'
                elif dias <= 10:
                    frasco.milk_type = 'T'
                else:
                    frasco.milk_type = 'M'

    @api.depends('milk_type')
    def _compute_tipo_leche(self):
        for frasco in self:
            tipos = {'C': 'Calostro', 'T': 'Transición', 'M': 'Madura'}
            frasco.tipo_leche = tipos.get(frasco.milk_type or 'M', 'Madura')
