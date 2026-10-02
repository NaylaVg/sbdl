from odoo import api, fields, models


class Alimento(models.Model):
    # definicion del catalogo de alimentos, leches y formulas que usamos
    # aqui guardo el nombre, el tipo y todos los nutrientes por 100 ml
    _name = 'caen.alimento'
    _description = 'Alimento / Leche / Formula'
    _rec_name = 'name'

    name = fields.Char(string='Nombre', required=True)
    # el tipo me sirve para filtrar despues y saber si es leche, formula o fortificador
    tipo = fields.Selection([
        ('lh_madura', 'Leche humana madura'),
        ('lh_transicion', 'Leche humana de transición'),
        ('calostro', 'Calostro'),
        ('formula_iniciacion', 'Fórmula de iniciación'),
        ('formula_pretermino', 'Fórmula para pretérmino'),
        ('formula_pm', 'Fórmula PM (post-termino)'),
        ('fortificador', 'Fortificador'),
        ('suplemento', 'Suplemento proteico'),
        ('otro', 'Otro'),
    ], string='Tipo', required=True)

    # estos valores son la composicion por cada 100 ml, salen de la planilla 15
    kcal = fields.Float(string='Kcal')
    hc_g = fields.Float(string='Hidratos de carbono (g)')
    protein_g = fields.Float(string='Proteínas (g)')
    fat_g = fields.Float(string='Grasas (g)')
    calcium_mg = fields.Float(string='Calcio (mg)')
    iron_mg = fields.Float(string='Hierro (mg)')
    phosphorus_mg = fields.Float(string='Fósforo (mg)')
    sodium_mg = fields.Float(string='Sodio (mg)')
    zinc_mg = fields.Float(string='Zinc (mg)')
    vit_c_mg = fields.Float(string='Vitamina C (mg)')
    vit_d_mcg = fields.Float(string='Vitamina D (mcg)')
    vit_a_mcg = fields.Float(string='Vitamina A (mcg)')

    # marcas de formula que se pueden anotar si hace falta
    brand = fields.Char(string='Marca / Fabricante')
    active = fields.Boolean(string='Activo', default=True)
