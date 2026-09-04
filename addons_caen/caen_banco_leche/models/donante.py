from odoo import api, fields, models


class Donante(models.Model):
    # la madre donante del banco de leche
    _name = 'caen.donante'
    _description = 'Madre Donante'
    # heredo de mail para tener historial de mensajes y actividades
    # en la ficha de la donante
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'

    name = fields.Char(string='Nombre completo', required=True)
    dni = fields.Char(string='DNI', size=20)
    birth_date = fields.Date(string='Fecha de nacimiento')
    phone = fields.Char(string='Teléfono')
    email = fields.Char(string='Email')
    address = fields.Text(string='Domicilio')
    # centro al que pertenece, reutilizo res.partner (los contactos de odoo)
    # para no duplicar un modelo de centros
    center_id = fields.Many2one(
        'res.partner', string='Centro de recolección',
        help='Centro al que pertenece la donante (SPE, Vidal, etc.)')

    # relaciones uno a muchos con los hijos, cada hijo guarda un donor_id
    # que apunta de vuelta a esta donante
    consent_ids = fields.One2many('caen.consentimiento', 'donor_id',
                                  string='Consentimientos')
    serology_ids = fields.One2many('caen.serologia', 'donor_id',
                                   string='Serologías')
    batch_ids = fields.One2many('caen.frasco', 'donor_id',
                                string='Frascos')
    visit_ids = fields.One2many('caen.visita', 'donor_id',
                                string='Visitas de donación')

    next_visit_due = fields.Date(string='Próxima visita programada')
    # ciclo de vida: borrador al crearla, activa mientras dona y baja
    # cuando deja de donar
    state = fields.Selection([
        ('draft', 'Borrador'),
        ('active', 'Activa'),
        ('dismissed', 'Baja'),
    ], string='Estado', default='draft')

    # campos calculados, no se guardan, odoo los recalcula con el metodo
    # que indica el atributo compute
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

    # cuenta los frascos de la donante, se dispara al agregar o quitar uno
    @api.depends('batch_ids')
    def _compute_n_frascos(self):
        for rec in self:
            rec.n_frascos = len(rec.batch_ids)

    # resume el estado de salud de la donante
    @api.depends('serology_ids.result', 'consent_ids.state',
                 'consent_ids.start_date', 'consent_ids.end_date')
    def _compute_serologias_ok(self):
        # uso la fecha del usuario, no la del servidor
        today = fields.Date.context_today(self)
        for rec in self:
            rec.serologias_ok = len(rec.serology_ids.filtered(
                lambda s: s.result == 'ok'))
            rec.serologias_pendientes = len(rec.serology_ids.filtered(
                lambda s: s.result == 'pending'))
            # busco un consentimiento activo, vigente a la fecha de hoy
            consent_vigente = rec.consent_ids.filtered(
                lambda c: c.state == 'active' and c.start_date <= today
                and (not c.end_date or c.end_date >= today))
            # apta solo si esta activa, aprobo las 7 serologias y tiene
            # consentimiento vigente
            rec.apta_donar = rec.state == 'active' and rec.serologias_ok >= 7 \
                and bool(consent_vigente)
