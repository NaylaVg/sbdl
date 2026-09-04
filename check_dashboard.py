import xmlrpc.client

url = 'http://localhost:8069'
db = 'bdl_odoo'
common = xmlrpc.client.ServerProxy(url + '/xmlrpc/2/common')
uid = common.authenticate(db, 'admin', 'admin', {})
models = xmlrpc.client.ServerProxy(url + '/xmlrpc/2/object')

# Verificar que el menu raiz tiene action y web_icon
menu = models.execute_kw(db, uid, 'admin', 'ir.ui.menu', 'search_read', [[['id', '=', 229]]], {'fields': ['name', 'action', 'web_icon', 'parent_id']})
print('Menu root:', menu)

# Verificar la accion del dashboard
action = models.execute_kw(db, uid, 'admin', 'ir.actions.act_window', 'search_read', [[['res_model', '=', 'caen.dashboard']]], {'fields': ['id', 'name', 'res_model', 'target']})
print('Action:', action)

# Verificar permisos del modelo
perm = models.execute_kw(db, uid, 'admin', 'ir.model.access', 'search_read', [[['model_id.model', '=', 'caen.dashboard']]], {'fields': ['name', 'group_id', 'perm_read', 'perm_write', 'perm_create']})
print('Permisos:', perm)
