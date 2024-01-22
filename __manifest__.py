# -*- coding: utf-8 -*-
##############################################################################
#
#    Palmares Sucursal Matanzas
#    Departamento de Informática y Comunicaciones
#    Autor: Raúl Sánchez Pérez
#
##############################################################################{
    'name': 'Certificados Comerciales',
    'version': '1.0',
    'summary': """Control de los certificados comerciales. Notificación del vencimiento""",
    'description': """Control del vencimiento de los certificados comerciales..""",
    'category': 'Operaciones',
    'author': 'Dpto. Informática',
    'company': 'Sucursal Palmares Matanzas',
    'maintainer': 'Sucursal Palmares Matanzas',
    'website': "http://intranet.var.palmares.cu",
    'depends': ['base', 'hr'],
    'data': [
        'views/ccomercial_check_list_view.xml',
        'views/ccomercial_document_view.xml',
        'views/report.xml',
        'security/ccomercial_document_security.xml',
        'security/ir.model.access.csv',
    ],
    'demo': ['data/data.xml'],
    'images': ['static/description/banner.jpg'],
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'application': True,
}
