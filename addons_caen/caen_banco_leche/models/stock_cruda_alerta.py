from odoo import fields, models, tools


class StockCrudaAlerta(models.Model):
    # leche cruda que lleva dias en recepcion sin pasteurizar
    # sirve para saber que leche hay que pasteurizar pronto
    _name = 'caen.stock_cruda_alerta'
    _description = 'Leche cruda por antiguedad (para pasteurizar)'
    _auto = False
    _rec_name = 'name'
    _order = 'dias_antiguedad desc'

    name = fields.Char(string='Frasco', readonly=True)
    donor_id = fields.Many2one('caen.donante', string='Donante', readonly=True)
    donor_name = fields.Char(string='Donante', readonly=True)
    volume_ml = fields.Float(string='Volumen (ml)', readonly=True)
    extraction_date = fields.Datetime(string='Fecha extracción', readonly=True)
    dias_antiguedad = fields.Integer(string='Días de antigüedad', readonly=True)
    lot_id = fields.Many2one('stock.lot', string='Lote/QR', readonly=True)

    def init(self):
        tools.drop_view_if_exists(self._cr, 'caen_stock_cruda_alerta')
        self._cr.execute("""
            CREATE OR REPLACE VIEW caen_stock_cruda_alerta AS (
                SELECT
                    f.id AS id,
                    f.name AS name,
                    f.donor_id AS donor_id,
                    d.name AS donor_name,
                    f.volume_ml AS volume_ml,
                    f.extraction_date AS extraction_date,
                    (CURRENT_DATE - f.extraction_date::date) AS dias_antiguedad,
                    f.lot_id AS lot_id
                FROM caen_frasco f
                JOIN caen_donante d ON d.id = f.donor_id
                WHERE f.state = 'raw'
            )
        """)
