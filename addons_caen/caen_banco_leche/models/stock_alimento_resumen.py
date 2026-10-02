from odoo import api, fields, models


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
        self._cr.execute("""
            CREATE OR REPLACE VIEW caen_stock_alimento_resumen AS (
                SELECT
                    min(m.id) AS id,
                    m.alimento_id AS alimento_id,
                    COALESCE(SUM(CASE WHEN m.tipo_movimiento = 'entrada' THEN m.cantidad ELSE -m.cantidad END), 0) AS cantidad_actual
                FROM caen_stock_alimento m
                GROUP BY m.alimento_id
            )
        """)
