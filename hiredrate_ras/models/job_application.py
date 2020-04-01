from odoo import api, fields, models
from datetime import datetime
from openerp.exceptions import UserError

class Applicant(models.Model):
    _inherit = "hr.applicant"

    """Displaying these results in kanban view"""
    @api.multi
    @api.depends('match_analytic_id')
    def compute_match_skills(self):
        for rec in self:
            if rec.match_analytic_id and rec.match_analytic_id.match_analytic_result:
                for app in rec.match_analytic_id.match_analytic_result:
                    if rec.id == app.applications.id:
                        rec.match_skills = app.skills_matched
                        rec.match_experience = app.applications.total_exp
                        rec.match_degree = app.qualification_matched
                        rec.match_score = app.analytic_score
                        rec.match_rank = app.match_rank

    @api.depends('skills', 'certifications', 'total_exp', 'educational_details', 'employment_details')
    def compute_form_fill(self):
        for rec in self:
            if rec.skills or rec.certifications or rec.total_exp or rec.educational_details or rec.employment_details:
                rec.is_form_fill = True
            elif rec.skills and rec.certifications and rec.total_exp and rec.educational_details and rec.employment_details:
                rec.is_form_fill = False

    @api.multi
    def account_token(self):
        user_token = self.env['iap.account'].get('analytic_service')
        return user_token

    is_form_fill = fields.Boolean('Form Fill', compute='compute_form_fill', store=True, default=False)
    cmplify_application = fields.Boolean('HIREdrate RAS Application', default=lambda self: self.env.user.company_id.cmplify_recruitment)
    description = fields.Text("Summary")
    form_filling = fields.Boolean('Form Fill', default=False)
    application_id = fields.Char('Application Id')
    certifications = fields.Many2many('certificate.details', string='Certifications')
    skills = fields.Many2many('skill.details', string='Skills')
    employment_details = fields.One2many('employment.details', 'employment_ref', 'Employment Details')
    educational_details = fields.One2many('educational.details', 'educational_ref', 'Educational Details')
    total_exp = fields.Selection(
        [('0', '0'), ('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5'), ('6', '6'), ('7', '7'), ('8', '8'),
         ('9', '9'), ('10', '10'), ('11', '11'), ('12', '12'), ('13', '13'), ('14', '14'), ('15', '15'), ('16', '16'),
         ('17', '17'), ('18', '18'), ('19', '19'), ('20', '20'), ('21', '21'), ('22', '22'), ('23', '23'), ('24', '24'),
         ('25', '25'), ('26', '26'), ('27', '27'), ('28', '28'), ('29', '29'), ('30', '30')], default='',
        string="Total Experience")
    job_application_id = fields.Char('Job Application Id')
    response_status = fields.Char('Response Status')
    analytic_status = fields.Char('Status')
    submit_match_analytic = fields.Boolean('Enable')
    match_analytic_id = fields.Many2one('match.run.history', 'Match Analytics')
    match_skills = fields.Char('Match Skills', compute='compute_match_skills', store=True)
    match_experience = fields.Char('Match Experience', compute='compute_match_skills', store=True)
    match_degree = fields.Char('Match Degree', compute='compute_match_skills', store=True)
    match_score = fields.Char('Match Score', compute='compute_match_skills', store=True)
    match_rank = fields.Char('Match Rank', compute='compute_match_skills', store=True)
    analytic_count = fields.Integer('Match Analytics Count', default=0)
    application_count = fields.Integer('Application Count', default=0)
    report_objective = fields.Text('Objective')
    resume_attachment = fields.Binary('Attachment', attachment=True)
    resume_file_name = fields.Char("Form Filename")
    parse_required = fields.Boolean('Parse Required?', default=lambda self: self.env.user.company_id.job_application_parsing)
    survey_id = fields.Many2one('survey.survey', related='', string="Survey", readonly=False)
    applicant_ref_id = fields.Char('Application Reference')
    shortlisted_date = fields.Datetime('Shortlisted Date')

    @api.model
    def default_get(self, fields):
        res = super(Applicant, self).default_get(fields)
        survey_id = None
        if self.job_id and self.job_id.survey_id:
            survey_id = self.job_id.survey_id.id
        res.update({
            'survey_id': survey_id
        })
        return res

    @api.multi
    def fetch_customer_id(self):
        customer_id = ''
        # if self.env.user.partner_id and self.env.user.partner_id.parent_id and self.env.user.partner_id.parent_id.customer_id:
        #     customer_id = self.env.user.partner_id.parent_id.customer_id
        if self.env.user.company_id and self.env.user.company_id.customer_id:
            customer_id = self.env.user.company_id.customer_id
        return customer_id

    def compute_application_count(self):
        for rec in self:
            if rec.job_id:
                application_rec = self.env['hr.applicant'].search([('job_id', '=', rec.job_id.id)])
                if application_rec:
                    rec.application_count = len(application_rec)

    """APi Status Check and returning message to UI."""

    @api.multi
    def api_status_check(self, vals, api='', status=''):
        if api not in [200, 201]:
            self.with_context(skip_updation=True).write({
                'analytic_status': status['status'],
                'response_status': status['message']
            })
        elif api in [200, 201]:
            if vals and not vals.get('job_application_id', False) and not self.job_application_id:
                self.with_context(skip_updation=True).write({'job_application_id': status['parameters']['application_id']})
            self.with_context(skip_updation=True).write({
                'analytic_status': status['status'],
                'response_status': status['message']
            })

    @api.multi
    def get_form_parameters(self, vals={}, call=''):
        name = ''
        contact = ''
        email = ''
        application_id = ''
        total_exp = 0
        certifi = []
        skills = []
        education = []
        employment = []
        """Fetching Name"""
        if self.name:
            name = self.name.split()
        f_name = name[0]
        name.pop(0)
        l_name = " ".join(name)
        """Fetching contact number"""
        if self.partner_mobile or self.partner_phone:
            contact = self.partner_mobile or self.partner_phone
        """Fetching email address"""
        if self.email_from:
            email = self.email_from
        """Fetching Application Id"""
        if vals.get('application_id', False):
            application_id = vals['application_id']
        elif self.application_id:
            application_id = self.application_id
        """Fetching Total Experience"""
        if self.total_exp:
            total_exp = self.total_exp

        """Fetching Certification Details."""
        if self.certifications:
            for line in self.certifications:
                certifi.append(line.name)

        """Fetching Skills Details."""
        if self.skills:
            for line in self.skills:
                skills.append(line.name)

        """Fetching Educational Details."""
        if self.educational_details:
            for line in self.educational_details:
                start_date = ''
                end_date = ''
                if line.start_date:
                    start_date = datetime.strptime(str(line.start_date), "%Y-%m-%d").strftime("%d/%m/%Y")
                if line.end_date:
                    end_date = datetime.strptime(str(line.end_date), "%Y-%m-%d").strftime("%d/%m/%Y")

                educa = {
                    "degree_major": line.qual_major.name or '',
                    "degree_name": line.qual_name.name or '',
                    "degree_type": line.type_id.name or '',
                    "start_date": start_date,
                    "end_date": end_date,
                    "school_name": line.school_name or '',
                    "school_type": line.school_university or '',
                }
                education.append(educa)

        """Fetching Employment Details."""
        if self.employment_details:
            for line in self.employment_details:
                employ = {
                    "employer_org_name": line.name or '',
                    "position_title": line.position or '',
                    "start_date": datetime.strptime(str(line.start_date), "%Y-%m-%d").strftime("%d/%m/%Y") if line.start_date else '',
                    "end_date": datetime.strptime(str(line.end_date), "%Y-%m-%d").strftime("%d/%m/%Y") if line.end_date else '',
                    "employment_description": line.description if line.description else ''
                }
                employment.append(employ)
        return f_name, l_name, contact, email, application_id, total_exp, certifi, skills, education, employment

    @api.multi
    def job_application_creation(self, vals, call=''):
        status = ''
        f_name, l_name, contact, email, application_id, total_exp, certifi, skills, education, employment = self.get_form_parameters(
            vals)
        if vals.get('stage_id', False):
            status_id = self.env['hr.recruitment.stage'].browse(vals['stage_id'])
            status = status_id.name

        """Default data to be passed if parameters are not passed."""
        data = {
            "org_application_id": application_id,
            "application_fname": f_name,
            "application_lname": l_name,
            "application_contact": contact,
            "application_emailid": email,
            "total_exp": 0,
            "application_skills": [],
            "application_certifications": [],
            "application_employment": [],
            "application_education": [],
            "application_summary": '',
            "application_objective": '',
            # "application_status": status,
            "hire_state": status
        }

        if ( self.is_form_fill or vals.get('name', False) or vals.get('partner_name', False)) and (not vals.get('description', False)):
            data['application_certifications'] = certifi
            data['application_skills'] = skills
            data['application_education'] = education
            data['application_employment'] = employment
            data['total_exp'] = float(total_exp)
            if vals.get('report_objective', False):
                data['application_objective'] = vals.get('report_objective', False)

        elif not self.is_form_fill and vals.get('description', False):
            data['application_summary'] = vals['description']

        if vals.get('job_id', False):
            job_position = self.env['hr.job'].browse(vals['job_id']).job_position_id
        elif self.job_id:
            job_position = self.job_id.job_position_id
        if data:
            """Calling bridge server for odoo credits"""
            token = self.account_token()
            if token:
                api, status = self.env['api.request'].job_application_iap(data, token, call=call, job_position_id=job_position)
                self.api_status_check(vals, api=api, status=status)

    @api.multi
    def job_application_updation(self, vals={}, call=''):
        data = {}
        status = ''
        if vals.get('stage_id', False):
            status_id = self.env['hr.recruitment.stage'].browse(vals['stage_id'])
            status = status_id.name
        else:
            status = self.stage_id.name
        f_name, l_name, contact, email, application_id, total_exp, certifi, skills, education, employment = self.get_form_parameters(vals)
        description = self.description if self.description else ""
        if self.env.context.get('skip_description', False):
            description = ""
        data = {
            "application_certifications": certifi,
            "application_skills": skills,
            "application_contact": contact,
            "application_education": education,
            "application_emailid": email,
            "application_employment": employment,
            "application_fname": f_name,
            "application_lname": l_name,
            "total_exp": float(total_exp),
            "application_summary": self.description if self.description else "",
            "application_objective": vals['report_objective'] if vals.get('report_objective', False) else '',
            # "application_status": status
            "hire_state": status
        }
        if self.job_id:
            job_position = self.job_id.job_position_id
        job_application_id = ''
        if self.job_application_id:
            job_application_id = self.job_application_id
        if data:
            """Calling bridge server for odoo credits"""
            token = self.account_token()
            if token:
                api, status = self.env['api.request'].job_application_iap(data, token, call=call, job_position_id=job_position, job_application_id=job_application_id)
                self.api_status_check(vals, api=api, status=status)

    @api.model
    def create(self, vals):
        self = super(Applicant, self).create(vals)
        cmplify_application = False
        if 'cmplify_application' in vals.keys():
            cmplify_application = vals.get('cmplify_application', False)
        else:
            cmplify_application = self.cmplify_application
        if cmplify_application:
            if vals.get("description", False) and self.is_form_fill:
                raise UserError("Please clear the form before entering the description.")
            """Job Application Id auto sequence part"""
            if vals.get('company_id', False):
                vals['application_id'] = self.env['ir.sequence'].with_context(
                    force_company=self.env.user.company_id.id).next_by_code('hr.applicant') or _('New')
            else:
                vals['application_id'] = self.env['ir.sequence'].next_by_code('hr.applicant') or _('New')
            job_position = None
            if vals.get('job_id', False):
                job_position = self.env['hr.job'].browse(vals['job_id'])

            self.job_application_creation(vals=vals, call='post')
        return self

    @api.multi
    def write(self, vals):
        rec = super(Applicant, self).write(vals)
        if vals.get('stage_id', False):
            stage_rec = self.env['hr.recruitment.stage'].browse(vals['stage_id'])
            if stage_rec and stage_rec.code == 'SL':
                self.shortlisted_date = self.write_date
        if 'cmplify_application' in vals.keys():
            cmplify_application = vals.get('cmplify_application', False)
        else:
            cmplify_application = self.cmplify_application
        if cmplify_application:
            if vals.get("description", False) and self.is_form_fill:
                raise UserError("Please clear the form before entering the description.")
            if self.env.context.get('skip_updation', False):
                return super(Applicant, self).write(vals)
            job_position = None
            if vals.get('job_id', False):
                job_position = self.env['hr.job'].browse(vals['job_id'])
            elif self.job_id:
                job_position = self.job_id

            if not self.job_application_id and job_position:
                self.job_application_creation(vals)
                return super(Applicant, self).write(vals)
            if self.job_application_id and job_position:
                self.with_context(skip_updation=True).job_application_updation(vals, call='put')
        return rec

    @api.multi
    def action_reset_application_form(self):
        if self.cmplify_application:
            if self.analytic_status == 'IN_PROGRESS':
                raise UserError("You cannot reset the form while processing.")

            if self.job_id:
                job_position = self.job_id.job_position_id
                job_application_id = self.job_application_id
                data = {
                    "application_certifications": [],
                    "application_education": [],
                    "application_employment": [],
                    "total_exp": '',
                    "application_skills": [],
                    # "application_objective": []
                }
                token = self.account_token()
                if token:
                    api, status = self.env['api.request'].job_application_iap(data, token, call='put', job_position_id=job_position, job_application_id=job_application_id, reset=1)
                    vals = {}
                    self.api_status_check(vals, api, status)
                    self.with_context(skip_updation=True).write({
                        "certifications": [(3, rec, None) for rec in self.certifications.ids] if self.certifications else None,
                        "skills": [(3, rec, None) for rec in self.skills.ids] if self.skills else None,
                        "total_exp": None,
                        "report_objective": None,
                        "email_from": None,
                        "partner_phone": None,
                        "educational_details": [(2, rec, None) for rec in self.educational_details.ids] if self.educational_details else None,
                        "employment_details": [(2, rec, None) for rec in self.employment_details.ids] if self.employment_details else None,
                    })

    @api.multi
    def refresh_request(self):
        if self.cmplify_application:
            customer_id = self.fetch_customer_id()
            document_attach = self.env['ir.attachment'].search([('res_model', '=', 'hr.applicant'), ('res_id', '=', self.id)])
            api = {}
            if self.analytic_status == 'IN_PROGRESS':
                job_application_id = self.job_application_id
                job_position = self.job_id.job_position_id
                data = {
                    "cust_id": customer_id or None,
                    "org_application_id": job_application_id,
                }

                token = self.account_token()
                if job_application_id and token:
                    type = ''
                    if self.description:
                        type = 'description'
                    elif document_attach:
                        type = 'document'
                    api, status = self.env['api.request'].job_application_iap(data, token, job_position_id=job_position, job_application_id=job_application_id, call='get', type=type)
                if api in [200, 201]:
                    certification_id = []
                    if status['parameters'] and status['parameters']['application_certifications']:
                        for certi in status['parameters']['application_certifications']:
                            certifi_id = self.env['certificate.details'].search([('name', '=ilike', certi)])
                            if certifi_id:
                                certification_id.append(certifi_id.id)
                            else:
                                certifi_id = self.env['certificate.details'].create({'name': certi})
                                certification_id.append(certifi_id.id)
                    skill_rec = []
                    if status['parameters'] and status['parameters']['application_skills']:
                        for skill in status['parameters']['application_skills']:
                            skill_id = self.env['skill.details'].search([('name', '=ilike', skill)], limit=1)
                            if skill_id:
                                skill_rec.append(skill_id.id)
                            else:
                                skill_id = self.env['skill.details'].create({'name': skill})
                                skill_rec.append(skill_id.id)
                    total_exp = 0
                    if status['parameters'] and status['parameters']['total_exp']:
                        total_exp = status['parameters']['total_exp']
                    objective = ''
                    if status['parameters'] and status['parameters']['application_objective']:
                        objective = status['parameters']['application_objective']
                    education = []
                    if status['parameters'] and status['parameters']['application_education']:
                        for edu in status['parameters']['application_education']:
                            start_date = False
                            end_date = False
                            if edu['start_date'] == 'None':
                                start_date = False
                            else:
                                start_date = edu['start_date']
                            if edu['end_date'] == 'None':
                                end_date = False
                            else:
                                end_date = edu['end_date']
                            degree_id = None
                            if edu['degree_type']:
                                degree_type = self.env['qualification.details'].search(
                                    [('name', '=ilike', edu['degree_type'])])
                                if degree_type:
                                    degree_id = degree_type[0].id
                                else:
                                    degree_type = self.env['qualification.details'].create({'name': edu['degree_type']})
                                    degree_id = degree_type.id
                            degree_name_id = None
                            if edu['degree_name']:
                                degree_name = self.env['qual.name'].search(
                                    [('name', '=ilike', edu['degree_name'])])
                                if degree_name:
                                    degree_name_id = degree_name[0].id
                                else:
                                    degree_name = self.env['qual.name'].create(
                                        {'name': edu['degree_type'], 'company_id': self.env.user.company_id.id})
                                    degree_name_id = degree_name.id
                            degree_major_id = None
                            if edu['degree_major']:
                                degree_major = self.env['qual.major'].search(
                                    [('name', '=ilike', edu['degree_major'])])
                                if degree_major:
                                    degree_major_id = degree_major.id
                                else:
                                    degree_major = self.env['qual.major'].create(
                                        {'name': edu['degree_major'], 'company_id': self.env.user.company_id.id})
                                    degree_major_id = degree_major.id

                            vals = {
                                # 'name': ,
                                'type_id': degree_id if degree_id else None,
                                'qual_name': degree_name_id if degree_name_id else None,
                                'qual_major': degree_major_id if degree_major_id else None,
                                'start_date': start_date,
                                'end_date': end_date,
                                'school_name': edu['school_name'],
                                'school_university': edu['school_type'],
                                'educational_ref': self.id
                            }
                            education_details = self.env['educational.details'].create(vals)
                            education.append(education_details)
                    employment = []
                    if status['parameters'] and status['parameters']['application_employment']:
                        for empl in status['parameters']['application_employment']:
                            start_date = False
                            end_date = False
                            description = ''
                            if empl['start_date'] == 'None':
                                start_date = False
                            else:
                                start_date = empl['start_date']
                            if empl['end_date'] == 'None':
                                end_date = False
                            else:
                                end_date = empl['end_date']
                            if empl['employment_description']:
                                description = empl['employment_description']
                            vals = {
                                'position': empl['position_title'] if empl['position_title'] else '',
                                'name': empl['employer_org_name'] if empl['employer_org_name'] else '',
                                'start_date': start_date,
                                'end_date': end_date,
                                'employment_ref': self.id,
                                'description': description
                            }
                            employment_details = self.env['employment.details'].create(vals)
                            employment.append(employment_details)

                    self.with_context(skip_description=True).write({
                        "certifications": [(4, rec, None) for rec in certification_id] if certification_id else None,
                        "skills": [(4, rec, None) for rec in skill_rec] if skill_rec else None,
                        "total_exp": str(int(total_exp)),
                        "report_objective": objective,
                        "partner_phone": status['parameters']['application_contact'] if status['parameters']['application_contact'] else '',
                        "email_from": status['parameters']['application_emailid'] if status['parameters']['application_emailid'] else '',
                        "educational_details": education,
                        "employment_details": employment,
                        "analytic_status": status['status'],
                        "response_status": status['message'],
                    })


    @api.multi
    def refresh_request_cron(self):
        job_application = self.env['hr.applicant'].search([('analytic_status', '=', 'IN_PROGRESS')])
        if job_application:
            for rec in job_application:
                rec.response_status = ''
                if rec.job_id and rec.active:
                    rec.refresh_request()

    @api.multi
    def toggle_active(self):
        self = self.with_context(skip_updation=True)
        super(Applicant, self).toggle_active()

    @api.multi
    def unlink(self):
        for application in self:
            token = self.account_token()
            if token:
                job_position = ''
                job_application = ''
                if application:
                    application.active = False
                    if application.job_id and application.job_id.job_position_id:
                        job_position = application.job_id.job_position_id
                    if application.job_application_id:
                        job_application = application.job_application_id
                    api, status = self.env['api.request'].delete_iap(token, job_position_id=job_position,
                                                                              job_application_id=job_application,
                                                                              call='delete', model='hr_applicant')
                    # api = self.env['api.request'].delete_request('delete', job_position, job_application)

    @api.multi
    def create_employee_from_applicant(self):
        self = self.with_context(skip_updation=True)
        super(Applicant, self).create_employee_from_applicant()

    @api.multi
    def archive_applicant(self):
        self = self.with_context(skip_updation=True)
        super(Applicant, self).archive_applicant()

    @api.multi
    def reset_applicant(self):
        self = self.with_context(skip_updation=True)
        super(Applicant, self).reset_applicant()

class EmploymentDetails(models.Model):
    _name = "employment.details"

    name = fields.Char('Company Name')
    position = fields.Char('Position')
    start_date = fields.Date('Start Date')
    end_date = fields.Date('End Date')
    employment_ref = fields.Many2one('hr.applicant', 'Employment Ref')
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.user.company_id)
    description = fields.Text('Description')

class EducationalDetails(models.Model):
    _name = "educational.details"

    name = fields.Char('Name')
    type_id = fields.Many2one('qualification.details', 'Degree')
    qual_name = fields.Many2one('qual.name', 'Qualification Name')
    qual_major = fields.Many2one('qual.major', 'Qualification Major')
    start_date = fields.Date('Start Date')
    end_date = fields.Date('End Date')
    school_name = fields.Char('School Type')
    school_university = fields.Char('School University')
    educational_ref = fields.Many2one('hr.applicant', 'Educational Ref')
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.user.company_id)

class QualName(models.Model):
    _name = "qual.name"

    name = fields.Char("Name")
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.user.company_id)

class QualMajor(models.Model):
    _name = "qual.major"

    name = fields.Char("Name")
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.user.company_id)
