from odoo import api, fields, models


class PlanAlimentacion(models.Model):
    _name = 'caen.plan_alimentacion'
    _description = 'Plan de alimentación de un paciente'

    patient_id = fields.Many2one('caen.paciente', string='Paciente',
                                 required=True)
    daily_volume_ml = fields.Integer(string='Volumen diario (ml)')
    frequency_per_day = fields.Integer(string='Tomas por día')
    kcal_per_day = fields.Integer(string='Kcal por día')
    start_date = fields.Date(string='Fecha de inicio')
    end_date = fields.Date(string='Fecha de fin')

    tracking_ids = fields.One2many('caen.seguimiento_nutricional',
                                   'plan_id', string='Seguimientos')


class SeguimientoNutricional(models.Model):
    _name = 'caen.seguimiento_nutricional'
    _description = 'Seguimiento nutricional del paciente'

    plan_id = fields.Many2one('caen.plan_alimentacion', string='Plan',
                              required=True)
    patient_id = fields.Many2one('caen.paciente', string='Paciente',
                                 related='plan_id.patient_id')
    tracking_date = fields.Date(string='Fecha')
    weight_g = fields.Integer(string='Peso (g)')
    height_cm = fields.Float(string='Talla (cm)')
    head_circumference_cm = fields.Float(string='Perímetro cefálico (cm)')
    z_score_weight = fields.Float(string='Z-score peso')
    z_score_height = fields.Float(string='Z-score talla')
