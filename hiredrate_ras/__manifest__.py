# -*- coding: utf-8 -*-
{
    'name': "HIREdrate Match Analytics",
    'version': '13.0.1.0.1',
    'summary': """Recruitments & Analytics""",
    'category': 'Human Resources',
    'description': """
        Recruitments & Analytics
    """,
    'author': "The Office BPO",
    'license': 'LGPL-3',
    'company': 'The OfficeBPO',
    'maintainer': 'The OfficeBPO',
    'support': 'apps.admin@theofficebpo.com',
	'website': 'www.hiredrate.com',
    'demo': [],

    # any module necessary for this one to work correctly
    'depends': ['base', 'hr', 'hr_recruitment', 'web', 'portal', 'hiredrate_registry'],

    # always loaded
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/ir_sequence_data.xml',
        'data/cron.xml',
        'data/data.xml',
        'data/template.xml',
        'report/template.xml',
        'report/report.xml',
        'report/applicant.xml',
        'wizard/skill_wizard_view.xml',
        'wizard/model_wizard_view.xml',
        # 'wizard/application_docx_view.xml',
        'wizard/compose_template_wizard_view.xml',
        'views/res_config_settings_view.xml',
        'views/job_position_view.xml',
        'views/job_application_view.xml',
        'views/match_analytic_view.xml',
        'views/match_run_history_view.xml',
        'views/templates.xml',
        'views/portal_template.xml',
    ],
    # only loaded in demonstration mode
    'qweb': [],
    'application': True,
    'images': ['static/description/MatchAnalytic.gif'],
    'sequence': 1,
}