from odoo import api, fields, models, tools


class StockAlimentoResumen(models.Model):
    # esto no es una tabla real, es una vista de odoo
    # aca calculo el stock actual sumando entradas y restando salidas
    _name = 'caen.stock_alimento_resumen'
    _description = 'Resumen de stock de producto alimentario'
    _auto = False
    _rec_name = 'alimento_id'

    alimento_id = fields.Many2one('caen.alimento', string='Alimento')
    cantidad_actual = fields.Float(string='Cantidad actual')
    tipo_alimento = fields.Selection(related='alimento_id.tipo', store=True)

    def init(self):
        # creo la vista sql con el calculo de stock actual
        # traigo el tipo desde caen_alimento porque el campo es related con store true y si no la columna no existe y rompe la lista
        # hago drop antes porque postgres no me deja agregar columnas en el medio con or replace
        tools.drop_view_if_exists(self._cr, 'caen_stock_alimento_resumen')
        self._cr.execute("""
            CREATE OR REPLACE VIEW caen_stock_alimento_resumen AS (
                SELECT
                    min(m.id) AS id,
                    m.alimento_id AS alimento_id,
                    a.tipo AS tipo_alimento,
                    COALESCE(SUM(CASE WHEN m.tipo_movimiento = 'entrada' THEN m.cantidad ELSE -m.cantidad END), 0) AS cantidad_actual
                FROM caen_stock_alimento m
                LEFT JOIN caen_alimento a ON a.id = m.alimento_id
                GROUP BY m.alimento_id, a.tipo
            )
        """)
