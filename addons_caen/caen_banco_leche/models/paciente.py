from odoo import api, fields, models


class Paciente(models.Model):
    _name = 'caen.paciente'
    _description = 'Bebé receptor'
    _rec_name = 'name'

    name = fields.Char(string='Nombre completo', required=True)
    birth_date = fields.Date(string='Fecha de nacimiento')
    birth_weight_g = fields.Integer(string='Peso de nacimiento (g)')
    gestational_age_weeks = fields.Integer(string='Semanas de gestación')
    mother_id = fields.Many2one('caen.donante', string='Madre (si es donante)')

    plan_ids = fields.One2many('caen.plan_alimentacion', 'patient_id',
                               string='Planes de alimentación')
    distribution_ids = fields.One2many('caen.distribucion', 'patient_id',
                                       string='Distribuciones recibidas')
