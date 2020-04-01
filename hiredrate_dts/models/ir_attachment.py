# -*- coding: utf-8 -*-
from odoo import api, fields, models

class IrAttachment(models.Model):
	_inherit = "ir.attachment"

	dts_created = fields.Boolean('DTS Created')