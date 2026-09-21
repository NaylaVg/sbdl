from odoo import models, fields


class ResPartner(models.Model):
    _inherit = 'res.partner'

    es_centro_recoleccion = fields.Boolean(string='Es centro de recolección')
    horario_atencion = fields.Char(string='Horario de atención')
    referente_centro = fields.Char(string='Persona referente')