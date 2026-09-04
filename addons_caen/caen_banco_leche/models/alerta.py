from odoo import api, fields, models


class Alerta(models.Model):
    # alertas que genera el sistema de forma automatica con un cron diario
    # para avisar de pendientes, vencimientos y stock bajo
    _name = 'caen.alerta'
    _description = 'Alerta del sistema CAEN'
    _rec_name = 'description'
    _order = 'create_date desc'

    # tipo de alerta
    alert_type = fields.Selection([
        ('serologia_pendiente', 'Serología Pendiente'),
        ('serologia_vencida', 'Serología Vencida'),
        ('consentimiento_por_vencer', 'Consentimiento por Vencer'),
        ('consentimiento_vencido', 'Consentimiento Vencido'),
        ('stock_bajo', 'Stock Bajo'),
    ], string='Tipo', required=True, index=True)

    # que tan urgente es
    severity = fields.Selection([
        ('info', 'Informativa'),
        ('warning', 'Advertencia'),
        ('critical', 'Crítica'),
    ], string='Severidad', default='warning', required=True)

    # a que registro esta vinculada (puede ser de varios modelos)
    donor_id = fields.Many2one('caen.donante', string='Donante')
    related_model = fields.Char(string='Modelo relacionado')
    related_id = fields.Integer(string='ID relacionado')
    description = fields.Text(string='Descripción', required=True)
    # ciclo de vida de la alerta
    state = fields.Selection([
        ('active', 'Activa'),
        ('acknowledged', 'Reconocida'),
        ('resolved', 'Resuelta'),
    ], string='Estado', default='active', index=True)

    # metodo que ejecuta el cron, primero limpia las activas y las vuelve
    # a generar segun el estado actual de los datos
    @api.model
    def _cron_generar_alertas(self):
        Alerta = self.env['caen.alerta']
        today = fields.Date.context_today(self)

        # las alertas activas viejas las cierro para regenerarlas
        old = Alerta.search([('state', '=', 'active')])
        old.write({'state': 'resolved'})

        # 1 serologias pendientes: aviso cuando no tiene resultado
        serologias = self.env['caen.serologia'].search([('result', '=', 'pending')])
        for s in serologias:
            Alerta.create({
                'alert_type': 'serologia_pendiente',
                'severity': 'warning',
                'donor_id': s.donor_id.id,
                'related_model': 'caen.serologia',
                'related_id': s.id,
                'description': f'Serología {s.study_type} de {s.donor_id.name} sigue pendiente de resultado.',
            })

        # 2 consentimientos por vencer: los que vencen dentro de 30 dias
        from datetime import timedelta
        limit_date = today + timedelta(days=30)
        por_vencer = self.env['caen.consentimiento'].search([
            ('state', '=', 'active'),
            ('end_date', '>=', today),
            ('end_date', '<=', limit_date),
        ])
        for c in por_vencer:
            dias = (c.end_date - today).days
            Alerta.create({
                'alert_type': 'consentimiento_por_vencer',
                'severity': 'critical' if dias <= 7 else 'warning',
                'donor_id': c.donor_id.id,
                'related_model': 'caen.consentimiento',
                'related_id': c.id,
                'description': f'Consentimiento de {c.donor_id.name} vence en {dias} días ({c.end_date}).',
            })

        # 3 consentimientos vencidos: los paso a expirado y aviso
        vencidos = self.env['caen.consentimiento'].search([
            ('state', '=', 'active'),
            ('end_date', '<', today),
        ])
        for c in vencidos:
            c.write({'state': 'expired'})
            Alerta.create({
                'alert_type': 'consentimiento_vencido',
                'severity': 'critical',
                'donor_id': c.donor_id.id,
                'related_model': 'caen.consentimiento',
                'related_id': c.id,
                'description': f'¡Consentimiento de {c.donor_id.name} está vencido! Se marcó como expirado.',
            })

        # 4 stock bajo: sumo la leche cruda en recepcion y aviso si falta
        location = self.env.ref('caen_banco_leche.stock_location_recepcion')
        product = self.env.ref('caen_banco_leche.product_leche_cruda').product_variant_id
        quant = self.env['stock.quant'].search([
            ('product_id', '=', product.id),
            ('location_id', '=', location.id),
        ])
        qty_total = sum(quant.mapped('quantity'))
        if qty_total <= 0:
            Alerta.create({
                'alert_type': 'stock_bajo',
                'severity': 'critical',
                'description': 'No hay leche cruda en recepción. Se necesita más donaciones.',
            })
        elif qty_total <= 0.5:
            Alerta.create({
                'alert_type': 'stock_bajo',
                'severity': 'warning',
                'description': f'Stock bajo: solo {qty_total:.1f}L de leche cruda en recepción.',
            })

        return True

    # botones para cambiar el estado de la alerta
    def action_acknowledge(self):
        for rec in self:
            rec.state = 'acknowledged'
        return True

    def action_resolve(self):
        for rec in self:
            rec.state = 'resolved'
        return True

    # wrapper publico para regenerar las alertas desde la pantalla
    def generar_alertas(self):
        return self._cron_generar_alertas()
