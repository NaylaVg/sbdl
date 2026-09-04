from odoo import api, fields, models
from odoo.exceptions import ValidationError


class Bitacora(models.Model):
    _name = 'caen.bitacora'
    _description = 'Bitácora de cambios del sistema CAEN'
    _rec_name = 'record_name'
    _order = 'create_date desc'

    record_model = fields.Char(string='Modelo', required=True)
    record_id = fields.Integer(string='ID del registro')
    record_name = fields.Char(string='Registro')
    action_type = fields.Selection([
        ('create', 'Creación'),
        ('write', 'Modificación'),
        ('unlink', 'Eliminación'),
        ('stage', 'Cambio de etapa'),
        ('stock', 'Movimiento de stock'),
    ], string='Tipo de acción', required=True)
    user_id = fields.Many2one('res.users', string='Usuario', default=lambda self: self.env.user)
    create_date = fields.Datetime(string='Fecha', default=lambda self: fields.Datetime.now())
    changes = fields.Text(string='Detalle de los cambios')

    def unlink(self):
        raise ValidationError('La bitácora es inmutable: no se pueden eliminar registros de auditoría.')

    def write(self, vals):
        raise ValidationError('La bitácora es inmutable: no se pueden modificar registros de auditoría.')

    @api.model
    def _registrar(self, record_model, record_id, record_name, action_type, changes=None):
        """Registra un evento en la bitácora."""
        self.sudo().create({
            'record_model': record_model,
            'record_id': record_id,
            'record_name': record_name,
            'action_type': action_type,
            'changes': changes,
        })
        return True

    def registrar(self, record_model, record_id, record_name, action_type, changes=None):
        """Método público para registrar un evento (wrapper de _registrar)."""
        return self._registrar(record_model, record_id, record_name, action_type, changes)
