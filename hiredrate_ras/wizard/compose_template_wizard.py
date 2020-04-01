# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from openerp.exceptions import UserError

class ComposeTemplateWizard(models.TransientModel):
	"""Model Wizard"""

	_name = "compose.template.wizard"

	attachment_required =fields.Boolean('Attachment Required?')
	resume_template = fields.Selection([('app_resume', 'Applicant Resume'), ('dts_resume', 'Paskon Resume')], default='app_resume', string="Resume Template", required=True)
	match_run_ref = fields.Many2one('match.run.history', 'Match Run Ref')
	dts_installed = fields.Boolean('DTS Installed', compute="compute_dts_module", store=True)
	applicant_status = fields.Char('Response Status')

	@api.multi
	@api.depends('attachment_required')
	def compute_dts_module(self):
		module_rec = self.env['ir.module.module'].search([('name', '=', 'cmplify_dts'), ('state', '=', 'installed')])
		for rec in self:
			if module_rec:
				rec.dts_installed = True
			else:
				rec.dts_installed = False

	@api.onchange('resume_template')
	def onchange_resume_template(self):
		applications = self.match_run_ref.applications
		applicants = []
		if self.resume_template == 'app_resume':
			# applicants = []
			for app in applications:
				ir_attachment = self.env['ir.model'].search([('model', '=', 'ir.attachment')], limit=1).id
				dts_created_field = self.env['ir.model.fields'].search([('name', '=', 'dts_created'), ('model_id', '=', ir_attachment)])
				domain = [('res_model', '=', 'hr.applicant'), ('res_id', '=', app.id)]
				if dts_created_field:
					domain.append(('dts_created', '!=', True))
				attachment_rec = self.env['ir.attachment'].search(domain)
				if not attachment_rec:
					applicants.append(app.name or app.partner_name)
			if applicants:
				applicants = ', '.join(applicants)
				self.applicant_status = "The following applicants doesn't have resumes.\n %s"% (applicants)
		else:
			self.applicant_status = False

	@api.multi
	def open_mail_template_action(self):
		self.ensure_one()
		ir_model_data = self.env['ir.model.data']
		try:
			template_id = ir_model_data.get_object_reference('hiredrate_ras', 'email_template_match_analytic')[1]
		except ValueError:
			template_id = False
		try:
			compose_form_id = ir_model_data.get_object_reference('mail', 'email_compose_message_wizard_form')[1]
		except ValueError:
			compose_form_id = False

		if self.match_run_ref and self.match_run_ref.applications and template_id:
			applications = self.match_run_ref.applications
			attachment = []
			for app in applications:
				ir_attachment = self.env['ir.model'].search([('model', '=', 'ir.attachment')], limit=1).id
				if self.resume_template == 'app_resume':
					dts_created_field = self.env['ir.model.fields'].search([('name', '=', 'dts_created'), ('model_id', '=', ir_attachment)])
					domain = [('res_model', '=', 'hr.applicant'), ('res_id', '=', app.id)]
					if dts_created_field:
						domain.append(('dts_created', '!=', True))

					attachment_rec = self.env['ir.attachment'].search(domain, limit=1)
					if attachment_rec:
						attachment.append(attachment_rec)
				elif self.resume_template == 'dts_resume':
					dts_created_field = self.env['ir.model.fields'].search([('name', '=', 'dts_created'), ('model_id', '=', ir_attachment)])
					domain = [('res_model', '=', 'hr.applicant'), ('res_id', '=', app.id)]
					if dts_created_field:
						domain.append(('dts_created', '!=', True))

					attachment_rec = self.env['ir.attachment'].search(domain)
					if attachment_rec:
						for attach in attachment_rec:
							attach.unlink()
					job_position_rec = self.match_run_ref.job_position_rec
					if job_position_rec and job_position_rec.template_id:
						dts_template = job_position_rec.template_id
					else:
						raise UserError("Please update template in Job Position")
					binary_file, file_name = app.resume_document_print(job_id=job_position_rec.id, applicant_id=app.id, template=dts_template.id)
					attachment_id = self.env['ir.attachment'].with_context(skip_updation=True).create({
						'name': file_name,
						'type': 'binary',
						'datas': binary_file,
						'datas_fname': file_name,
						'store_fname': file_name,
						'res_model': app._name,
						'res_id': app.id,
						'mimetype': 'application/x-pdf',
						'dts_created': True
					})
					attachment.append(attachment_id)
			template_rec = self.env['mail.template'].browse(template_id)
			if attachment and self.attachment_required:
				if template_rec:
					template_rec.attachment_ids = False
					template_rec.attachment_ids = [(4, rec.id, None) for rec in attachment]
			elif not self.attachment_required:
				template_rec.attachment_ids = False
		ctx = dict(self._context or {})
		ctx.update({
			'default_model': 'match.run.history',
			'default_res_id': self.match_run_ref.id,
			'default_use_template': bool(template_id),
			'default_template_id': template_id,
			'default_composition_mode': 'comment',
			'model_description': 'Match Analytics',
			'custom_layout': "mail.mail_notification_paynow",
		})

		return {
			'name': _('Compose Email'),
			'type': 'ir.actions.act_window',
			'view_type': 'form',
			'view_mode': 'form',
			'res_model': 'mail.compose.message',
			'views': [(compose_form_id, 'form')],
			'view_id': compose_form_id,
			'target': 'new',
			'context': ctx,
		}

class MailComposer(models.TransientModel):
	_inherit = 'mail.compose.message'

	@api.multi
	def account_token(self):
		user_token = self.env['iap.account'].get('analytic_service')
		return user_token

	@api.multi
	def action_send_mail(self):
		token = self.account_token()
		if token:
			self.env['api.request'].send_mail_iap(token=token)