from odoo import models, fields, api


class DashboardCaen(models.Model):
    _name = 'caen.dashboard'
    _description = 'Dashboard del Banco de Leche'
    _rec_name = 'name'

    name = fields.Char(string='Nombre', default='Dashboard CAEN')
    donantes_activas = fields.Integer(string='Donantes Activas', compute='_compute_stats')
    serologias_pendientes = fields.Integer(string='Serologías Pendientes', compute='_compute_stats')
    frascos_crudos = fields.Integer(string='Frascos Crudos', compute='_compute_stats')
    frascos_pasteurizados = fields.Integer(string='Frascos Pasteurizados', compute='_compute_stats')
    biberones_generados = fields.Integer(string='Biberones Generados', compute='_compute_stats')
    pacientes_activos = fields.Integer(string='Pacientes Activos', compute='_compute_stats')
    consentimientos_activos = fields.Integer(string='Consentimientos Activos', compute='_compute_stats')
    alertas_activas = fields.Integer(string='Alertas Activas', compute='_compute_stats')

    @api.depends()
    def _compute_stats(self):
        for rec in self:
            rec.donantes_activas = self.env['caen.donante'].search_count([('state', '=', 'active')])
            rec.serologias_pendientes = self.env['caen.serologia'].search_count([('result', '=', 'pending')])
            rec.frascos_crudos = self.env['caen.frasco'].search_count([('state', '=', 'raw')])
            rec.frascos_pasteurizados = self.env['caen.frasco'].search_count([('state', '=', 'pasteurized')])
            rec.biberones_generados = self.env['caen.frasco'].search_count([('state', '=', 'delivered')])
            rec.pacientes_activos = self.env['caen.paciente'].search_count([])
            rec.consentimientos_activos = self.env['caen.consentimiento'].search_count([('state', '=', 'active')])
            rec.alertas_activas = self.env['caen.alerta'].search_count([('state', '=', 'active')])

    def action_donantes(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Donantes Activas',
            'res_model': 'caen.donante',
            'domain': [('state', '=', 'active')],
            'view_mode': 'list,form',
            'target': 'current',
        }

    def action_serologias_pendientes(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Serologías Pendientes',
            'res_model': 'caen.serologia',
            'domain': [('result', '=', 'pending')],
            'view_mode': 'list,form',
            'target': 'current',
        }

    def action_frascos_crudos(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Frascos Crudos',
            'res_model': 'caen.frasco',
            'domain': [('state', '=', 'raw')],
            'view_mode': 'list,form',
            'target': 'current',
        }

    def action_pasteurizaciones(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Pasteurizaciones',
            'res_model': 'caen.pasteurizacion',
            'view_mode': 'list,form',
            'target': 'current',
        }

    def action_biberones(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Biberones Generados',
            'res_model': 'caen.biberon',
            'view_mode': 'list,form',
            'target': 'current',
        }

    def action_pacientes(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Pacientes',
            'res_model': 'caen.paciente',
            'view_mode': 'list,form',
            'target': 'current',
        }

    def action_consentimientos(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Consentimientos Activos',
            'res_model': 'caen.consentimiento',
            'domain': [('state', '=', 'active')],
            'view_mode': 'list,form',
            'target': 'current',
        }

    def action_alertas(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Alertas Activas',
            'res_model': 'caen.alerta',
            'domain': [('state', '=', 'active')],
            'view_mode': 'list,form',
            'target': 'current',
        }

    def action_generar_alertas(self):
        self.env['caen.alerta'].generar_alertas()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Alertas',
            'res_model': 'caen.alerta',
            'domain': [('state', '=', 'active')],
            'view_mode': 'list,form',
            'target': 'current',
        }
