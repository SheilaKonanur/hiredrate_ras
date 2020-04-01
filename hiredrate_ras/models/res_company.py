# -*- coding: utf-8 -*-
from odoo import fields, models, api, _

class ResCompany(models.Model):
	_inherit = "res.company"

	cmplify_recruitment = fields.Boolean('HIREdrate RAS', default=True)
	job_position_parsing = fields.Boolean('Job Position', default=True)
	job_application_parsing = fields.Boolean('Job Application', default=True)
	match_analytic = fields.Boolean('Match Analytic', default=True)
	ras_bridge_host = fields.Char('Host', default="http://service.hiredrate.com")