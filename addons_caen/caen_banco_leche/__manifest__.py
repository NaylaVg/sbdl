{
    'name': 'CAEN Banco de Leche Humana',
    'version': '1.0',
    'category': 'Operations',
    'summary': 'Gestión integral del Banco de Leche Humana del Hospital Perrando',
    'description': """
Sistema CAEN - Banco de Leche Humana
====================================
Sistema web para gestionar la trazabilidad completa:
madre -> frasco -> pasteurización -> fraccionamiento -> entrega -> bebé.

- Gestión de donantes, consentimientos y serologías
- Control de frascos, pasteurización y fraccionamiento (con códigos QR)
- Control de stock con alarmas automáticas
- Gestión nutricional de pacientes (percentiles OMS)
- Auditoría total e inmutable
    """,
    'author': 'Hospital Dr. J. C. Perrando',
    'website': '',
    'depends': [
        'base',
        'contacts',
        'stock',
        'mrp',
        'hr',
        'uom',
        'auth_signup',
        'base_geolocalize',
    ],
'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/stock_locations.xml',
        'data/cron_alertas.xml',
        'data/filtros.xml',
        'data/auth_signup_config.xml',
        'data/test_users.xml',
        'views/dashboard_views.xml',
        'views/res_partner_views.xml',
        'views/menu_views.xml',
        'views/donante_views.xml',
        'views/visita_views.xml',
        'views/consentimiento_views.xml',
        'views/serologia_views.xml',
        'views/frasco_views.xml',
        'views/pasteurizacion_views.xml',
        'views/fraccionamiento_views.xml',
        'views/distribucion_views.xml',
        'views/paciente_views.xml',
        'views/nutricion_views.xml',
        'views/bitacora_views.xml',
        'views/alerta_views.xml',
        'views/stock_views.xml',
        'views/reportes_views.xml',
        'views/usuarios_caen_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'caen_banco_leche/static/src/css/caen_style.css',
            'caen_banco_leche/static/src/js/caen_role_watcher.js',
            'caen_banco_leche/static/src/js/caen_profile.js',
            'caen_banco_leche/static/src/xml/caen_profile.xml',
        ],
    },
    'installable': True,
    'application': True,
    'auto_install': False,
}
