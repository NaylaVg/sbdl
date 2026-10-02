from odoo import api, fields, models


class PlanAlimentacion(models.Model):
    # plan de alimentacion de un paciente rn
    # guarda que alimento recibe, volumen diario y calcula nutrientes
    _name = 'caen.plan_alimentacion'
    _description = 'Plan de alimentación de un paciente'

    patient_id = fields.Many2one('caen.paciente', string='Paciente',
                                 required=True)
    # alimento seleccionado del catalogo de alimentos
    alimento_id = fields.Many2one('caen.alimento', string='Alimento')
    # tipo de alimento: lh, formula, mixta o fortificada
    tipo_alimento = fields.Selection([
        ('lh', 'Leche humana pasteurizada'),
        ('formula', 'Fórmula'),
        ('mixta', 'Mixta (leche humana + fórmula)'),
        ('fortificada', 'Leche humana fortificada'),
    ], string='Tipo de alimento')
    # etapa de la leche humana
    milk_stage = fields.Selection([
        ('colostrum', 'Calostro'),
        ('transition', 'Transición'),
        ('mature_low', 'Madura baja'),
        ('mature_high', 'Madura alta'),
    ], string='Etapa de la leche')
    # destino de la leche
    target = fields.Selection([
        ('preterm', 'Prematuro'),
        ('term', 'Término'),
    ], string='Destino')
    # fortificante usado
    fortifier = fields.Char(string='Fortificante')
    # volumen y tomas
    daily_volume_ml = fields.Integer(string='Volumen diario (ml)')
    frequency_per_day = fields.Integer(string='Tomas por día')
    # valores calculados a partir del alimento y volumen
    kcal_per_day = fields.Float(string='Kcal por día',
                                compute='_compute_kcal',
                                store=True)
    protein_g_day = fields.Float(string='Proteínas por día (g)',
                                 compute='_compute_kcal', store=True)
    fat_g_day = fields.Float(string='Grasas por día (g)',
                             compute='_compute_kcal', store=True)
    calcium_mg_day = fields.Float(string='Calcio por día (mg)',
                                  compute='_compute_kcal', store=True)

    start_date = fields.Date(string='Fecha de inicio')
    end_date = fields.Date(string='Fecha de fin')

    # adecuacion automatica de la alimentacion
    adecuacion = fields.Selection([
        ('adecuado', 'Adecuado'),
        ('insuficiente', 'Insuficiente'),
        ('excesivo', 'Excesivo'),
        ('no_evaluable', 'No evaluable'),
    ], string='Adecuación de la alimentación', compute='_compute_adecuacion',
       store=True)
    kcal_necesarias_estimadas = fields.Float(string='Kcal necesarias estimadas',
                                             compute='_compute_adecuacion',
                                             store=True)

    tracking_ids = fields.One2many('caen.seguimiento_nutricional',
                                   'plan_id', string='Seguimientos')

    # calculo las calorias y nutrientes por dia cuando cambio el volumen o el alimento
    @api.depends('alimento_id', 'daily_volume_ml')
    def _compute_kcal(self):
        for rec in self:
            # por defecto dejo todo en cero por si no hay alimento o volumen cargado
            rec.kcal_per_day = 0.0
            rec.protein_g_day = 0.0
            rec.fat_g_day = 0.0
            rec.calcium_mg_day = 0.0
            if rec.alimento_id and rec.daily_volume_ml:
                # divido el volumen por 100 para saber cuantas veces aplico la composicion
                factor = rec.daily_volume_ml / 100.0
                rec.kcal_per_day = rec.alimento_id.kcal * factor
                rec.protein_g_day = rec.alimento_id.protein_g * factor
                rec.fat_g_day = rec.alimento_id.fat_g * factor
                rec.calcium_mg_day = rec.alimento_id.calcium_mg * factor

    # evaluo la adecuacion de la alimentacion segun el paciente
    @api.depends('kcal_per_day', 'patient_id', 'patient_id.gestational_age_weeks',
                 'patient_id.gestational_age_days', 'patient_id.birth_weight_g')
    def _compute_adecuacion(self):
        for rec in self:
            rec.adecuacion = 'no_evaluable'
            rec.kcal_necesarias_estimadas = 0.0
            if not rec.patient_id:
                continue
            eg_weeks = rec.patient_id.gestational_age_weeks or 0
            eg_days = rec.patient_id.gestational_age_days or 0
            birth_weight_g = rec.patient_id.birth_weight_g or 0
            # calculo edad gestacional total en semanas aproximadas
            eg_total_weeks = eg_weeks + (eg_days / 7.0)
            kcal_est = 0.0
            # estimacion simple segun peso para neonatos (referencia general)
            if birth_weight_g > 0:
                peso_kg = birth_weight_g / 1000.0
                # prematuros suelen necesitar mas kcal/kg (100-120)
                # termino ~80-100
                if eg_total_weeks < 34:
                    kcal_est = peso_kg * 110
                elif eg_total_weeks < 37:
                    kcal_est = peso_kg * 100
                else:
                    kcal_est = peso_kg * 90
            rec.kcal_necesarias_estimadas = round(kcal_est, 2)
            if kcal_est <= 0 or rec.kcal_per_day <= 0:
                rec.adecuacion = 'no_evaluable'
                continue
            # tolerancia simple: dentro del 10% considero adecuado
            diferencia = abs(rec.kcal_per_day - kcal_est)
            margen = kcal_est * 0.10
            if rec.kcal_per_day < kcal_est - margen:
                rec.adecuacion = 'insuficiente'
            elif rec.kcal_per_day > kcal_est + margen:
                rec.adecuacion = 'excesivo'
            else:
                rec.adecuacion = 'adecuado'


class SeguimientoNutricional(models.Model):
    # seguimiento de crecimiento y nutricion por fecha
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
