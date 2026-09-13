from odoo import api, fields, models


class PlanAlimentacion(models.Model):
    _name = 'caen.plan_alimentacion'
    _description = 'Plan de alimentación de un paciente'

    patient_id = fields.Many2one('caen.paciente', string='Paciente',
                                 required=True)
    # tipo de alimento que recibe el bebe
    # leche humana pasteurizada, formula o mixta
    # en la planilla 15 del contexto se ve que se anota esto por bebe
    daily_volume_ml = fields.Integer(string='Volumen diario (ml)')
    frequency_per_day = fields.Integer(string='Tomas por día')
    kcal_per_day = fields.Integer(string='Kcal por día')
    # tipo de alimento que recibe el bebe
    # leche humana pasteurizada, formula o mixta
    tipo_alimento = fields.Selection([
        ('lh', 'Leche humana pasteurizada'),
        ('formula', 'Fórmula'),
        ('mixta', 'Mixta (leche humana + fórmula)'),
        ('fortificada', 'Leche humana fortificada'),
    ], string='Tipo de alimento')
    # subtipo segun la leche del banco (calostro, transicion, madura)
    # esto lo maneja el personal segun la donante
    milk_stage = fields.Selection([
        ('colostrum', 'Calostro'),
        ('transition', 'Transición'),
        ('mature_low', 'Madura baja'),
        ('mature_high', 'Madura alta'),
    ], string='Etapa de la leche')
    # destino: leche para prematuro o para termino
    target = fields.Selection([
        ('preterm', 'Prematuro'),
        ('term', 'Término'),
    ], string='Destino')
    # fortificante que se le agrega a la leche humana
    fortifier = fields.Char(string='Fortificante')
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
