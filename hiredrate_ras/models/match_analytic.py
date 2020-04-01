# -*- coding: utf-8 -*-
from odoo import models, fields, api, SUPERUSER_ID
from openerp.exceptions import UserError

class MatchAnalytic(models.Model):
	_name = "match.analytic"
	_order = "match_rank"

	name = fields.Char('Applicant Name')
	experience_weightage = fields.Integer('Experience Weightage')
	skills_weightage = fields.Integer('Skill Weightage')
	qualification_weightage = fields.Integer('Qualification Weightage')
	certification_weightage = fields.Integer('Certification Weightage')
	match_rank = fields.Integer('Rank')
	application_name = fields.Char('Application Name')
	mobile = fields.Char('Phone Number')
	skills_match = fields.Many2many('skill.details', string='Skills')
	skills_matched = fields.Text('Skills Matched')
	match_count = fields.Char('Match Count')
	compatibility_score = fields.Char('Compatibility')
	cmskills = fields.Char('matched')
	experience = fields.Char('Experience')
	qualification_matched = fields.Text('Qualification')
	analytic_score = fields.Char('Match Analytics Score(%)')
	application_id = fields.Char('Application_id')
	job_position_id = fields.Char('Job Position Id')
	match_analytic_id = fields.Char('Match Analytics Id')
	company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.user.company_id)
	match_history_ref = fields.Many2one('match.run.history', 'Match History Ref')
	applications = fields.Many2one('hr.applicant', 'Applications')
	stage_id = fields.Char('Status', compute="application_stage_id", store=True)
	stage_code = fields.Char('Stage Code', compute="application_stage_id", store=True)
	resume_attachment = fields.Binary('Resume Attachment')
	resume_file_name = fields.Char("Form Filename")

	@api.depends('applications.stage_id')
	def application_stage_id(self):
		for rec in self:
			if rec.applications:
				rec.stage_id = rec.applications.stage_id.name
				rec.stage_code = rec.applications.stage_id.code

	@api.multi
	def short_list_application(self):
		for rec in self:
			res_model, res_id = self.env['ir.model.data'].get_object_reference('hr_recruitment', 'stage_job1')
			stage_id = self.env[res_model].browse(res_id)
			res_model_stage, res_id_stage = self.env['ir.model.data'].get_object_reference('hiredrate_ras','stage_extended_shortlist')
			short_list_stage = self.env[res_model_stage].browse(res_id_stage)
			if rec.applications.stage_id.id == stage_id.id:
				rec.applications.with_context(skip_updation=True).write({
					'stage_id': short_list_stage.id,
					'match_analytic_id': rec.match_history_ref.id
				})

	@api.multi
	def remove_application(self):
		for rec in self:
			res_model, res_id = self.env['ir.model.data'].get_object_reference('hr_recruitment', 'stage_job1')
			stage_id = self.env[res_model].browse(res_id)
			res_model_stage, res_id_stage = self.env['ir.model.data'].get_object_reference('hiredrate_ras', 'stage_extended_shortlist')
			short_list_stage = self.env[res_model_stage].browse(res_id_stage)
			if rec.applications.stage_id.id == short_list_stage.id:
				rec.applications.with_context(skip_updation=True).write({'stage_id': stage_id.id})
				rec.applications.with_context(skip_updation=True).write({
					'match_analytic_id': False,
					'match_skills': False,
					'match_experience': False,
					'match_degree': False,
					'match_score': False,
					'match_rank': False,

				})

	@api.multi
	def open_application(self):
		for rec in self:
			action = self.env.ref('hiredrate_ras.application_view_form')
			result = {
				'name': action.name,
				'help': action.help,
				'type': action.type,
				'view_type': action.view_type,
				'view_mode': action.view_mode,
				'target': 'new',
				'res_id': rec.applications.id,
				'res_model': action.res_model,
			}
			return result

	@api.multi
	def download_file(self):
		if self.resume_attachment:
			return {
				'type': 'ir.actions.act_url',
				'url': '/web/binary/download_document?model=match.analytic&field=resume_attachment&id=%s&filename=%s' %(self.id, self.resume_file_name),
				'target': 'self',
			}
		else:
			raise UserError("Resume is unavailable for this applicant!")