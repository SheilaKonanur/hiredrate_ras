# -*- coding: utf-8 -*-
from odoo import models, fields, api, SUPERUSER_ID, _
from odoo.exceptions import UserError

class MatchRunHistory(models.Model):
	_name = "match.run.history"
	_inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
	_order = "id desc"

	@api.depends('experience_prior', 'skills_prior', 'qualification_prior', 'certification_prior')
	def compute_weightage(self):
		for rec in self:
			total_sum = int(rec.qualification_prior) + int(rec.skills_prior) + int(rec.experience_prior) + int(rec.certification_prior)
			if (rec.qualification_prior == '5' and rec.skills_prior == '5' and rec.experience_prior == '5' and rec.certification_prior == '5') or (rec.qualification_prior == '3' and rec.skills_prior == '3' and rec.experience_prior == '3' and rec.certification_prior == '3') or (rec.qualification_prior == '2' and rec.skills_prior == '2' and rec.experience_prior == '2' and rec.certification_prior == '2') or (rec.qualification_prior == '0' and rec.skills_prior == '0' and rec.experience_prior == '0' and rec.certification_prior == '0'):
				skill_weightage = 25
				qual_weightage = 25
				exp_weightage = 25
				certificate_weightage = 25
			else:
				skill_weightage = int(rec.skills_prior) * (100 / total_sum)
				qual_weightage = int(rec.qualification_prior) * (100 / total_sum)
				exp_weightage = int(rec.experience_prior) * (100 / total_sum)
				certificate_weightage = int(rec.certification_prior) * (100 / total_sum)
			rec.skills_weightage = skill_weightage
			rec.qualification_weightage = qual_weightage
			rec.experience_weightage = exp_weightage
			rec.certification_weightage = certificate_weightage
			if (rec.skills_weightage + rec.qualification_weightage + rec.experience_weightage + rec.certification_weightage) != 100:
				remaining_weightage = 100 - (rec.skills_weightage + rec.qualification_weightage + rec.experience_weightage + rec.certification_weightage)
				rec.skills_weightage = rec.skills_weightage + remaining_weightage

	name = fields.Char("Name", required=True, track_visibility='always')
	experience_prior = fields.Selection([('5', 'High'), ('3', 'Medium'), ('2', 'Low'), ('0', 'None')], 'Experience', default='0', required=True)
	skills_prior = fields.Selection([('5', 'High'), ('3', 'Medium'), ('2', 'Low'), ('0', 'None')], 'Skill', default='0', required=True)
	qualification_prior = fields.Selection([('5', 'High'), ('3', 'Medium'), ('2', 'Low'), ('0', 'None')], 'Qualification', default='0', required=True)
	certification_prior = fields.Selection([('5', 'High'), ('3', 'Medium'), ('2', 'Low'), ('0', 'None')], 'Certification', default='0', required=True)
	experience_weightage = fields.Integer('Experience', compute='compute_weightage', store=True)
	skills_weightage = fields.Integer('Skill', compute='compute_weightage', store=True)
	qualification_weightage = fields.Integer('Qualification', compute='compute_weightage', store=True)
	certification_weightage = fields.Integer('Certification', compute='compute_weightage', store=True)
	job_position_id = fields.Char('Job Position Id')
	match_analytic_id = fields.Char('Match Analytic Id')
	state = fields.Selection([('draft', 'Draft'),('in_progress', 'InProgress'),('complete', 'Complete'),('error','Error')], required=True, default='draft', string='Status')
	start_index = fields.Integer('Start Index', default='1')
	end_index = fields.Integer('End Index', default=False)
	applications = fields.Many2many('hr.applicant', string='Applications')
	company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.user.company_id)
	no_of_applications = fields.Char('No. of Applications', compute="compute_applications")
	response_status = fields.Char('Response Status')
	match_analytic_result = fields.One2many('match.analytic','match_history_ref','Match Analytic Result')
	job_position_name = fields.Char('Job Position')
	job_position_rec = fields.Many2one('hr.job', 'Job Position')
	job_position_skills = fields.One2many('skill.details', 'skill_match', 'Skills')
	# job_position_skills = fields.One2many('skill.details', 'skill_id', 'Skills', related="job_position_rec.skills")
	job_position_skill_text = fields.Char('Job Position Skill Text')
	user_id = fields.Many2one('res.users', 'User', readonly=True, default=lambda self: self.env.uid)
	active = fields.Boolean('Active', default=True)
	application_template = fields.Many2one('ir.actions.report', 'Report Template')
	job_board_ref = fields.Boolean('Updated in Job Board')

	@api.multi
	def _error_mes(self):
		return ('%s already exist!' % (self.name))

	@api.multi
	def _check_customer_is_duplicated(self):
		customer_rec = self.env['match.run.history'].search([])
		customer_name = []
		if customer_rec:
			for rec in customer_rec:
				if rec.name in customer_name:
					return False
				else:
					customer_name.append(rec.name)
		return True

	_constraints = [
		(_check_customer_is_duplicated, _error_mes, ['name'])

	]

	def _compute_access_url(self):
		super(MatchRunHistory, self)._compute_access_url()
		for order in self:
			order.access_url = '/my/analytics_result/%s' % (order.id)

	@api.model
	def default_get(self, fields):
		res = super(MatchRunHistory, self).default_get(fields)
		match_name = ''
		if self.env.user.company_id:
			match_name = self.env['ir.sequence'].with_context(force_company=self.env.user.company_id.id).next_by_code(
				'match.run.history') or _('New')
		else:
			match_name = self.env['ir.sequence'].next_by_code('match.run.history') or _('New')
		job_position = self.env['hr.job'].browse(self.env.context.get('active_ids'))
		job_position_skill_text = []
		exp_weightage = 25
		qual_weightage = 25
		skill_weightage = 25
		certificate_weightage = 25
		report_template = self.env['ir.actions.report'].search([('model', '=', 'hr.applicant')], limit=1)
		if job_position:
			applications = self.env['hr.applicant'].search([('job_id', '=', job_position.id), ('analytic_status', '=', 'COMPLETE'), ('stage_id.code', 'in', ['IQ']), ('analytic_count', '=', 0)])
			job_position_skills = None
			if job_position.skills:
				job_position_skills = job_position.skills.ids
				for rec in job_position.skills:
					job_position_skill_text.append(rec.name)
			if job_position.skills and not job_position.certifications and not job_position.qualification and job_position.min_exp in ['--', None] and job_position.max_exp in ['--', None]:
				exp_weightage = '0'
				qual_weightage = '0'
				skill_weightage = '5'
				certificate_weightage = '0'
			elif job_position.skills and job_position.certifications and not job_position.qualification and job_position.min_exp in ['--', None] and job_position.max_exp in ['--', None]:
				exp_weightage = '0'
				qual_weightage = '0'
				skill_weightage = '5'
				certificate_weightage = '5'
			elif job_position.skills and not job_position.certifications and job_position.qualification and job_position.min_exp in ['--', None] and job_position.max_exp in ['--', None]:
				exp_weightage = '0'
				qual_weightage = '5'
				skill_weightage = '5'
				certificate_weightage = '0'
			elif job_position.skills and not job_position.certifications and not job_position.qualification and (job_position.min_exp not in [
					'--', None] or job_position.max_exp not in ['--', None]):
				exp_weightage = '5'
				qual_weightage = '0'
				skill_weightage = '5'
				certificate_weightage = '0'
			elif job_position.skills and job_position.certifications and job_position.qualification and job_position.min_exp in [
					'--', None] and job_position.max_exp in ['--', None]:
				exp_weightage = '0'
				qual_weightage = '5'
				skill_weightage = '5'
				certificate_weightage = '5'
			elif job_position.skills and not job_position.certifications and job_position.qualification and (job_position.min_exp not in [
					'--', None] or job_position.max_exp not in ['--', None]):
				exp_weightage = '5'
				qual_weightage = '5'
				skill_weightage = '5'
				certificate_weightage = '0'
			elif job_position.skills and job_position.certifications and not job_position.qualification and (job_position.min_exp not in [
					'--', None] or job_position.max_exp not in ['--', None]):
				exp_weightage = '5'
				qual_weightage = '0'
				skill_weightage = '5'
				certificate_weightage = '5'
			elif job_position.skills and job_position.certifications and job_position.qualification and (job_position.min_exp not in [
					'--', None] or job_position.max_exp not in ['--', None]):
				exp_weightage = '5'
				qual_weightage = '5'
				skill_weightage = '5'
				certificate_weightage = '5'

		res.update({
			'name': match_name if match_name else 'New',
			'experience_prior': exp_weightage,
			'skills_prior': skill_weightage,
			'qualification_prior': qual_weightage,
			'certification_prior': certificate_weightage,
			'applications': applications.ids or None,
			'job_position_id': job_position.job_position_id,
			'job_position_name' : applications[0].job_id.name if applications else None,
			'job_position_skills': job_position_skills,
			'job_position_rec': job_position.id,
			'job_position_skill_text': ", ".join(job_position_skill_text),
			'application_template': report_template.id
		})
		return res

	@api.depends('applications')
	def compute_applications(self):
		for rec in self:
			if rec.applications:
				rec.no_of_applications = len(rec.applications)

	@api.model
	def create(self, vals):
		res = super(MatchRunHistory, self).create(vals)
		if res.job_position_rec and res.job_position_rec.skills and res.job_position_skills:
			for skills in res.job_position_skills:
				if skills.id not in res.job_position_rec.skills.ids:
					raise UserError("Please enter appropriate skills.\n Skills required to run match analytics are %s"%(res.job_position_skill_text))
		if not res.applications:
			raise UserError("Cannot run Match Analytics without applications")
		if res.job_position_rec:
			# res.job_position_rec.match_analytics_ids = [(4, res.id, None)]
			res.job_position_rec.with_context(skip_updation=True).write({'match_analytics_ids': [(4, res.id, None)]})
		app_name = []
		if res.applications:
			for app in res.applications:
				if app.stage_id.code not in ['SL','IQ']:
					app_name.append(app.partner_name)
		if app_name:
			raise UserError("The following applications cannot run match analytics:-\n %s"%(", ".join(map(str, app_name))))
		if res.experience_weightage or res.skills_weightage or res.qualification_weightage or res.certification_weightage:
			total = res.experience_weightage + res.skills_weightage + res.qualification_weightage + res.certification_weightage
			if total > 100:
				raise UserError('All weightage must equivalent to 100.')
		skill_name = []
		if res.job_position_skills:
			for skill_rec in res.job_position_skills:
				skill_name.append(skill_rec.name)
		data = {
			"match_name": res.name,
			"weightage": {
				"skills": res.skills_weightage/100,
				"certification": res.certification_weightage/100,
				"qualification": res.qualification_weightage/100,
				"experience": res.experience_weightage/100
			},
			"applications": [rec.job_application_id for rec in res.applications],
			"required_skills": skill_name,
			"model": res.job_position_rec.model if res.job_position_rec.model else ''
			}
		job_position_id = res.job_position_id
		if data:
			token = res.job_position_rec.account_token()
			if token:
				api, status = self.env['api.request'].match_analytic_iap(data, token, job_position_id=job_position_id, call='post')
		application_id = []
		result = {}
		if api in [200, 201]:
			if status['status'] == 'COMPLETE' and 'parameters' in status.keys() and 'recommendation_values' in status['parameters'].keys() and 'score_values' in status['parameters'].keys():
				if status['parameters']['recommendation_values'] and status['parameters']['score_values']:
					for x in status['parameters']['recommendation_values']:
						for l in status['parameters']['score_values']:
							if x['application_id'] == l['application_id']:
								result[x['application_id']] = x
								result[x['application_id']].update(l)
				rank_order = []
				if result:
					for line in result:
						rank_order.append(result[line])
					rank_order = sorted(rank_order, key=lambda x: (x['candidate_score']), reverse=True)
					count = 1
					for dict in rank_order:
						result[dict['application_id']] = dict
						result[dict['application_id']]['rank'] = count
						count += 1
					match_analytic = status['parameters']['match_analytics_id']
					res.match_analytic_id = match_analytic
					match_rec = self.env['match.analytic'].search([('match_analytic_id', '=', match_analytic)])
					if not match_rec:
						for app in result:
							skill_rec = []
							qualification = []
							application_rec = self.env['hr.applicant'].search([('job_application_id', '=', app)])
							if application_rec:
								application_id.append(application_rec.id)
							if result[app]['qualification'] != 0:
								if application_rec:
									for rec in application_rec:
										if rec.job_id and rec.educational_details:
											for edu in rec.educational_details:
												if edu.type_id in application_rec.job_id.qualification.ids:
													qualification.append(edu.type_id.name)
							else:
								if application_rec:
									for rec in application_rec:
										if rec.job_id and rec.educational_details:
											for edu in rec.educational_details:
												if edu.type_id:
													qualification.append(edu.type_id.name)
													break

							if result[app]['skill_sname'] != 0:
								for line in result[app]['skill_sname']:
									skill = self.env['skill.details'].search([('name', '=ilike', line)])
									if skill:
										skill_rec.append(skill[0])
									else:
										skill = self.env['skill.details'].create({'name': line.title()})
										skill_rec.append(skill)
							ir_attachment = self.env['ir.model'].search([('model', '=', 'ir.attachment')], limit=1).id
							dts_created_field = self.env['ir.model.fields'].search([('name', '=', 'dts_created'), ('model_id', '=', ir_attachment)])
							domain = [('res_model', '=', 'hr.applicant'), ('res_id', '=', application_rec.id)]
							if dts_created_field:
								domain.append(('dts_created', '=', False))
							attachment_rec = self.env['ir.attachment'].search(domain, limit=1)
							total_skills = 0
							matched_skills = 0
							if result[app]['noofrequireskills']:
								total_skills = result[app]['noofrequireskills']
							if result[app]['skillsMatched']:
								matched_skills = result[app]['skillsMatched']
							vals = {
								'name': application_rec.partner_name or application_rec.name,
								'match_rank': result[app]['rank'],
								'application_name': application_rec.name,
								'mobile':application_rec.partner_phone or application_rec.partner_mobile,
								'skills_matched': ', '.join(result[app]['skill_sname']).lower(),
								'skill_match': [(4, rec.id, None) for rec in skill_rec],
								'qualification_matched': ', '.join(qualification) or 'Not Matched',
								'analytic_score': round(result[app]['candidate_score']),
								'compatibility_score': result[app]['compatibility_score'],
								'resume_file_name': attachment_rec.datas_fname if attachment_rec else False,
								'resume_attachment': attachment_rec.datas if attachment_rec else False,
								'match_count': str(matched_skills) + "/" + str(total_skills),
								'application_id': app,
								'job_position_id': status['parameters']['job_position_id'],
								'match_analytic_id': status['parameters']['match_analytics_id'],
							}
							match_analytic_rec = self.env['match.analytic'].create(vals)
							match_analytic_rec.applications = application_rec.id
							application_rec.with_context(skip_updation=True).write({'analytic_count': int(result[app]['ma_count'])})
							res.match_analytic_result = [(4, match_analytic_rec.id, None)]

		if status['status'] == 'IN_PROGRESS':
			res.state = 'in_progress'
		elif status['status'] == 'COMPLETE':
			res.state = 'complete'
		elif status['status'] == 'ERROR':
			res.state = 'error'
		res.response_status = status['message']

		return res

	@api.multi
	def action_match_analytic_view(self):
		if self.state not in ['in_progress']:
			action = self.env.ref('hiredrate_ras.action_match_analytics')
			result = {
				'name': action.name,
				'help': action.help,
				'type': action.type,
				'view_type': action.view_type,
				'view_mode': action.view_mode,
				'target': action.target,
				'domain': [('match_analytic_id', '=', self.match_analytic_id)],
				'res_model': action.res_model,
			}
			return result

	@api.multi
	def refresh_match_analytics_cron(self):
		match_analytic = self.env['match.run.history'].search([])
		for rec in match_analytic:
			if rec.state == 'in_progress':
				job_position = rec.job_position_id
				match_analytic = rec.match_analytic_id
				data = {}
				token = rec.job_position_rec.account_token()
				if token:
					api, status = self.env['api.request'].match_analytic_iap(data, token, job_position_id=job_position_id, match_analytic_id=match_analytic, call='get')
				if api in [200, 201]:
					if status['status'] == 'COMPLETE' and 'parameters' in status.keys() and 'results' in status['parameters'].keys():
						if api['parameters']['results']:
							match_analytic = status['parameters']['match_analytics_id']
							match_rec = self.env['match.analytic'].search([('match_analytic_id', '=', match_analytic)])
							if not match_rec:
								for app in status['parameters']['results']:
									qualification = []
									application_rec = self.env['hr.applicant'].search([('job_application_id', '=', app)])
									# raise UserError("Test")
									if application_rec:
										application_id.append(application_rec.id)
									if status['parameters']['results'][app]['qualification'] != 0:
										if application_rec and application_rec.job_id and application_rec.educational_details:
											for rec in application_rec.educational_details:
												if rec.type_id.id in application_rec.job_id.qualification.ids:
													qualification.append(rec.type_id.name)
									attachment_rec = self.env['ir.attachment'].search([('res_model', '=', 'hr.applicant'), ('res_id', '=', application_rec.id)], limit=1)
									total_skills = str(status['parameters']['results'][app]['noofrequireskills'])
									matched_skills = str(status['parameters']['results'][app]['skillsMatched'])
									vals = {
										'name': application_rec.partner_name or '',
										'match_rank': status['parameters']['results'][app]['rank'],
										'application_name': application_rec.name,
										'mobile': application_rec.partner_phone or application_rec.partner_mobile,
										'skills_matched': ', '.join(status['parameters']['results'][app]['skill_sname'].lower()),
										'match_count': ', '.join([i + "/" + j for i, j in zip(matched_skills, total_skills)]),
										'compatibility_score': status['parameters']['results'][app]['compatibility_score'],
										'resume_attachment': attachment_rec.datas,
										'experience': status['parameters']['results'][app]['experience'],
										'qualification_matched': ', '.join(qualification) or 'Not Matched',
										'analytic_score': round(status['parameters']['results'][app]['candidate_score']),
										'application_id': app,
										'job_position_id': status['parameters']['job_position_id'],
										'match_analytic_id': status['parameters']['match_analytics_id'],
									}
									self.env['match.analytic'].create(vals)

					if status['status'] == 'IN_PROGRESS':
						rec.state = 'in_progress'
					elif status['status'] == 'COMPLETE':
						rec.state = 'complete'
					elif status['status'] == 'ERROR':
						rec.state = 'error'
						rec.response_status = api['message']
				elif api not in [200, 201]:
					# api = api.json()
					rec.state = 'error'
					rec.response_status = api['message']

	@api.multi
	def action_view_application(self):
		action = self.env.ref('hr_recruitment.action_hr_job_applications')
		result = {
			'name': action.name,
			'help': action.help,
			'type': action.type,
			'view_type': action.view_type,
			'view_mode': action.view_mode,
			'target': action.target,
			'domain': [('id', '=', self.applications.ids)],
			'res_model': action.res_model,
		}
		return result

	@api.multi
	def action_send_by_email(self):
		action = self.env.ref('hiredrate_ras.action_compose_template_wizard')
		result = {
			'name': 'Attachment Template Selection',
			'help': action.help,
			'type': action.type,
			'view_type': action.view_type,
			'view_mode': action.view_mode,
			'target': action.target,
			'context': {'default_match_run_ref': self.id},
			'res_model': action.res_model,
		}
		return result

	@api.multi
	def unlink(self):
		for analytics in self:
			token = analytics.job_position_rec.account_token()
			if token:
				if analytics:
					analytics.active = False
					if analytics.job_position_rec and analytics.job_position_rec.job_position_id:
						job_position = analytics.job_position_rec.job_position_id
					job_application = ''
					match_analytic = analytics.match_analytic_id
					api, status = self.env['api.request'].delete_iap(token, job_position_id=job_position, job_application_id=job_application, match_analytic_id=match_analytic, call='delete', model='match_analytic')
					# api = self.env['api.request'].delete_request('delete', job_position, job_application, match_analytic)