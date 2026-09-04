from odoo import api, fields, models


class Serologia(models.Model):
    _name = 'caen.serologia'
    _description = 'Estudio de serología de una donante'

    donor_id = fields.Many2one('caen.donante', string='Donante',
                               required=True)
    study_type = fields.Selection([
        ('hiv', 'HIV'),
        ('hep_b', 'Hepatitis B'),
        ('hep_c', 'Hepatitis C'),
        ('htlv', 'HTLV'),
        ('toxo', 'Toxoplasmosis'),
        ('chagas', 'Chagas'),
        ('vdrl', 'VDRL / Sífilis'),
    ], string='Estudio', required=True)
    result = fields.Selection([
        ('pending', 'Pendiente'),
        ('ok', 'Negativo / Apto'),
        ('positive', 'Positivo / No apto'),
    ], string='Resultado', default='pending')
    test_date = fields.Date(string='Fecha de extracción')
