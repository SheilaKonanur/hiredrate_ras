# -*- coding: utf-8 -*-
from odoo import models, fields, api, SUPERUSER_ID
from odoo.exceptions import UserError
from datetime import datetime

class Job(models.Model):
	_inherit = "hr.job"

	@api.depends('skills', 'certifications', 'qualification', 'min_exp', 'max_exp')
	def compute_form_fill(self):
		for rec in self:
			if rec.skills or rec.certifications or rec.qualification or rec.min_exp not in ['--', False] or rec.max_exp not in ['--', False]:
				rec.is_form_fill = True
			elif rec.skills and rec.certifications and rec.qualification and rec.min_exp in ['--', False] and rec.max_exp in ['--', False]:
				rec.is_form_fill = False

	is_form_fill = fields.Boolean('Form Fill', compute='compute_form_fill', store=True, default=False)
	cmplify_position = fields.Boolean('HIREdrate RAS Position', default=lambda self: self.env.user.company_id.cmplify_recruitment)
	certifications = fields.One2many('certificate.details', 'certificate_id', 'Certifications')
	skills = fields.One2many('skill.details', 'skill_id', 'Skills')
	qualification = fields.One2many('qualification.details', 'qualification_id', 'Qualifications')
	job_id = fields.Char('Position Id')
	job_position_id = fields.Char('Job Position Id')
	response_status = fields.Char('Response Status')
	analytic_status = fields.Char('Status')
	submit_match_analytic = fields.Boolean('Enable', default=lambda self: self.env.user.company_id.match_analytic)
	min_exp = fields.Selection(
		[('--', '--'), ('0', '0'), ('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5'), ('6', '6'), ('7', '7'),
		 ('8', '8'), ('9', '9'), ('10', '10'), ('11', '11'), ('12', '12'), ('13', '13'), ('14', '14'), ('15', '15'),
		 ('16', '16'), ('17', '17'), ('18', '18'), ('19', '19'), ('20', '20')], default='--',
		string="Minimum Experience")
	max_exp = fields.Selection(
		[('--', '--'), ('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5'), ('6', '6'), ('7', '7'), ('8', '8'),
		 ('9', '9'), ('10', '10'), ('11', '11'), ('12', '12'), ('13', '13'), ('14', '14'), ('15', '15'), ('16', '16'),
		 ('17', '17'), ('18', '18'), ('19', '19'), ('20', '20')], default='--', string="Maximum Experience")
	active = fields.Boolean('Active', default=True)
	hr_job = fields.Many2one('hr.job', 'Job Id')
	app_cnt = fields.Integer('Application Count', default=0)
	match_cnt = fields.Integer('Match Count', default=0)
	match_analytics_ids = fields.Many2many('match.run.history', string='Match Analytics')
	model = fields.Char('Training Model')
	application_template = fields.Many2one('ir.actions.report', 'Report Template')
	parse_required = fields.Boolean('Parse Required?', default=lambda self: self.env.user.company_id.job_position_parsing)
	job_ref_id = fields.Char('Job Ref Id')
	average_closing_recruitment = fields.Float('Recruitment Time in Days')
	average_shortlisted = fields.Float("Average Shortlisted Days")

	@api.multi
	def _error_message(self):
		return ('Job Position [%s] cannot be repeated!' % (self.name))

	@api.multi
	def _check_job_position_is_duplicated(self):
		hr_job = self.env['hr.job'].search([])
		job_position = []
		if hr_job:
			for rec in hr_job:
				if rec.name in job_position:
					return False
				else:
					job_position.append(rec.name)
		return True

	_constraints = [
		(_check_job_position_is_duplicated, _error_message, ['name']),
	]

	@api.multi
	def fetch_customer_id(self):
		customer_id = ''
		# if self.env.user.company_id.partner_id and self.env.user.company_id.partner_id.customer_id:
		# 	customer_id = self.env.user.company_id.partner_id.customer_id
		if self.env.user.company_id and self.env.user.company_id.customer_id:
			customer_id = self.env.user.company_id.customer_id
		return customer_id

	"""Getting record Ids of Certificate, Skills and Qualification."""

	@api.multi
	def getting_form_parameters(self, api):
		certifi_id = []
		skill_id = []
		qualifi_id = []
		"""Checking in database whether the certificate is there or its newly created. """
		if 'certifications' in api['parameters'].keys():
			for certi in api['parameters']['certifications']:
				certificates = self.env['certificate.details'].search([('name', '=ilike', certi)])
				if certificates:
					certifi_id.append(certificates[0].id)
				else:
					certi_vals = {
						'name': certi
					}
					certifi_id.append(self.env['certificate.details'].create(certi_vals).id)

		"""Checking in database whether the skill is there or its newly created. """
		if 'skills' in api['parameters'].keys():
			for skill in api['parameters']['skills']:
				skill_list = self.env['skill.details'].search([('name', '=ilike', skill)])
				if skill_list:
					skill_id.append(skill_list[0].id)
				else:
					skill_vals = {
						'name': skill
					}
					skill_id.append(self.env['skill.details'].create(skill_vals).id)

		"""Checking in database whether the qualification is there or its newly created. """
		if 'qualification' in api['parameters'].keys():
			for qual in api['parameters']['qualification']:
				qual_list = self.env['qualification.details'].search([('name', '=ilike', qual)])
				if qual_list:
					qualifi_id.append(qual_list[0].id)
				else:
					qual_vals = {
						'name': qual
					}
					qualifi_id.append(self.env['qualification.details'].create(qual_vals).id)
		return certifi_id, skill_id, qualifi_id

	@api.multi
	def account_token(self):
		user_token = self.env['iap.account'].get('analytic_service')
		return user_token

	"""On Creation or Updation if Job Position Id is not created then this function will execute."""

	@api.multi
	def job_position_creation(self, vals, call=''):
		certifi = []
		qualifi = []
		skills = []
		api = {}
		customer_id = self.fetch_customer_id()
		if not customer_id:
			raise UserError("Please enter Customer Id. \nGo to Recruitment -> Settings -> HIREdrate -> Enter Customer Id")
		# if self.env.user.partner_id.id not in self.env.user.company_id.partner_id.child_ids.ids:
		# 	raise UserError("Please register your User[%s] under your company [%s] \n Go to Contacts -> %s -> Add your company" % (self.env.user.partner_id.name, self.env.user.company_id.partner_id.name, self.env.user.partner_id.name))
		if vals.get('address_id', False):
			address = self.env['res.partner'].browse(vals['address_id'])
		else:
			address = self.address_id
		if vals.get('name', False):
			title = vals['name']
		else:
			title = self.name
		job_id = ''
		if vals.get('job_id', False):
			job_id = vals['job_id']
		elif self.job_id:
			job_id = self.job_id
		data = {
			"cust_id": customer_id or None,
			"org_job_id": job_id or '',
			"org_job_location": address.state_id.name or '',
			"org_job_title": title,
			'job_description': '',
			"max_experience": 0,
			"min_experience": 0,
			"qualification": [],
			"skills": [],
			"certifications": [],
			"job_position_state": self.state,
			"position_count": self.no_of_recruitment,
			"position_hired_count": self.no_of_hired_employee,
		}
		if (vals.get('description', False) or self.description) and not self.is_form_fill:
			if vals.get('description', False):
				data['job_description'] = vals['description']
			elif self.description:
				data['job_description'] = self.description

		elif self.is_form_fill:
			if vals.get('certifications', False):
				for line in self.env['certificate.details'].browse(vals['certifications'][0][2]):
					certifi.append(line.name)
			elif self.certifications:
				for line in self.certifications:
					certifi.append(line.name)

			if vals.get('qualification', False):
				for qual in self.env['qualification.details'].browse(vals['qualification'][0][2]):
					qualifi.append(qual.name)
			elif self.qualification:
				for line in self.qualification:
					qualifi.append(line.name)

			if vals.get('skills', False):
				for skl in self.env['skill.details'].browse(vals['skills'][0][2]):
					skills.append(skl.name)
			elif self.skills:
				for line in self.skills:
					skills.append(line.name)
			max_exp = 0
			min_exp = 0
			if vals.get('max_exp', False):
				max_exp = int(vals['max_exp']) if vals['max_exp'] != '--' else 0
			elif self.max_exp:
				max_exp = self.max_exp if self.max_exp != '--' else 0
			if vals.get('min_exp', False):
				min_exp = int(vals['min_exp']) if vals['min_exp'] != '--' else 0
			elif self.min_exp:
				min_exp = self.min_exp if self.min_exp != '--' else 0

			data['certifications'] = certifi
			data['skills'] = skills
			data['qualification'] = qualifi
			data['max_experience'] = int(max_exp)
			data['min_experience'] = int(min_exp)
		if data:
			token = self.account_token()
			if token:
				api, status = self.env['api.request'].job_position_iap(data, token, call=call)
				model_api, model_status = self.env['api.request'].model_fetch_iap(token, name=self.name, job_position_id=self.job_position_id, call='get')
			if model_api in [200, 201]:
				if model_status.get('parameters', False) and model_status['parameters']['available_models'] and 'Generic Model' in model_status['parameters']['available_models']:
					self.with_context(skip_updation=True).write({
					'model': 'Generic Model'
					})
			if api not in [200, 201]:
				self.with_context(skip_updation=True).write({
					'analytic_status': status['status'],
					'response_status': status['message']
				})
			elif api in [200, 201]:
				if 'description' in vals.keys() and not self.parse_required:
					status_message = 'Successfully created Job Position.'
					status_analytics = 'COMPLETE'
				else:
					status_message = status['message']
					status_analytics = status['status']

				self.with_context(skip_updation=True).write({
					'analytic_status': status_analytics,
					'response_status': status_message,
					'job_position_id': status['parameters']['job_position_id']
				})
		return data, status

	""""Once Job Position Id is created then Get call will be triggered for updation."""
	@api.multi
	def job_position_updation(self, vals, call=''):
		certifi = []
		qualifi = []
		skills = []
		api = {}
		if vals.get('name', False):
			name = vals['name']
		elif self.name:
			name = self.name
		if vals.get('address_id', False):
			partner = self.env['res.partner'].browse(vals['address_id'])
			location = partner.state_id.name
		elif self.address_id:
			location = self.address_id.state_id.name
		if vals.get('certifications', False):
			certificates = self.env['certificate.details'].browse(vals['certifications'][0][2])
			if certificates:
				for rec in certificates:
					certifi.append(rec.name)
		elif self.certifications:
			for line in self.certifications:
				certifi.append(line.name)
		if vals.get('skills', False):
			skill = self.env['skill.details'].browse(vals['skills'][0][2])
			if skill:
				for rec in skill:
					skills.append(rec.name)
		elif self.skills:
			for line in self.skills:
				skills.append(line.name)
		if vals.get('qualification', False):
			qualification = self.env['qualification.details'].browse(vals['qualification'][0][2])
			if qualification:
				for rec in qualification:
					qualifi.append(rec.name)
		elif self.qualification:
			for line in self.qualification:
				qualifi.append(line.name)
		if vals.get('max_exp', False):
			max_exp = vals['max_exp']
		elif self.max_exp:
			max_exp = self.max_exp
		if vals.get('min_exp', False):
			min_exp = vals['min_exp']
		elif self.min_exp:
			min_exp = self.min_exp
		data = {
			"org_job_location": location or '',
			"org_job_title": name,
			"certifications": [],
			"qualification": [],
			"skills": [],
			"max_experience": 0,
			"min_experience": 0,
			"job_description": '',
			"job_position_state": self.state,
			"position_count": self.no_of_recruitment,
			"position_hired_count": self.no_of_hired_employee
		}

		if self.is_form_fill:
			data['certifications'] = certifi
			data['skills'] = skills
			data['qualification'] = qualifi
			data['min_experience'] = int(min_exp) if min_exp != '--' else 0
			data['max_experience'] = int(max_exp) if max_exp != '--' else 0

		elif not self.is_form_fill and vals.get('description', False):
			data['job_description'] = vals['description']

		job_position = self.job_position_id
		if data:
			token = self.account_token()
			api, status = self.env['api.request'].job_position_iap(data, token, job_position_id=job_position, call=call)
			if api not in [200, 201]:
				self.with_context(skip_updation=True).write({
					'analytic_status': status['status'],
					'response_status': status['message']
				})
			elif api in [200, 201]:
				if 'description' in vals.keys() and not self.parse_required:
					status_message = 'Successfully updated Job Position.'
					status_analytics = 'COMPLETE'
				else:
					status_message = status['message']
					status_analytics = status['status']
				self.with_context(skip_updation=True).write({
					'analytic_status': status_analytics,
					'response_status': status_message,
				})
		return api

	@api.model
	def create(self, vals):
		"""Job Id auto sequence part"""
		self = super(Job, self).create(vals)
		"""Checking whether company_id is there not for configuration part."""
		cmplify_position = False
		if 'cmplify_position' in vals.keys():
			cmplify_position = vals.get('cmplify_position', False)
		else:
			cmplify_position = self.cmplify_position
		if cmplify_position:
			if vals.get('description', False) and self.is_form_fill:
				raise UserError("Please clear the form before entering the description.")
			"""Fetching and assigning sequence for Job Position"""
			if vals.get('company_id', False):
				self.with_context(skip_updation=True).write({'job_id': self.env['ir.sequence'].with_context(force_company=vals['company_id']).next_by_code('hr.job') or _('New')})
			else:
				self.with_context(skip_updation=True).write({'job_id': self.env['ir.sequence'].next_by_code('hr.job') or _('New')})
			""" Calling Bridge Server for Odoo Credits"""
			data, api = self.job_position_creation(vals=vals, call='post')
		return self

	@api.multi
	def write(self, vals):
		rec = super(Job, self).write(vals)
		if vals.get('state', False) and vals['state'] == 'open':
			start_date = self.create_date
			end_date = self.write_date
			diff = end_date - start_date
			days, seconds = diff.days, diff.seconds
			hours = diff.total_seconds() / 3600
			self.with_context(skip_updation=True).average_closing_recruitment = round(hours/24, 2)
		cmplify_position = False
		if 'cmplify_position' in vals.keys():
			cmplify_position = vals.get('cmplify_positon', False)
		else:
			cmplify_position = self.cmplify_position
		if cmplify_position:
			if vals.get('description', False) and self.is_form_fill:
				raise UserError("Please clear the form before entering the description.")
			if self.env.context.get('skip_updation', False) or 'is_published' in vals.keys() or 'website_published' in vals.keys():
				return super(Job, self).write(vals)
			if not self.job_position_id:
				data, api = self.job_position_creation(vals, call='post')
			if self.job_position_id:
				api = self.job_position_updation(vals, call='put')
			if 'parse_required' in vals.keys() and vals.get('parse_required', False):
				self.refresh_request()
			elif 'parse_required' in vals.keys() and not vals.get('parse_required', False):
				self.write({
					'certifications': [[6, 0, False]],
					'skills': [[6, 0, False]],
					'qualification': [[6, 0, False]],
					'min_exp': '--',
					'max_exp': '--'
				})
		return rec

	@api.multi
	def action_match_analysis(self):
		if not self.skills:
			raise UserError("Please enter Skills before Match Analytics.!")
		if not self.model:
			raise UserError("Please select Training Model before running Match Analytics.!")
		if self.analytic_status not in ['COMPLETE', 'COMPLETED']:
			raise UserError("Your Job Position cannot be send to Match Analysis on Progress State.")
		application_id = self.env['hr.applicant'].search(
			[('job_id', '=', self.id), ('analytic_status', '=', 'COMPLETE')])
		if len(application_id) < 2:
			raise UserError("Atleast two applications are required to run Match Analytics.")
		job_position = self.job_position_id
		action = self.env.ref('hiredrate_ras.action_match_run_history')
		result = {
			'name': action.name,
			'help': action.help,
			'type': action.type,
			'view_type': action.view_type,
			'view_mode': action.view_mode,
			'target': action.target,
			'domain': [('job_position_id', '=', job_position)],
			'res_model': action.res_model,
		}
		return result

	@api.multi
	def refresh_request(self):
		if self.cmplify_position:
			customer_id = self.fetch_customer_id()
			job_position = self.job_position_id
			document_attach = self.env['ir.attachment'].search([('res_model', '=', 'hr.job'), ('res_id', '=', self.id)])
			if self.analytic_status == 'IN_PROGRESS':
				data = {
					"cust_id": customer_id or None,
					"org_job_id": self.job_id,
					"org_job_location": self.address_id.state_id.name or '',
					"org_job_title": self.name,
				}
				document_attach = self.env['ir.attachment'].search([('res_model', '=', 'hr.job'), ('res_id', '=', self.id)])
				job_position = self.job_position_id
				api = {}
				data = {
					'certifications': [],
					'skills': [],
					'qualification': [],
					'min_experience': 0,
					'max_experience': 0,
				}
				token = self.account_token()
				if token:
					type = ''
					if self.description:
						type = 'description'
					elif document_attach:
						type = 'document'
					api, status = self.env['api.request'].job_position_iap(data, token, job_position_id=job_position, call='get', type=type)
				if api not in [200, 201]:
					self.with_context(skip_updation=True).write({
						'analytic_status': status['status'],
						'response_status': status['message']
					})

				elif api in [200, 201]:
					self.with_context(skip_updation=True).write({
						'analytic_status': status['status'],
						'response_status': status['message']
					})

					certifi_id, skill_id, qualifi_id = self.getting_form_parameters(status)
					self.write({
						'certifications': [(4, rec, None) for rec in certifi_id],
						'skills': [(4, rec, None) for rec in skill_id],
						'qualification': [(4, rec, None) for rec in qualifi_id],
						'min_exp': str(int(status['parameters']['min_experience'])) if status['parameters']['min_experience'] != None else '--',
						'max_exp': str(int(status['parameters']['max_experience'])) if status['parameters']['max_experience'] != None else '--'
					})

	@api.multi
	def refresh_request_cron(self):
		job_position = self.env['hr.job'].search([])
		if job_position:
			for rec in job_position:
				rec.response_status = ''
				rec.refresh_request()

	@api.multi
	def action_reset_form(self):
		if self.analytic_status == 'IN_PROGRESS':
			raise UserError("You cannot reset the form while processing.")
		if self.submit_match_analytic:
			job_position = self.job_position_id
			data = {
				"min_experience": 0,
				"max_experience": 0,
				"skills": [],
				"certifications": [],
				"qualification": []
			}
			token = self.account_token()
			if data and token:
				api, status = self.env['api.request'].job_position_iap(data, token, job_position_id=job_position, call='put', reset=1)
			if api in [200, 201]:
				self.with_context(skip_updation=True).write({
					'analytic_status': status['status'],
					'response_status': status['message'],
				})
		else:
			self.with_context(skip_updation=True).write({
				'analytic_status': '',
				'response_status': '',
			})
		self.with_context(skip_updation=True).write({
			'certifications': [[6, 0, False]],
			'skills': [[6, 0, False]],
			'qualification': [[6, 0, False]],
			'min_exp': '--',
			'max_exp': '--'
		})

	@api.multi
	def unlink(self):
		for position in self:
			token = self.account_token()
			if token:
				position.active = False
				if position.job_position_id:
					job_position = position.job_position_id
					application_id = self.env['hr.applicant'].search([('job_id', '=', position.id)])
					if application_id:
						for app in application_id:
							app.active = False
					analytic_id = self.env['match.run.history'].search([('job_position_rec', '=', position.id)])
					if analytic_id:
						for match in analytic_id:
							match.active = False
					api, status = self.env['api.request'].delete_iap(token, job_position_id=job_position, call='delete', model='hr_job')
					# api = self.env['api.request'].delete_request('delete', job_position)

	@api.multi
	def skill_fetch(self):
		skill_id = []
		if self.name:
			name = self.name
			job_position = self.job_position_id
			token = self.account_token()
			if token:
				api, status = self.env['api.request'].skill_suggestion_iap(token, name=name, job_position_id=job_position, call='get')
			if api in [200, 201]:
				if status.get('predicted_skills', False):
					for skill in status['predicted_skills']:
						skill_rec = self.env['skill.details'].search([('name', '=ilike', skill)])
						if skill_rec:
							skill_id.append(skill_rec[0].id)
						else:
							vals = {
								'name': skill,
								'company_id': self.env.user.company_id.id
							}
							skill_rec = self.env['skill.details'].create(vals)
							skill_id.append(skill_rec.id)

		action = self.env.ref('hiredrate_ras.action_skill_wizard')
		result = {
			'name': action.name,
			'help': action.help,
			'type': action.type,
			'view_type': action.view_type,
			'view_mode': action.view_mode,
			'target': 'new',
			'context': {'default_job_position_id': self.id, 'default_skill_id': skill_id},
			'res_model': action.res_model,
		}
		return result

	@api.multi
	def model_fetch(self):
		model_id = []
		if self.name:
			name = self.name
			job_position = self.job_position_id
			token = self.account_token()
			if token:
				api, status = self.env['api.request'].model_fetch_iap(token, name=name, job_position_id=job_position, call='get')
			if api in [200, 201]:
				if status.get('parameters', False) and status['parameters']['available_models']:
					model_rec = self.env['model.details'].search([])
					if model_rec:
						for line in model_rec:
							line.unlink()
					for model in status['parameters']['available_models']:
						vals = {
							'name': model,
							'company_id': self.env.user.company_id.id
						}
						model_rec = self.env['model.details'].create(vals)
						model_id.append(model_rec.id)

		action = self.env.ref('hiredrate_ras.action_model_wizard')
		result = {
			'name': action.name,
			'help': action.help,
			'type': action.type,
			'view_type': action.view_type,
			'view_mode': action.view_mode,
			'target': 'new',
			'context': {'default_job_position_id': self.id},
			'res_model': action.res_model,
		}
		return result

	@api.multi
	def toggle_active(self):
		self = self.with_context(skip_updation=True)
		super(Job, self).toggle_active()

	@api.multi
	def set_open(self):
		# self = self.with_context(skip_updation=True)
		return super(Job, self).set_open()

	@api.multi
	def set_recruit(self):
		# self = self.with_context(skip_updation=True)
		return super(Job, self).set_recruit()

	@api.multi
	def refresh_report_status_cron(self):
		self = self.with_context(skip_updation=True)
		hr_job_rec = self.env['hr.job'].search([])
		if hr_job_rec:

			for rec in hr_job_rec:
				"""Average Job Position to close a recruitment"""
				start_date = rec.create_date
				end_date = datetime.today()
				diff = end_date - start_date
				hours = diff.total_seconds() / 3600
				rec.average_closing_recruitment = round(hours / 24, 2)

				application_rec = self.env['hr.applicant'].search([('job_id', '=', rec.id), ('active', '=', True)])
				app_cnt = 0
				total_hour = 0
				rec.average_shortlisted = None
				if application_rec:
					for app in application_rec:
						if app.shortlisted_date:
							app_start = app.create_date
							app_end = app.shortlisted_date
							diff = app_end - app_start
							hours = diff.total_seconds() / 3600
							total_hour += hours
							app_cnt += 1
				if total_hour:
					total_hour = total_hour / app_cnt
					rec.average_shortlisted = round(total_hour / 24, 2)
				analytic_rec = self.env['match.run.history'].search(
					[('job_position_rec', '=', rec.id), ('active', '=', True)])
				if application_rec:
					rec.app_cnt = len(application_rec)
				if analytic_rec:
					rec.match_cnt = len(analytic_rec)


