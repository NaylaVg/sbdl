from odoo import api, fields, models
from odoo.exceptions import ValidationError


class DistribucionAlimento(models.Model):
    # registro de entrega de fórmula / suplemento a un paciente receptor
    # descuenta stock de caen.stock_alimento al confirmar
    _name = 'caen.distribucion_alimento'
    _description = 'Distribución de fórmula / suplemento a paciente'
    _rec_name = 'name'
    _order = 'fecha desc, id desc'

    name = fields.Char(string='Referencia', readonly=True, copy=False)
    paciente_id = fields.Many2one('caen.paciente', string='Paciente', required=True)
    alimento_id = fields.Many2one('caen.alimento', string='Fórmula / Suplemento', required=True)
    cantidad_ml = fields.Float(string='Volumen (ml)', required=True)
    fecha = fields.Datetime(string='Fecha', default=fields.Datetime.now)
    lote = fields.Char(string='Lote')
    fecha_vencimiento = fields.Date(string='Fecha de vencimiento')
    usuario_id = fields.Many2one('res.users', string='Usuario',
                                 default=lambda self: self.env.user, readonly=True)
    observaciones = fields.Text(string='Observaciones')
    state = fields.Selection([('draft', 'Borrador'), ('done', 'Confirmada')],
                             string='Estado', default='draft')

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('name'):
                seq = self.env['ir.sequence'].next_by_code('caen.distribucion_alimento') or 'DFA0001'
                vals['name'] = seq
        registros = super().create(vals_list)
        return registros

    def action_confirmar(self):
        for rec in self:
            if rec.state != 'draft':
                continue
            # chequeo de stock disponible del alimento y lote
            movimientos = self.env['caen.stock_alimento'].search([
                ('alimento_id', '=', rec.alimento_id.id),
                ('lote', '=', rec.lote or False),
            ])
            entradas = sum(m.cantidad for m in movimientos if m.tipo_movimiento == 'entrada')
            salidas = sum(m.cantidad for m in movimientos if m.tipo_movimiento == 'salida')
            disponible = entradas - salidas
            if disponible < rec.cantidad_ml:
                raise ValidationError(
                    f'No hay stock suficiente de {rec.alimento_id.name} lote {rec.lote or "sin lote"}.\n'
                    f'Disponible: {disponible} ml, necesita: {rec.cantidad_ml} ml.')
            # creo el movimiento de salida de stock
            self.env['caen.stock_alimento'].create({
                'alimento_id': rec.alimento_id.id,
                'cantidad': rec.cantidad_ml,
                'tipo_movimiento': 'salida',
                'fecha': rec.fecha,
                'lote': rec.lote,
                'fecha_vencimiento': rec.fecha_vencimiento,
                'origen': f'Entrega a {rec.paciente_id.name}',
                'observacion': rec.observaciones,
                'usuario_id': rec.usuario_id.id,
            })
            rec.state = 'done'
            rec._bitacora('stage', f'Distribución de fórmula confirmada: {rec.alimento_id.name} {rec.cantidad_ml} ml -> {rec.paciente_id.name}')
        return True

    def _bitacora(self, action_type, changes):
        self.env['caen.bitacora']._registrar(
            'caen.distribucion_alimento', self.id, self.name, action_type, changes)
