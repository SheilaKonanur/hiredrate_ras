# -*- coding: utf-8 -*-

from odoo import models, fields, api

class SkillWizard(models.TransientModel):
	"""Skill Wizard"""

	_name = "skill.wizard"

	name = fields.Char('Name')
	skill_id = fields.Many2many('skill.details', string='Skills')
	job_position_id = fields.Many2one('hr.job', 'Job Position')

	@api.multi
	def skill_fetch_action(self):
		if self.skill_id:
			self.job_position_id.write({
				'skills': [[6, 0, self.skill_id.ids]]
			})