from odoo import models, fields, api

# mapa de roles predefinidos 
ROLE_MAP = {
    'admin': 'caen_banco_leche.role_admin',
    'jefe': 'caen_banco_leche.role_jefe',
    'enfermera': 'caen_banco_leche.role_enfermera',
    'tecnico': 'caen_banco_leche.role_tecnico_lab',
    'nutricionista': 'caen_banco_leche.role_nutricionista',
    'recepcionista': 'caen_banco_leche.role_recepcionista',
}


class ResUsers(models.Model):
    _inherit = 'res.users'

    # campo de seleccion para elegir rol CAEN en el formulario de usuarios
    # incluye los 6 roles predefinidos + personalizado (sin permisos base)
    caen_role = fields.Selection(
        selection=[
            ('admin', 'CAEN Administrador'),
            ('jefe', 'CAEN Jefe'),
            ('enfermera', 'CAEN Enfermera'),
            ('tecnico', 'CAEN Tecnico de Laboratorio'),
            ('nutricionista', 'CAEN Nutricionista'),
            ('recepcionista', 'CAEN Recepcionista'),
            ('custom', 'Personalizado (elegir permisos manualmente)'),
        ],
        string='Rol CAEN',
    )

    # indica si el usuario necesita aprobacion (sin rol asignado)
    # aparece en la lista de usuarios como filtro y con color amarillo
    caen_pendiente = fields.Boolean(
        string='Pendiente de aprobación',
        compute='_compute_caen_pendiente',
        search='_search_caen_pendiente',
    )

    @api.depends('caen_role', 'share')
    def _compute_caen_pendiente(self):
        for user in self:
            user.caen_pendiente = bool(not user.caen_role)

    def _search_caen_pendiente(self, operator, value):
        if operator in ('=', '!=') and bool(value) == (operator == '='):
            return [('caen_role', '=', False)]
        return [('caen_role', '!=', False)]

    # al crear un usuario con rol, aplica los permisos del rol
    @api.model_create_multi
    def create(self, vals_list):
        users = super().create(vals_list)
        for user, vals in zip(users, vals_list):
            if vals.get('caen_role'):
                user._apply_caen_role(vals['caen_role'])
        return users

    # al cambiar el rol desde el formulario, re-sincroniza los permisos
    def write(self, vals):
        res = super().write(vals)
        if 'caen_role' in vals:
            for user in self:
                user._apply_caen_role(user.caen_role)
        return res

    # sincroniza los group_ids con el rol seleccionado
    # 1. busca todos los permisos CAEN (los que tienen privilege_id)
    # 2. los saca del usuario
    # 3. agrega los permisos del nuevo rol (si es custom no agrega nada)
    def _apply_caen_role(self, role):
        xmlid = ROLE_MAP.get(role)
        new_perms = self.env['res.groups']

        # si se asigna un rol, el usuario deja de ser portal y pasa a ser interno
        group_user = self.env.ref('base.group_user')
        group_portal = self.env.ref('base.group_portal')

        # si tiene un rol asignado (no es custom ni vacio), le damos interno y sacamos portal
        if role and role != 'custom':
            self.sudo().write({'group_ids': [(4, group_user.id), (3, group_portal.id)]})

        if xmlid:
            group = self.env.ref(xmlid, raise_if_not_found=False)
            if group:
                new_perms = group.all_implied_ids.filtered(
                    lambda g: g.privilege_id
                )

        caen_perms = self.env['res.groups'].search([
            ('privilege_id', '!=', False)
        ])
        remove_cmds = [(3, g.id) for g in caen_perms]
        add_cmds = [(4, g.id) for g in new_perms]
        self.sudo().write({'group_ids': remove_cmds + add_cmds})

    # onChange del radio de rol en el frontend
    # cuando se cambia el rol, las casillas de permisos se actualizan
    @api.onchange('caen_role')
    def _onchange_caen_role(self):
        if not self.caen_role:
            return
        xmlid = ROLE_MAP.get(self.caen_role)
        new_perms = self.env['res.groups']

        if xmlid:
            group = self.env.ref(xmlid, raise_if_not_found=False)
            if group:
                new_perms = group.all_implied_ids.filtered(
                    lambda g: g.privilege_id
                )

        self.group_ids = [(6, 0, new_perms.ids)]
