# -*- coding: utf-8 -*-
from odoo import fields, models, api

class ResPartner(models.Model):
	_inherit = "res.partner"

	customer_id = fields.Char('Customer Id')
	client_id = fields.Char('Client Id')
	api_key = fields.Char('API Key')