from odoo import api, fields, models


class Consentimiento(models.Model):
    _name = 'caen.consentimiento'
    _description = 'Consentimiento de donación'

    donor_id = fields.Many2one('caen.donante', string='Donante',
                               required=True)
    bottles_to_print = fields.Integer(string='Cantidad de frascos a imprimir',
                                      default=0)
    photo_permission = fields.Boolean(string='Permite uso de fotos', default=False)
    state = fields.Selection([
        ('draft', 'Borrador'),
        ('active', 'Vigente'),
        ('expired', 'Vencido'),
        ('revoked', 'Revocado'),
    ], string='Estado', default='draft')
    start_date = fields.Date(string='Fecha de inicio')
    end_date = fields.Date(string='Fecha de fin')
