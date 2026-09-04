from odoo import api, fields, models


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
