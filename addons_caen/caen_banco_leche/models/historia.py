from odoo import fields, models


class HistoriaPerinatal(models.Model):
    # historia obstetrica de la madre donante, punto 8 del programa
    # una ficha por madre con resumen de embarazos y partos
    # mas una linea por cada bebe con sus datos de nacimiento
    _name = 'caen.historia_perinatal'
    _description = 'Historia perinatal de la madre'
    _rec_name = 'donor_id'

    donor_id = fields.Many2one('caen.donante', string='Madre donante',
                               required=True, ondelete='restrict')
    fecha = fields.Date(string='Fecha de registro',
                        default=fields.Date.context_today)
    # resumen obstetrico, lo completa el personal con la entrevista
    n_embarazos = fields.Integer(string='Embarazos')
    n_partos = fields.Integer(string='Partos vaginales')
    n_cesareas = fields.Integer(string='Cesáreas')
    n_abortos = fields.Integer(string='Abortos')
    controles = fields.Integer(string='Controles prenatales')
    patologia = fields.Selection([
        ('ninguna', 'Ninguna'),
        ('hta', 'Hipertensión'),
        ('diabetes', 'Diabetes'),
        ('anemia', 'Anemia'),
        ('itu', 'Infección urinaria'),
        ('otra', 'Otra'),
    ], string='Patología del embarazo', default='ninguna')
    observaciones = fields.Text(string='Observaciones')
    # un bebe por linea, aca van semanas peso y fecha de cada hijo
    bebe_ids = fields.One2many('caen.historia_bebe', 'historia_id',
                               string='Bebés')


class HistoriaBebe(models.Model):
    # cada hijo de la madre con sus datos de nacimiento
    # sirve para ver semanas y peso sin abrir otra ficha
    _name = 'caen.historia_bebe'
    _description = 'Bebé de historia perinatal'
    _rec_name = 'historia_id'

    historia_id = fields.Many2one('caen.historia_perinatal',
                                  string='Historia', required=True,
                                  ondelete='cascade')
    donor_id = fields.Many2one('caen.donante', string='Madre',
                               related='historia_id.donor_id', store=True,
                               readonly=True)
    fecha_nac = fields.Date(string='Fecha de nacimiento')
    semanas = fields.Float(string='Semanas de gestación')
    peso_g = fields.Integer(string='Peso al nacer (g)')
    orden = fields.Integer(string='Orden de nacimiento', default=1)
    observaciones = fields.Text(string='Observaciones')
