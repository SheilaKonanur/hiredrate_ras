# -*- coding: utf-8 -*-
from odoo import models, fields, api, SUPERUSER_ID

class Job(models.Model):
    _inherit = "hr.job"

    template_id = fields.Many2one("template.settings", "Template")