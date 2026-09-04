from odoo import api, fields, models


class Paciente(models.Model):
    # el bebe que recibe la leche donada
    _name = 'caen.paciente'
    _description = 'Bebé receptor'
    _rec_name = 'name'

    name = fields.Char(string='Nombre completo', required=True)
    birth_date = fields.Date(string='Fecha de nacimiento')
    birth_weight_g = fields.Integer(string='Peso de nacimiento (g)')
    gestational_age_weeks = fields.Integer(string='Semanas de gestación')
    # si la madre del bebe ademas es donante, lo vinculo aca
    mother_id = fields.Many2one('caen.donante', string='Madre (si es donante)')

    # los planes de alimentacion y las leches que recibio
    plan_ids = fields.One2many('caen.plan_alimentacion', 'patient_id',
                               string='Planes de alimentación')
    distribution_ids = fields.One2many('caen.distribucion', 'patient_id',
                                       string='Distribuciones recibidas')
