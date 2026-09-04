from odoo import api, fields, models


class Consentimiento(models.Model):
    # el consentimiento informado que firma la donante, tiene que estar
    # vigente para que ella pueda donar
    _name = 'caen.consentimiento'
    _description = 'Consentimiento de donación'

    donor_id = fields.Many2one('caen.donante', string='Donante',
                               required=True)
    # cuantos frascos tiene permitido imprimir segun lo firmado
    bottles_to_print = fields.Integer(string='Cantidad de frascos a imprimir',
                                      default=0)
    photo_permission = fields.Boolean(string='Permite uso de fotos', default=False)
    # ciclo de vida: borrador, vigente, vencido o revocado
    state = fields.Selection([
        ('draft', 'Borrador'),
        ('active', 'Vigente'),
        ('expired', 'Vencido'),
        ('revoked', 'Revocado'),
    ], string='Estado', default='draft')
    # vigencia del consentimiento
    start_date = fields.Date(string='Fecha de inicio')
    end_date = fields.Date(string='Fecha de fin')
