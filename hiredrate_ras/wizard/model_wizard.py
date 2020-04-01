# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ModelWizard(models.TransientModel):
	"""Model Wizard"""

	_name = "model.wizard"

	name = fields.Char('Name')
	model_id = fields.Many2one('model.details', string='Model')
	job_position_id = fields.Many2one('hr.job', 'Job Position')

	@api.multi
	def model_fetch_action(self):
		if self.model_id:
			# self.job_position_id.model = False
			self.job_position_id.model = self.model_id.name