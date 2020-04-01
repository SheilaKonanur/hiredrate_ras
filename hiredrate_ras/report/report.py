# -*- coding: utf-8 -*-

from odoo import api, models
from datetime import datetime
import calendar
DEFAULT_MONTH ={
	'january': 'Jan',
	'february': 'Feb',
	'march': 'Mar',
	'april': 'Apr',
	'may': 'May',
	'june': 'Jun',
	'july': 'Jul',
	'august': 'Aug',
	'september': 'Sep',
	'october': 'Oct',
	'november': 'Nov',
	'december': 'Dec'
}

class ApplicationReport(models.AbstractModel):
	_name = 'report.hiredrate_ras.report_application'

	@api.model
	def _get_report_values(self, docids, data=None):
		report = self.env['ir.actions.report'].sudo()._get_report_from_name('hiredrate_ras.report_application')
		applications = self.env['hr.applicant'].browse(docids)
		education = []
		if applications and applications.educational_details:
			for line in applications.educational_details:
				start_month = None
				start_year = None
				start_month_name = None
				end_month = None
				end_year = None
				end_month_name = None
				if line.start_date:
					start_month = datetime.strptime(str(line.start_date), '%Y-%m-%d').strftime('%m')
					start_year = datetime.strptime(str(line.start_date), '%Y-%m-%d').strftime('%Y')
					start_month_name = calendar.month_name[int(start_month)]
					start_month_name = start_month_name.lower()
					start_month_name = DEFAULT_MONTH[start_month_name]
				if line.end_date:
					end_month = datetime.strptime(str(line.end_date), '%Y-%m-%d').strftime('%m')
					end_year = datetime.strptime(str(line.end_date), '%Y-%m-%d').strftime('%Y')
					end_month_name = calendar.month_name[int(end_month)]
					end_month_name = end_month_name.lower()
					end_month_name = DEFAULT_MONTH[end_month_name]

				edu = {
					'name': line.school_name,
					'degree': line.type_id.name if line.type_id else '',
					'qual_name': line.qual_name.name if line.qual_name else '',
					'qual_major': line.qual_major.name if line.qual_major else '',
					'university': line.school_university,
					'start_name': start_month_name,
					'end_name': end_month_name,
					'start_year': start_year,
					'end_year': end_year,
				}
				education.append(edu)
		employment = []
		if applications and applications.employment_details:
			for line in applications.employment_details:
				start_month = None
				start_year = None
				start_month_name = None
				end_month = None
				end_year = None
				end_month_name = None
				if line.start_date:
					start_month = datetime.strptime(str(line.start_date), '%Y-%m-%d').strftime('%m')
					start_year = datetime.strptime(str(line.start_date), '%Y-%m-%d').strftime('%Y')
					start_month_name = calendar.month_name[int(start_month)]
					start_month_name = start_month_name.lower()
					start_month_name = DEFAULT_MONTH[start_month_name]

				if line.end_date:
					end_month = datetime.strptime(str(line.end_date), '%Y-%m-%d').strftime('%m')
					end_year = datetime.strptime(str(line.end_date), '%Y-%m-%d').strftime('%Y')
					end_month_name = calendar.month_name[int(end_month)]
					end_month_name = end_month_name.lower()
					end_month_name = DEFAULT_MONTH[end_month_name]
				employ = {
					'position': line.position,
					'company': line.name,
					'description': line.description,
					'start_name': start_month_name,
					'end_name': end_month_name,
					'start_year': start_year,
					'end_year': end_year,
				}
				employment.append(employ)
		certifications = []
		if applications and applications.certifications:
			for certi in applications.certifications:
				certifications.append(certi.name.title())
		skills = []
		if applications and applications.skills:
			for skill in applications.skills:
				skills.append(skill.name.capitalize())
		if skills:
			skills = ", ".join(skills)
		return {
			'doc_ids': docids,
			'doc_model': report.model,
			'docs': self.env[report.model].browse(docids),
			'report_type': data.get('report_type') if data else '',
			'education': education,
			'employment': employment,
			'certifications': certifications,
			'skills': skills
		}

class ApplicationPaskonReport(models.AbstractModel):
	_name = 'report.hiredrate_ras.report_application_paskon'

	@api.model
	def _get_report_values(self, docids, data=None):
		report = self.env['ir.actions.report'].sudo()._get_report_from_name('hiredrate_ras.report_application')
		applications = self.env['hr.applicant'].browse(docids)
		education = []
		if applications and applications.educational_details:
			for line in applications.educational_details:
				start_month = None
				start_year = None
				start_month_name = None
				end_month = None
				end_year = None
				end_month_name = None
				if line.start_date:
					start_month = datetime.strptime(str(line.start_date), '%Y-%m-%d').strftime('%m')
					start_year = datetime.strptime(str(line.start_date), '%Y-%m-%d').strftime('%Y')
					start_month_name = calendar.month_name[int(start_month)]
				if line.end_date:
					end_month = datetime.strptime(str(line.end_date), '%Y-%m-%d').strftime('%m')
					end_year = datetime.strptime(str(line.end_date), '%Y-%m-%d').strftime('%Y')
					end_month_name = calendar.month_name[int(end_month)]
				edu = {
					'name': line.school_name,
					'degree': line.type_id.name if line.type_id else '',
					'qual_name': line.qual_name.name if line.qual_name else '',
					'qual_major': line.qual_major.name if line.qual_major else '',
					'university': line.school_university,
					'start_name': start_month_name,
					'end_name': end_month_name,
					'start_year': start_year,
					'end_year': end_year,
				}
				education.append(edu)
		employment = []
		if applications and applications.employment_details:
			for line in applications.employment_details:
				start_month = None
				start_year = None
				start_month_name = None
				end_month = None
				end_year = None
				end_month_name = None
				if line.start_date:
					start_month = datetime.strptime(str(line.start_date), '%Y-%m-%d').strftime('%m')
					start_year = datetime.strptime(str(line.start_date), '%Y-%m-%d').strftime('%Y')
					start_month_name = calendar.month_name[int(start_month)]
				if line.end_date:
					end_month = datetime.strptime(str(line.end_date), '%Y-%m-%d').strftime('%m')
					end_year = datetime.strptime(str(line.end_date), '%Y-%m-%d').strftime('%Y')
					end_month_name = calendar.month_name[int(end_month)]
				employ = {
					'position': line.position,
					'company': line.name,
					'description': line.description,
					'start_name': start_month_name,
					'end_name': end_month_name,
					'start_year': start_year,
					'end_year': end_year,
				}
				employment.append(employ)
		certifications = []
		if applications and applications.certifications:
			for certi in applications.certifications:
				certifications.append(certi.name.title())
		return {
			'doc_ids': docids,
			'doc_model': report.model,
			'docs': self.env[report.model].browse(docids),
			'report_type': data.get('report_type') if data else '',
			'education': education,
			'employment': employment,
			'certifications': certifications,
		}