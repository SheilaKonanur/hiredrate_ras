# -*- coding: utf-8 -*-
{
    'name': "HIREdrate Template Service",
    'version': '13.0.1.0.1',
    'summary': """Template Services""",
    'category': 'Human Resources',
    'description': """
        Resume generation tool.
    """,

    'author': "The Office BPO",
    'license': 'LGPL-3',
    'company': 'The OfficeBPO',
    'maintainer': 'The OfficeBPO',
    'support': 'apps.admin@theofficebpo.com',
	'website': 'www.hiredrate.com',
    'demo': [],

    # any module necessary for this one to work correctly
    'depends': ['base', 'hr_recruitment', 'hiredrate_registry'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'wizard/print_wizard_view.xml',
        'views/res_config_settings_view.xml',
        'views/job_position_view.xml',
        'views/job_application_view.xml',
    ],
    # only loaded in demonstration mode
    'qweb': [],
    'application': True,
    'sequence': 1,
}

