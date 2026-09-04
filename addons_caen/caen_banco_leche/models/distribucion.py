from odoo import api, fields, models
from odoo.exceptions import ValidationError


class Distribucion(models.Model):
    # registra la entrega de un frasco o biberon de leche a un paciente
    # receptor, es el ultimo paso del flujo
    _name = 'caen.distribucion'
    _description = 'Registro de distribución de leche a paciente'
    _rec_name = 'name'
    _order = 'distribution_date desc, id desc'

    # referencia autogenerada (DIS-0001)
    name = fields.Char(string='Referencia', readonly=True, copy=False)
    patient_id = fields.Many2one('caen.paciente', string='Paciente receptor', required=True)
    # el frasco entregado, tiene que estar en estado entregado (lo valido abajo)
    frasco_id = fields.Many2one('caen.frasco', string='Frasco / Biberón entregado', required=True)
    distribution_date = fields.Datetime(
        string='Fecha y hora de distribución', required=True,
        default=lambda self: fields.Datetime.now())
    state = fields.Selection([
        ('draft', 'Borrador'),
        ('done', 'Confirmada'),
    ], string='Estado', default='draft')
    # campos que copio del frasco para que la distribucion quede con
    # la info completa aunque despues el frasco cambie
    volume_ml = fields.Integer(
        string='Volumen entregado (ml)',
        related='frasco_id.volume_ml', readonly=True)
    milk_stage = fields.Selection([
        ('colostrum', 'Calostro'),
        ('transition', 'Transición'),
        ('mature_low', 'Madura baja'),
        ('mature_high', 'Madura alta'),
    ], string='Etapa de la leche', related='frasco_id.milk_stage', readonly=True)
    target = fields.Selection([
        ('preterm', 'Prematuro'),
        ('term', 'Término'),
    ], string='Destino', related='frasco_id.target', readonly=True)
    staff_id = fields.Many2one('hr.employee', string='Responsable')
    notes = fields.Text(string='Notas')

    # regla de negocio: solo se puede distribuir un frasco que ya fue
    # entregado (debe completarse el flujo pasteurizar -> fraccionar ->
    # entregar antes)
    @api.constrains('frasco_id')
    def _check_frasco_entregado(self):
        for rec in self:
            if rec.frasco_id.state != 'delivered':
                raise ValidationError(
                    'Solo se pueden registrar distribuciones de frascos en estado "Entregado".\n'
                    'Complete el flujo del frasco (Pasteurizar -> Fraccionar -> Entregar) primero.')

    # genero la referencia secuencial
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('name'):
                seq = int(self.env['ir.sequence'].next_by_code('caen.distribucion') or '1')
                vals['name'] = f'DIS-{seq:0>4d}'
        return super().create(vals_list)

    # boton confirmar, cierra la distribucion y lo anota en la bitacora
    def action_confirmar(self):
        for rec in self:
            rec.state = 'done'
            rec._bitacora('stage', f'Distribución confirmada: {rec.frasco_id.name} -> {rec.patient_id.name}')
        return True

    def _bitacora(self, action_type, changes):
        self.env['caen.bitacora']._registrar(
            'caen.distribucion', self.id, self.name, action_type, changes)
