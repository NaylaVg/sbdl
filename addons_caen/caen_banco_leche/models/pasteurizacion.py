from odoo import api, fields, models
from .qr_utils import generar_qr_imagen, construir_url_registro


class Pasteurizacion(models.Model):
    # registro del proceso de pasteurizacion y los controles de calidad
    # que se le hacen a un frasco
    _name = 'caen.pasteurizacion'
    _description = 'Registro de pasteurización y control de calidad'

    batch_id = fields.Many2one('caen.frasco', string='Frasco de origen',
                               required=True)
    # nuevo qr que se le asigna al frasco cuando se pasteuriza
    # se genera automaticamente al crear el registro
    new_barcode = fields.Char(string='QR post-pasteurización', index=True)
    # imagen del qr post-pasteurizacion
    qr_image = fields.Binary('Imagen QR', attachment=True, readonly=True)
    # metodo de pasteurizacion usado
    method = fields.Selection([
        ('holder', 'Holder (62.5°C)'),
        ('flash', 'Flash (72°C)'),
    ], string='Método')
    # controles de calidad del producto
    ac_dornic = fields.Float(string='Acidez Dornic (°D)')
    cream_percentage = fields.Float(string='% crema')
    fat_percentage = fields.Float(string='% grasa')
    kcal_per_liter = fields.Float(string='Kcal/litro')
    # resultado de los cultivos a las 24 y 48 horas
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
    # volumenes antes y despues del proceso, y cuanto se descarto
    volume_before = fields.Integer(string='Volumen antes (ml)')
    volume_after = fields.Integer(string='Volumen después (ml)')
    discard_volume = fields.Integer(string='Volumen descartado (ml)')
    processed_by = fields.Many2one('res.users', string='Responsable')
    processed_at = fields.Datetime(string='Fecha de procesamiento')

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            # si no se provio un barcode, lo genero a partir del frasco
            if not vals.get('new_barcode'):
                batch = self.env['caen.frasco'].browse(vals.get('batch_id'))
                if batch.exists():
                    vals['new_barcode'] = f"{batch.name}-P"
        registros = super().create(vals_list)
        # genero la imagen qr para cada registro nuevo
        for reg in registros:
            if reg.id:
                url = construir_url_registro(
                    self.env, 'caen.pasteurizacion', reg.id)
                if url:
                    imagen = generar_qr_imagen(url)
                    if imagen:
                        reg.qr_image = imagen
        return registros

    def action_generar_qr(self):
        """Regenera la imagen QR desde la URL del registro."""
        for reg in self:
            if reg.id:
                url = construir_url_registro(
                    self.env, 'caen.pasteurizacion', reg.id)
                if url:
                    imagen = generar_qr_imagen(url)
                    if imagen:
                        reg.qr_image = imagen
