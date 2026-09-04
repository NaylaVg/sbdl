from odoo import api, fields, models


class Serologia(models.Model):
    # un estudio de serologia que se le hace a la donante, cada donante
    # necesita las 7 negativas (ok) para poder donar
    _name = 'caen.serologia'
    _description = 'Estudio de serología de una donante'

    donor_id = fields.Many2one('caen.donante', string='Donante',
                               required=True)
    # los 7 estudios obligatorios de un banco de leche
    study_type = fields.Selection([
        ('hiv', 'HIV'),
        ('hep_b', 'Hepatitis B'),
        ('hep_c', 'Hepatitis C'),
        ('htlv', 'HTLV'),
        ('toxo', 'Toxoplasmosis'),
        ('chagas', 'Chagas'),
        ('vdrl', 'VDRL / Sífilis'),
    ], string='Estudio', required=True)
    # resultado, arranca pendiente y lo carga el laboratorio
    result = fields.Selection([
        ('pending', 'Pendiente'),
        ('ok', 'Negativo / Apto'),
        ('positive', 'Positivo / No apto'),
    ], string='Resultado', default='pending')
    test_date = fields.Date(string='Fecha de extracción')
