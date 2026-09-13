from odoo import api, fields, models


class Paciente(models.Model):
    # el bebe que recibe la leche donada
    _name = 'caen.paciente'
    _description = 'Bebé receptor'
    _rec_name = 'name'

    name = fields.Char(string='Nombre completo', required=True)
    # sexo del bebe, importante para las curvas de crecimiento oms
    # varones y mujeres tienen tablas distintas de peso y talla
    sexo = fields.Selection([
        ('m', 'Masculino'),
        ('f', 'Femenino'),
    ], string='Sexo')
    birth_date = fields.Date(string='Fecha de nacimiento')
    birth_weight_g = fields.Integer(string='Peso de nacimiento (g)')
    gestational_age_weeks = fields.Integer(string='Semanas de gestación')
    gestational_age_days = fields.Integer(string='Días de gestación')
    apgar_1min = fields.Integer(string='Apgar 1 min')
    apgar_5min = fields.Integer(string='Apgar 5 min')
    birth_height_cm = fields.Float(string='Talla de nacimiento (cm)')
    head_circumference_cm = fields.Float(string='Perímetro cefálico de nacimiento (cm)')
    diagnosis = fields.Text(string='Diagnóstico / motivo de internación')
    admission_date = fields.Date(string='Fecha de internación')
    record_number = fields.Char(string='Nº de expediente / historia clínica')
    # si la madre del bebe ademas es donante, lo vinculo aca
    mother_id = fields.Many2one('caen.donante', string='Madre (si es donante)')

    # ciclo de internacion: internado mientras este en neonatologia
    state = fields.Selection([
        ('admitted', 'Internado'),
        ('discharged', 'Egresado'),
        ('transferred', 'Derivado'),
        ('deceased', 'Fallecido'),
    ], string='Estado de internación', default='admitted')

    # los planes de alimentacion y las leches que recibio
    plan_ids = fields.One2many('caen.plan_alimentacion', 'patient_id',
                               string='Planes de alimentación')
    distribution_ids = fields.One2many('caen.distribucion', 'patient_id',
                                       string='Distribuciones recibidas')
    # la evolucion diaria del rnar en neonatologia
    evolution_ids = fields.One2many('caen.evolucion_diaria', 'patient_id',
                                    string='Evolución diaria')
    # tratamientos o medicacion que recibe el bebe
    treatments = fields.Text(string='Tratamientos y medicación')
    n_evolutions = fields.Integer(
        string='Días de evolución registrados',
        compute='_compute_n_evolutions')

    @api.depends('evolution_ids')
    def _compute_n_evolutions(self):
        for rec in self:
            rec.n_evolutions = len(rec.evolution_ids)