class ModelDetails(models.Model):
	_name = "model.details"

	name = fields.Char('Name')
	company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.user.company_id)


class CertificationDetails(models.Model):
	_name = "certificate.details"

	name = fields.Char('Certification Name')
	certificate_id = fields.Many2one('hr.job', 'Certification Id')
	certificate_fm = fields.Many2one('job.description', 'Certificate Ref')
	certificate_jd = fields.Many2one('job.description', 'Certificate Ref')
	company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.user.company_id)


class SkillDetails(models.Model):
	_name = "skill.details"

	name = fields.Char('Skill Name')
	skill_id = fields.Many2one('hr.job', 'Skill Id')
	skill_match = fields.Many2one('match.run.history', 'Skill Match')
	skill_fm = fields.Many2one('job.description', 'Skill Ref')
	skill_jd = fields.Many2one('job.description', 'Skill Ref')
	color = fields.Integer('Color Index')
	company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.user.company_id)


class QualificationDetails(models.Model):
	_name = "qualification.details"

	name = fields.Char('Qualification')
	qualification_id = fields.Many2one('hr.job', 'Qualification Id')
	qualification_fm = fields.Many2one('job.description', 'Qualification Ref')
	qualification_jd = fields.Many2one('job.description', 'Qualification Ref')
	company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.user.company_id)


class RecruitmentStage(models.Model):
	_inherit = "hr.recruitment.stage"

	code = fields.Char('Code', readonly=True)
