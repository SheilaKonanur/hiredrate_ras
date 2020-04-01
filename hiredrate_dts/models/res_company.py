# -*- coding: utf-8 -*-
from odoo import fields, models, api, _

class ResCompany(models.Model):
	_inherit = "res.company"

	cmplify_dts = fields.Boolean('HIREdrate DTS', default=True)
	dts_bridge_host = fields.Char('Host', default="http://service.hiredrate.com")