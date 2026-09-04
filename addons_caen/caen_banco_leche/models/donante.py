from odoo import api, fields, models


class Donante(models.Model):
    _name = 'caen.donante'
    _description = 'Madre Donante'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'

    name = fields.Char(string='Nombre completo', required=True)
    dni = fields.Char(string='DNI', size=20)
    birth_date = fields.Date(string='Fecha de nacimiento')
    phone = fields.Char(string='Teléfono')
    email = fields.Char(string='Email')
    address = fields.Text(string='Domicilio')
    center_id = fields.Many2one(
        'res.partner', string='Centro de recolección',
        help='Centro al que pertenece la donante (SPE, Vidal, etc.)')

    consent_ids = fields.One2many('caen.consentimiento', 'donor_id',
                                  string='Consentimientos')
    serology_ids = fields.One2many('caen.serologia', 'donor_id',
                                   string='Serologías')
    batch_ids = fields.One2many('caen.frasco', 'donor_id',
                                string='Frascos')
    visit_ids = fields.One2many('caen.visita', 'donor_id',
                                string='Visitas de donación')

    next_visit_due = fields.Date(string='Próxima visita programada')
    state = fields.Selection([
        ('draft', 'Borrador'),
        ('active', 'Activa'),
        ('dismissed', 'Baja'),
    ], string='Estado', default='draft')

    serologias_ok = fields.Integer(
        string='Serologías aptas',
        compute='_compute_serologias_ok')
    serologias_pendientes = fields.Integer(
        string='Serologías pendientes',
        compute='_compute_serologias_ok')
    apta_donar = fields.Boolean(
        string='Apta para donar',
        compute='_compute_serologias_ok')
    n_frascos = fields.Integer(
        string='Cantidad de frascos',
        compute='_compute_n_frascos')

    @api.depends('batch_ids')
    def _compute_n_frascos(self):
        for rec in self:
            rec.n_frascos = len(rec.batch_ids)

    @api.depends('serology_ids.result', 'consent_ids.state',
                 'consent_ids.start_date', 'consent_ids.end_date')
    def _compute_serologias_ok(self):
        today = fields.Date.context_today(self)
        for rec in self:
            rec.serologias_ok = len(rec.serology_ids.filtered(
                lambda s: s.result == 'ok'))
            rec.serologias_pendientes = len(rec.serology_ids.filtered(
                lambda s: s.result == 'pending'))
            consent_vigente = rec.consent_ids.filtered(
                lambda c: c.state == 'active' and c.start_date <= today
                and (not c.end_date or c.end_date >= today))
            rec.apta_donar = rec.state == 'active' and rec.serologias_ok >= 7 \
                and bool(consent_vigente)
