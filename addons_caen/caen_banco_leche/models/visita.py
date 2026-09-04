from odoo import api, fields, models
from odoo.exceptions import ValidationError


class Visita(models.Model):
    _name = 'caen.visita'
    _description = 'Visita de donación'
    _rec_name = 'name'
    _order = 'visit_date desc'

    name = fields.Char(string='Referencia', readonly=True, copy=False)
    donor_id = fields.Many2one('caen.donante', string='Donante', required=True)
    center_id = fields.Many2one('res.partner', string='Centro de recolección')
    visit_date = fields.Datetime(
        string='Fecha y hora de la visita', required=True,
        default=lambda self: fields.Datetime.now())
    state = fields.Selection([
        ('scheduled', 'Programada'),
        ('in_progress', 'En curso'),
        ('done', 'Completada'),
        ('cancelled', 'Cancelada'),
    ], string='Estado', default='scheduled')

    batch_ids = fields.One2many('caen.frasco', 'visit_id', string='Frascos donados')
    n_frascos = fields.Integer(string='Cantidad de frascos', compute='_compute_n_frascos')
    volumen_total_ml = fields.Integer(
        string='Volumen total (ml)', compute='_compute_n_frascos')
    apta_donar = fields.Boolean(string='Donante apta', related='donor_id.apta_donar')
    observations = fields.Text(string='Observaciones')

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('name'):
                seq = int(self.env['ir.sequence'].next_by_code('caen.visita') or '1')
                vals['name'] = f'VIS-{seq:0>4d}'
        return super().create(vals_list)

    @api.depends('batch_ids', 'batch_ids.volume_ml')
    def _compute_n_frascos(self):
        for rec in self:
            rec.n_frascos = len(rec.batch_ids)
            rec.volumen_total_ml = sum(rec.batch_ids.mapped('volume_ml'))

    def action_marcar_en_curso(self):
        for rec in self:
            if rec.state == 'scheduled':
                rec.state = 'in_progress'
                rec._bitacora('stage', f'Visita {rec.name} marcada en curso.')
        return True

    def action_marcar_completada(self):
        for rec in self:
            if rec.state in ('scheduled', 'in_progress'):
                rec.state = 'done'
                rec._bitacora('stage', f'Visita {rec.name} completada ({rec.n_frascos} frascos, {rec.volumen_total_ml}ml).')
        return True

    def action_cancelar(self):
        for rec in self:
            if rec.state != 'done':
                rec.state = 'cancelled'
                rec._bitacora('stage', f'Visita {rec.name} cancelada.')
        return True

    def _bitacora(self, action_type, changes):
        self.env['caen.bitacora']._registrar(
            'caen.visita', self.id, self.name, action_type, changes)

    def action_agregar_frasco(self):
        """Crea un frasco en estado crudo vinculado a esta visita."""
        self.ensure_one()
        if self.state == 'cancelled':
            raise ValidationError('No se pueden agregar frascos a una visita cancelada.')
        return {
            'name': 'Nuevo Frasco',
            'type': 'ir.actions.act_window',
            'res_model': 'caen.frasco',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_donor_id': self.donor_id.id,
                'default_center_id': self.center_id.id if self.center_id else False,
                'default_visit_id': self.id,
                'default_extraction_date': self.visit_date,
                'default_state': 'raw',
            },
        }
