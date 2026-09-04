from odoo import api, fields, models
from odoo.exceptions import ValidationError


class Bitacora(models.Model):
    # historial inmutable de los cambios importantes del sistema
    # sirve de auditoria, no se puede modificar ni borrar
    _name = 'caen.bitacora'
    _description = 'Bitácora de cambios del sistema CAEN'
    _rec_name = 'record_name'
    _order = 'create_date desc'

    # a que modelo y registro se refiere el cambio
    record_model = fields.Char(string='Modelo', required=True)
    record_id = fields.Integer(string='ID del registro')
    record_name = fields.Char(string='Registro')
    # que tipo de accion fue
    action_type = fields.Selection([
        ('create', 'Creación'),
        ('write', 'Modificación'),
        ('unlink', 'Eliminación'),
        ('stage', 'Cambio de etapa'),
        ('stock', 'Movimiento de stock'),
    ], string='Tipo de acción', required=True)
    # quien lo hizo y cuando
    user_id = fields.Many2one('res.users', string='Usuario', default=lambda self: self.env.user)
    create_date = fields.Datetime(string='Fecha', default=lambda self: fields.Datetime.now())
    changes = fields.Text(string='Detalle de los cambios')

    # hago la bitacora inmutable tirando excepcion en borrar y modificar
    def unlink(self):
        raise ValidationError('La bitácora es inmutable: no se pueden eliminar registros de auditoría.')

    def write(self, vals):
        raise ValidationError('La bitácora es inmutable: no se pueden modificar registros de auditoría.')

    # metodo que usan los otros modelos para anotar un evento, uso sudo
    # porque la bitacora es solo lectura para el usuario comun
    @api.model
    def _registrar(self, record_model, record_id, record_name, action_type, changes=None):
        self.sudo().create({
            'record_model': record_model,
            'record_id': record_id,
            'record_name': record_name,
            'action_type': action_type,
            'changes': changes,
        })
        return True

    # wrapper publico para poder llamar desde afuera (los metodos con
    # guion bajo no se pueden invocar por xmlrpc)
    def registrar(self, record_model, record_id, record_name, action_type, changes=None):
        return self._registrar(record_model, record_id, record_name, action_type, changes)
