from odoo import fields, models


class EvolucionDiaria(models.Model):
    # el registro diario de cada rnar internado en neonatologia
    # va ligado al paciente y se completa una vez por dia
    _name = 'caen.evolucion_diaria'
    _description = 'Evolución diaria de un RNAR'
    _order = 'record_date desc'

    patient_id = fields.Many2one('caen.paciente', string='Paciente',
                                 required=True)
    record_date = fields.Date(string='Fecha', required=True,
                              default=fields.Date.context_today)
    weight_g = fields.Integer(string='Peso (g)')
    height_cm = fields.Float(string='Talla (cm)')
    head_circumference_cm = fields.Float(string='Perímetro cefálico (cm)')
    notes = fields.Text(string='Evolución clínica / observaciones')