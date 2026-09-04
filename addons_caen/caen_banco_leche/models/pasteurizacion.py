from odoo import api, fields, models


class Pasteurizacion(models.Model):
    _name = 'caen.pasteurizacion'
    _description = 'Registro de pasteurización y control de calidad'

    batch_id = fields.Many2one('caen.frasco', string='Frasco de origen',
                               required=True)
    new_barcode = fields.Char(string='QR post-pasteurización', index=True)
    method = fields.Selection([
        ('holder', 'Holder (62.5°C)'),
        ('flash', 'Flash (72°C)'),
    ], string='Método')
    ac_dornic = fields.Float(string='Acidez Dornic (°D)')
    cream_percentage = fields.Float(string='% crema')
    fat_percentage = fields.Float(string='% grasa')
    kcal_per_liter = fields.Float(string='Kcal/litro')
    culture_24h = fields.Selection([
        ('pending', 'Pendiente'),
        ('ok', 'Negativo'),
        ('positive', 'Positivo'),
    ], string='Cultivo 24h', default='pending')
    culture_48h = fields.Selection([
        ('pending', 'Pendiente'),
        ('ok', 'Negativo'),
        ('positive', 'Positivo'),
    ], string='Cultivo 48h', default='pending')
    volume_before = fields.Integer(string='Volumen antes (ml)')
    volume_after = fields.Integer(string='Volumen después (ml)')
    discard_volume = fields.Integer(string='Volumen descartado (ml)')
    processed_by = fields.Many2one('res.users', string='Responsable')
    processed_at = fields.Datetime(string='Fecha de procesamiento')
