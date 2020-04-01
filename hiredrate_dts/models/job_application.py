from odoo import api, fields, models
import base64

class Applicant(models.Model):
	_inherit = "hr.applicant"

	@api.multi
	def account_token(self):
		user_token = self.env['iap.account'].get('analytic_service')
		return user_token

	@api.multi
	def print_resume(self):
		job_id = False
		applicant_id = False
		template_settings = False
		if self.job_id:
			job_id = self.job_id.id
		if self.job_id and self.job_id.template_id:
			template_settings = self.job_id.template_id.id
		if self:
			applicant_id = self.id
		file_doc, file_name = self.resume_document_print(job_id=job_id, applicant_id=applicant_id, template=False)
		action = self.env.ref('hiredrate_dts.action_print_wizard')
		result = {
			'name': 'Formatted Profile',
			'help': action.help,
			'type': action.type,
			'view_type': action.view_type,
			'view_mode': action.view_mode,
			'target': action.target,
			'context': {'default_job_position_id': job_id,
						# 'default_job_application_id': 178,
						'default_is_application': True,
						'default_output_filedata': file_doc,
						'default_output_filename': file_name,
						'default_template_settings': template_settings,
						'default_job_application_id': applicant_id,
						},
			'res_model': action.res_model,
		}
		return result

	@api.multi
	def resume_document_print(self, job_id=False, applicant_id=False, template=False):
		if job_id:
			hr_job = self.env['hr.job'].browse(job_id)
		if applicant_id:
			hr_applicant = self.env['hr.applicant'].browse(applicant_id)
		if template:
			template_id = self.env['template.settings'].browse(template)
			template_category_code = template_id.template_id.template_category.code
			template_code = template_id.template_id.code
			template_settings = template_id
			template_name = template_id.name
		else:
			template_id = hr_job.template_id
			template_category_code = hr_job.template_id.template_id.template_category.code
			template_code = hr_job.template_id.template_id.code
			template_settings = hr_job.template_id
			template_name = template_id.name
		if job_id and template_id:
			sections = []
			value = []
			if template_id.add_sections:
				for line in template_settings.add_sections:
					field_name = line.ir_fields.name
					application_values = self.read([field_name])
					if line.ir_fields.field_description.lower() == 'objective':
						name = 'SUMMARY'
						value = [application_values[0][field_name]]
					elif line.ir_fields.field_description.lower() == 'skills':
						name = 'SKILLS'
						skill_id = self.env['skill.details'].browse(application_values[0][field_name])
						skill_name = []
						if skill_id:
							for skill in skill_id:
								skill_name.append(skill.name)
						value = skill_name
					elif line.ir_fields.field_description.lower() == 'educational details':
						name = 'EDUCATION'
						education_id = self.env['educational.details'].browse(application_values[0][field_name])
						education_name = []
						if education_id:
							for edu in education_id:
								date = ''
								if edu.start_date:
									date = str(edu.start_date)
								if edu.end_date:
									date += 'to' + str(edu.end_date)
								education_name.append({
									'degree': edu.type_id.name if edu.type_id else '',
									'qualification_name': edu.qual_name.name if edu.qual_name else '',
									'qualification_major': edu.qual_major.name if edu.qual_major else '',
									'school_name': edu.school_name or '',
									'school_university': edu.school_university or '',
									'date': date,
								})
						value = education_name
					elif line.ir_fields.field_description.lower() == 'employment details':
						name = 'EMPLOYMENT'
						employment_id = self.env['employment.details'].browse(application_values[0][field_name])
						employment_name = []
						if employment_id:
							for employ in employment_id:
								date = ''
								if employ.start_date:
									date = str(employ.start_date)
								if employ.end_date:
									date += 'to' + str(employ.end_date)
								employment_name.append({
									'position_name': employ.position or '',
									'company_name': employ.name or '',
									'employment_summary': employ.description or '',
									'date': date,
								})
						value = employment_name
					else:
						form_values = []
						name = line.ir_fields.field_description.upper()

						if line.ir_fields.ttype in ['many2many', 'many2one', 'one2many']:
							model_id = self.env[line.ir_fields.relation].browse(application_values[0][field_name])
							if model_id:
								for rec in model_id:
									form_values.append(rec.name)
						elif line.ir_fields.ttype in ['boolean', 'char', 'date', 'datetime', 'float', 'integer',
													  'selection', 'text']:
							form_values.append(application_values[0][field_name])
						value = form_values

					sections.append({
						'name': name,
						'value': value
					})
			format_type = False
			if template_id and template_id.format_type:
				format_type = template_id.format_type

			data = {
				"category_id": template_category_code,
				"application_id": hr_applicant.application_id,
				"template_name": template_name,
				"sections": sections,
				"applicant_name": hr_applicant.name,
				"document_type": format_type
			}

			token = self.account_token()
			if token:
				api_document, api_document_status = self.env['template.request'].template_service_iap(token=token, call='post', data=data, template_code=template_code, doc_generation=True)
				template_api_id = None
				document_id = None
				if api_document in [200, 201]:
					if api_document_status['parameters']:
						if api_document_status['parameters']['template_id']:
							template_api_id = api_document_status['parameters']['template_id']
						if api_document_status['parameters']['document_id']:
							document_id = api_document_status['parameters']['document_id']

				document_get_api, document_get_api_status = self.env['template.request'].template_service_iap(token=token, call='get', template_code=template_api_id, document_id=document_id, format_type=format_type)
				if document_get_api in [200, 201]:
					name = ''
					file_path = ''
					if self.name:
						name = self.name
					elif self.partner_name:
						name = self.partner_name
					if format_type and format_type == 'docx':
						file_name = name + ".docx"
					else:
						file_name = name + ".pdf"
					file_doc = base64.b64decode(document_get_api_status)
				return file_doc, file_name
