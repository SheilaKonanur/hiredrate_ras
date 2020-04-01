# -*- coding: utf-8 -*-
from odoo import models, fields, api

class PrintWizard(models.TransientModel):
    """Print Wizard"""

    _name = "print.wizard"

    output_filename = fields.Char('Print Name')
    output_filedata = fields.Binary('Print Document')
    job_position_id = fields.Many2one('hr.job', 'Job Position')
    job_application_id = fields.Many2one('hr.applicant', 'Application')
    is_application = fields.Boolean('Is Application')
    template_settings = fields.Many2one('template.settings', 'Template')

    @api.onchange('job_position_id')
    def onchange_job_position_id(self):
        self.job_application_id = False
        if self.env.context and self.env.context.get('active_model', False) == 'hr.applicant' and self.env.context.get('active_id', False):
            self.job_application_id = self.env.context['active_id']

    @api.multi
    def get_stock_file(self):
        if not self.is_application:
            template_settings = False
            active_ids = self.env.context.get('active_ids', []) or []
            if active_ids:
                template_settings = self.env['template.settings'].browse(active_ids)
            job_id = False
            applicant_id = False
            if self.job_application_id:
                job_id = self.job_application_id.job_id.id
                applicant_id = self.job_application_id.id
            if template_settings and self.job_application_id:
                file_doc, file_name = self.job_application_id.resume_document_print(job_id=job_id, applicant_id=applicant_id, template=template_settings.id)
            if file_doc and file_name:
                self.write({'output_filedata': file_doc, 'output_filename': file_name})
        return {
            'type': 'ir.actions.act_url',
            'url': '/web/binary/download_document?model=print.wizard&field=output_filedata&id=%s&filename=%s'%(self.id, self.output_filename),
            'target': 'main',
        }