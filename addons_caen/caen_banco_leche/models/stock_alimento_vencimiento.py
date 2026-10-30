from odoo import fields, models, tools


class StockAlimentoVencimiento(models.Model):
    # vista SQL sin tabla (sql view) sobre stock_alimento agrupado por lote
    # sirve para ver qué fórmulas/suplementos quedan en stock y cuánto les falta para vencer
    _name = 'caen.stock_alimento_vencimiento'
    _description = 'Alimentos por vencer (FEFO)'
    _auto = False
    _rec_name = 'alimento_id'
    _order = 'fecha_vencimiento asc, lote asc'

    alimento_id = fields.Many2one('caen.alimento', string='Alimento', readonly=True)
    alimento_nombre = fields.Char(string='Alimento', readonly=True)
    lote = fields.Char(string='Lote', readonly=True)
    fecha_vencimiento = fields.Date(string='Fecha de vencimiento', readonly=True)
    stock_actual = fields.Float(string='Stock actual (ml)', readonly=True)
    dias_para_vencer = fields.Integer(string='Días para vencer', readonly=True)

    def init(self):
        tools.drop_view_if_exists(self._cr, 'caen_stock_alimento_vencimiento')
        self._cr.execute("""
            CREATE OR REPLACE VIEW caen_stock_alimento_vencimiento AS (
                SELECT
                    min(sa.id) AS id,
                    sa.alimento_id AS alimento_id,
                    a.name AS alimento_nombre,
                    sa.lote AS lote,
                    sa.fecha_vencimiento AS fecha_vencimiento,
                    COALESCE(SUM(CASE WHEN sa.tipo_movimiento = 'entrada' THEN sa.cantidad ELSE -sa.cantidad END), 0) AS stock_actual,
                    (sa.fecha_vencimiento::date - CURRENT_DATE) AS dias_para_vencer
                FROM caen_stock_alimento sa
                JOIN caen_alimento a ON a.id = sa.alimento_id
                WHERE sa.fecha_vencimiento IS NOT NULL
                GROUP BY sa.alimento_id, a.name, sa.lote, sa.fecha_vencimiento
                HAVING COALESCE(SUM(CASE WHEN sa.tipo_movimiento = 'entrada' THEN sa.cantidad ELSE -sa.cantidad END), 0) > 0
                ORDER BY sa.fecha_vencimiento ASC, sa.lote ASC
            )
        """)
