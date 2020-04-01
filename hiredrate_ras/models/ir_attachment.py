# -*- coding: utf-8 -*-
from odoo import api, fields, models
from openerp.exceptions import UserError

class IrAttachment(models.Model):
	_inherit = "ir.attachment"

	@api.model
	def create(self, vals):
		if self.env.context.get('skip_updation', False):
			return super(IrAttachment, self).create(vals)
		res = super(IrAttachment, self).create(vals)
		company_id = self.env.user.company_id
		if res.res_model == 'hr.job' and company_id:
			position = self.env['hr.job'].browse(res.res_id)
			if position.cmplify_position:
				job_position = position.job_position_id
				if position.analytic_status == 'IN_PROGRESS':
					raise UserError("Please process the Job Position before you update document")
				elif not position.is_form_fill:
					token = position.account_token()
					if token:
						binary_doc = res.datas
						doc_name = res.datas_fname
						job_position_id = position.job_position_id
						api, status = self.env['api.request'].document_parser_iap(token=token, job_position_id=job_position_id, binary_doc=binary_doc, doc_name=doc_name, call='post', model='hr_job')
						position.with_context(skip_updation=True).write({
							'analytic_status': status['status'],
							'response_status': status['message']
						})
				else:
					raise UserError("Please reset the Job Position before uploading document")
		elif res.res_model == 'hr.applicant' and company_id:
			application = self.env['hr.applicant'].browse(res.res_id)
			if application and application.cmplify_application:
				job_application_id = application.job_application_id
				job_position_id = ''
				if application:
					job_position_id = application.job_id.job_position_id
				if (not application.report_objective and not application.is_form_fill) and not application.description:
					token = application.account_token()
					if token:
						binary_doc = res.datas
						doc_name = res.datas_fname
						api, status = self.env['api.request'].document_parser_iap(token=token, job_position_id=job_position_id, job_application_id=job_application_id, binary_doc=binary_doc, doc_name=doc_name, call='post', model='hr_applicant')
						application.with_context(skip_updation=True).write({
							'analytic_status': status['status'],
							'response_status': status['message']
						})
				else:
					raise UserError("Please reset the Application before uploading document.")
		return res

	@api.multi
	def write(self, vals):
		if self.env.context.get('skip_updation', False):
			return super(IrAttachment, self).write(vals)
		res = super(IrAttachment, self).write(vals)
		company_id = self.env.user.company_id
		if self.res_model == 'hr.job' and company_id:
			position = self.env['hr.job'].browse(self.res_id)
			if position.cmplify_position:
				if position.analytic_status == 'IN_PROGRESS':
					raise UserError("Please process the Job Position before you update document")
				elif not position.is_form_fill:
					token = position.account_token()
					if token:
						binary_doc = self.datas
						doc_name = self.datas_fname
						job_position_id = position.job_position_id
						api, status = self.env['api.request'].document_parser_iap(token=token, job_position_id=job_position_id, binary_doc=binary_doc, doc_name=doc_name, call='put', model='hr_job')
						position.with_context(skip_updation=True).write({
							'analytic_status': status['status'],
							'response_status': status['message']
						})
				else:
					raise UserError("Please reset the Job Position before uploading document.")

		elif self.res_model == 'hr.applicant' and company_id:
			application = self.env['hr.applicant'].browse(self.res_id)
			if application.cmplify_application:
				job_position_id = application.job_id.job_position_id
				job_application_id = application.job_application_id
				if (not application.report_objective and not application.is_form_fill) and not application.description:
					token = application.account_token()
					if token:
						binary_doc = self.datas
						doc_name = self.datas_fname
						api, status = self.env['api.request'].document_parser_iap(token=token, job_position_id=job_position_id, job_application_id=job_application_id, binary_doc=binary_doc, doc_name=doc_name, call='put', model='hr_applicant')
						application.with_context(skip_updation=True).write({
							'analytic_status': status['status'],
							'response_status': status['message']
						})
				else:
					raise UserError("Please reset the Application before uploading document.")
		return res
