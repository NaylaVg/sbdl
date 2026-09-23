from odoo import fields, models, tools


class Rendimiento(models.Model):
    # vista que muestra el rendimiento del banco: leche recibida,
    # procesada y descartada por cada frasco
    # NO crea tabla, es una consulta SQL sobre frascos + pasteurizaciones
    _name = 'caen.rendimiento'
    _description = 'Rendimiento del Banco de Leche'
    _auto = False
    _order = 'extraction_date desc'

    donor_id = fields.Many2one('caen.donante', string='Donante', readonly=True)
    center_id = fields.Many2one('res.partner', string='Centro', readonly=True)
    extraction_date = fields.Date(string='Fecha de extracción', readonly=True)
    pasteurization_date = fields.Date(string='Fecha de pasteurización', readonly=True)
    milk_stage = fields.Selection([
        ('colostrum', 'Calostro'),
        ('transition', 'Transición'),
        ('mature_low', 'Madura baja'),
        ('mature_high', 'Madura alta'),
    ], string='Etapa', readonly=True)
    target = fields.Selection([
        ('preterm', 'Prematuro'),
        ('term', 'Término'),
    ], string='Destino', readonly=True)
    state = fields.Selection([
        ('raw', 'Crudo'),
        ('pasteurized', 'Pasteurizado'),
        ('fractioned', 'Fraccionado'),
        ('delivered', 'Entregado'),
        ('discarded', 'Descartado'),
    ], string='Estado del frasco', readonly=True)
    volume_received = fields.Float(
        string='Recibido (ml)', readonly=True,
        group_operator='sum')
    volume_pasteurized = fields.Float(
        string='Procesado (ml)', readonly=True,
        group_operator='sum')
    volume_discarded = fields.Float(
        string='Descartado (ml)', readonly=True,
        group_operator='sum')
    volume_delivered = fields.Float(
        string='Entregado (ml)', readonly=True,
        group_operator='sum')
    pasteurization_method = fields.Selection([
        ('holder', 'Holder (62.5°C)'),
        ('flash', 'Flash (72°C)'),
    ], string='Método pasteurización', readonly=True)
    culture_result = fields.Selection([
        ('pending', 'Pendiente'),
        ('ok', 'Negativo'),
        ('positive', 'Positivo'),
    ], string='Cultivo final', readonly=True)
    kcal_per_liter = fields.Float(string='Kcal/l', readonly=True)

    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute("""
            CREATE OR REPLACE VIEW %s AS (
                SELECT
                    ROW_NUMBER() OVER () AS id,
                    f.donor_id,
                    f.center_id,
                    DATE(f.extraction_date) AS extraction_date,
                    DATE(p.processed_at) AS pasteurization_date,
                    f.milk_stage,
                    f.target,
                    f.state,
                    COALESCE(f.volume_ml, 0) AS volume_received,
                    COALESCE(p.volume_after, 0) AS volume_pasteurized,
                    CASE
                        WHEN f.state = 'discarded' THEN COALESCE(f.volume_ml, 0)
                        ELSE COALESCE(p.discard_volume, 0)
                    END AS volume_discarded,
                    CASE
                        WHEN f.state = 'delivered' THEN COALESCE(f.volume_ml, 0)
                        ELSE 0
                    END AS volume_delivered,
                    p.method AS pasteurization_method,
                    CASE
                        WHEN p.culture_48h != 'pending' THEN p.culture_48h
                        WHEN p.culture_24h != 'pending' THEN p.culture_24h
                        ELSE 'pending'
                    END AS culture_result,
                    COALESCE(p.kcal_per_liter, 0) AS kcal_per_liter
                FROM caen_frasco f
                LEFT JOIN caen_pasteurizacion p ON p.batch_id = f.id
            )
        """ % self._table)
