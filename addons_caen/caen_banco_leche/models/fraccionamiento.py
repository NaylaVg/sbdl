from odoo import api, fields, models
from .qr_utils import generar_qr_imagen, construir_url_registro


class Fraccionamiento(models.Model):
    # registro del fraccionamiento: se divide la leche pasteurizada
    # de un frasco en varios biberones mas chicos
    _name = 'caen.fraccionamiento'
    _description = 'Registro de fraccionamiento de leche'

    pasteurization_id = fields.Many2one('caen.pasteurizacion',
                                        string='Pasteurización', required=True)
    fractionation_date = fields.Date(string='Fecha del fraccionamiento')
    staff_id = fields.Many2one('hr.employee', string='Responsable')

    # los biberones que salieron del fraccionamiento
    bottle_ids = fields.One2many('caen.biberon', 'fractionation_id',
                                 string='Biberones generados')


class Biberon(models.Model):
    # un biberon individual con su propio qr, resultado del fraccionamiento
    _name = 'caen.biberon'
    _description = 'Biberón fraccionado'

    fractionation_id = fields.Many2one('caen.fraccionamiento',
                                       string='Fraccionamiento', required=True)
    qr_code = fields.Char(string='Código QR del biberón', index=True)
    qr_image = fields.Binary('Imagen QR', attachment=True, readonly=True)
    volume_ml = fields.Integer(string='Volumen (ml)')
    milk_stage = fields.Selection([
        ('colostrum', 'Calostro'),
        ('transition', 'Transición'),
        ('mature_low', 'Madura baja'),
        ('mature_high', 'Madura alta'),
    ], string='Etapa')
    target = fields.Selection([
        ('preterm', 'Prematuro'),
        ('term', 'Término'),
    ], string='Destino')

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('qr_code'):
                frac = self.env['caen.fraccionamiento'].browse(
                    vals.get('fractionation_id'))
                if frac.exists() and frac.pasteurization_id:
                    base = frac.pasteurization_id.new_barcode or 'BIB'
                    count = self.search_count([
                        ('fractionation_id', '=', frac.id)])
                    vals['qr_code'] = f"{base}-B{count + 1:02d}"
        biberones = super().create(vals_list)
        for bib in biberones:
            if bib.id:
                url = construir_url_registro(
                    self.env, 'caen.biberon', bib.id)
                if url:
                    imagen = generar_qr_imagen(url)
                    if imagen:
                        bib.qr_image = imagen
        return biberones

    def action_generar_qr(self):
        for bib in self:
            if bib.id:
                url = construir_url_registro(
                    self.env, 'caen.biberon', bib.id)
                if url:
                    imagen = generar_qr_imagen(url)
                    if imagen:
                        bib.qr_image = imagen
