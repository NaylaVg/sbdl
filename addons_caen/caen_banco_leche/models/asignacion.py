from odoo import models, fields, api


class AsignacionCaen(models.Model):
    _name = 'caen.asignacion'
    _description = 'Asignación diaria de tareas/turnos'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'
    _order = 'fecha desc, turno'

    name = fields.Char(string='Referencia', compute='_compute_name', store=True)
    fecha = fields.Date(string='Fecha', required=True, default=fields.Date.context_today)
    turno = fields.Selection([
        ('manana', 'Mañana'),
        ('tarde', 'Tarde'),
        ('noche', 'Noche'),
    ], string='Turno', required=True)
    empleado_id = fields.Many2one('hr.employee', string='Personal asignado', required=True)
    encargada_id = fields.Many2one('res.users', string='Asignado por',
                                    default=lambda self: self.env.user)
    area = fields.Selection([
        ('recoleccion', 'Recolección'),
        ('pasteurizacion', 'Pasteurización'),
        ('distribucion', 'Distribución'),
        ('otro', 'Otro'),
    ], string='Área')
    descripcion = fields.Text(string='Descripción de la tarea')
    state = fields.Selection([
        ('pendiente', 'Pendiente'),
        ('en_progreso', 'En progreso'),
        ('completada', 'Completada'),
    ], string='Estado', default='pendiente')

    @api.depends('empleado_id', 'fecha', 'turno')
    def _compute_name(self):
        for rec in self:
            if rec.empleado_id and rec.fecha:
                rec.name = f"{rec.empleado_id.name} - {rec.fecha} ({dict(rec._fields['turno'].selection).get(rec.turno, '')})"
            else:
                rec.name = 'Nueva asignación'

    def action_iniciar(self):
        self.state = 'en_progreso'

    def action_completar(self):
        self.state = 'completada'