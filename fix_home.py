import xmlrpc.client

url = 'http://localhost:8069'
db = 'bdl_odoo'
common = xmlrpc.client.ServerProxy(url + '/xmlrpc/2/common')
uid = common.authenticate(db, 'admin', 'admin', {})
models = xmlrpc.client.ServerProxy(url + '/xmlrpc/2/object')

# Cambiar la Home Action del usuario admin a nuestro Dashboard
models.execute_kw(db, uid, 'admin', 'res.users', 'write', [[uid], {'action_id': 411}])
print('Home Action cambiada a Dashboard (id=411)')

# Verificar
user = models.execute_kw(db, uid, 'admin', 'res.users', 'read', [uid], {'fields': ['name', 'login', 'action_id']})
print('Usuario:', user)
