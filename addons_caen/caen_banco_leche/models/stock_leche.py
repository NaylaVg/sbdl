from odoo import fields, models, tools


class StockLeche(models.Model):
    # vista resumen que muestra todo el stock actual de leche y biberones
    # agrupado por producto, etapa de leche, destino y ubicacion
    # no crea tabla, es una consulta sql sobre stock_quant + caen_frasco
    _name = 'caen.stock_leche'
    _description = 'Resumen de stock de leche'
    _auto = False
    _order = 'product_id, location_id'

    product_id = fields.Many2one('product.product', string='Producto', readonly=True)
    milk_stage = fields.Selection([
        ('colostrum', 'Calostro'),
        ('transition', 'Transición'),
        ('mature_low', 'Madura baja'),
        ('mature_high', 'Madura alta'),
    ], string='Etapa de la leche', readonly=True)
    target = fields.Selection([
        ('preterm', 'Prematuro'),
        ('term', 'Término'),
    ], string='Destino', readonly=True)
    location_id = fields.Many2one('stock.location', string='Ubicación', readonly=True)
    lot_id = fields.Many2one('stock.lot', string='Lote/QR', readonly=True)
    quantity = fields.Float(string='Cantidad (L)', readonly=True)
    product_uom_id = fields.Many2one('uom.uom', string='Unidad', readonly=True)

    def init(self):
        # busco el id de la ubicacion raiz del banco de leche para filtrar
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute("""
            CREATE OR REPLACE VIEW %s AS (
                SELECT
                    row_number() OVER () as id,
                    pp.id as product_id,
                    COALESCE(f.milk_stage, NULL) as milk_stage,
                    COALESCE(f.target, NULL) as target,
                    sq.location_id,
                    sq.lot_id,
                    ROUND(SUM(sq.quantity)::numeric, 2) as quantity,
                    pt.uom_id as product_uom_id
                FROM stock_quant sq
                JOIN product_product pp ON sq.product_id = pp.id
                JOIN product_template pt ON pp.product_tmpl_id = pt.id
                JOIN stock_lot sl ON sq.lot_id = sl.id
                LEFT JOIN caen_frasco f ON f.name = sl.name
                WHERE sq.location_id IN (
                    SELECT id FROM stock_location
                    WHERE parent_path LIKE '%%/%%/'
                      AND id != 1
                )
                AND sq.quantity > 0
                AND pt.categ_id = (
                    SELECT id FROM product_category
                    WHERE name = 'Leche Humana' LIMIT 1
                )
                GROUP BY pp.id, f.milk_stage, f.target, sq.location_id,
                         sq.lot_id, pt.uom_id
            )
        """ % self._table)
