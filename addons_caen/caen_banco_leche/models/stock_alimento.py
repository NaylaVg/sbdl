from odoo import api, fields, models


class StockAlimento(models.Model):
    # guardo cada entrada o salida de producto alimentario
    # me sirve para ver cuanto entro, cuanto salio y armar el resumen
    _name = 'caen.stock_alimento'
    _description = 'Stock de producto alimentario'
    _rec_name = 'alimento_id'
    _order = 'id desc'

    alimento_id = fields.Many2one('caen.alimento', string='Alimento',
                                  required=True)
    cantidad = fields.Float(string='Cantidad', required=True)
    # el tipo de movimiento me dice si suma o resta
    tipo_movimiento = fields.Selection([
        ('entrada', 'Entrada'),
        ('salida', 'Salida'),
    ], string='Tipo de movimiento', required=True, default='entrada')
    fecha = fields.Datetime(string='Fecha', default=fields.Datetime.now)
    # estos campos extra ayudan a identificar el lote y vencimiento
    lote = fields.Char(string='Lote')
    fecha_vencimiento = fields.Date(string='Fecha de vencimiento')
    origen = fields.Char(string='Origen')
    observacion = fields.Text(string='Observación')
    # guardo quien lo hizo para saber el historial
    user_id = fields.Many2one('res.users', string='Usuario',
                              default=lambda self: self.env.user, readonly=True)
