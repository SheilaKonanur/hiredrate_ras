# -*- coding: utf-8 -*-
from odoo import fields, models, api

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    cmplify_dts = fields.Boolean('HIREdrate DTS', related='company_id.cmplify_dts', default=True, readonly=False)
    dts_bridge_host = fields.Char('Host', related='company_id.dts_bridge_host', readonly=False)

class TemplateCategory(models.Model):
    _name = 'template.category'

    name = fields.Char('Name')
    code = fields.Integer('Id', readonly=True)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.user.company_id)


class AddSections(models.Model):
    _name = 'add.sections'
    _order = 'sequence'

    # name = fields.Char('Label Name')
    model_id = fields.Many2one('ir.model', 'Model')
    ir_fields = fields.Many2one('ir.model.fields', 'Fields')
    styling = fields.Selection([('comma_separated', 'Comma Separated Values'), ('edu_list', 'Educational List'),
                                ('emp_list', 'Employment List'), ('list', 'List'), ('para', 'Paragraph')],
                               default='list', string='Styling')
    section_id = fields.Many2one('template.settings', 'Section Id')
    list_id = fields.Many2one('template.list', 'List Id')
    is_optional = fields.Boolean('Is Optional')
    sequence = fields.Integer('Sequence')

    @api.model
    def default_get(self, fields):
        res = super(AddSections, self).default_get(fields)
        model_id = self.env['ir.model'].search([('model', '=', 'hr.applicant')], limit=1)
        res.update({
            'model_id': model_id.id
        })
        return res


class TemplateSettings(models.Model):
    _name = 'template.settings'

    name = fields.Char('Name')
    template_category = fields.Many2one("template.category", "Category")
    base_template_id = fields.Many2one("template.list", "Base Template")
    template_id = fields.Many2one('template.list', 'Template')
    # template_class = fields.Many2one("template.class", "Template Class")
    # doc_filename = fields.Char('File Name', readonly=False)
    # doc_filedata = fields.Binary('File', readonly=False)
    upload_filename = fields.Char('File Name')
    upload_filedata = fields.Binary('Upload Template')
    add_sections = fields.One2many('add.sections', 'section_id', 'Add Sections')
    is_template = fields.Boolean('Is Template?')
    # is_new = fields.Boolean("Is New", default=False)
    logo = fields.Binary(string="Logo")
    street = fields.Char()
    street2 = fields.Char()
    zip = fields.Char()
    city = fields.Char()
    state_id = fields.Many2one('res.country.state', string="Fed. State")
    country_id = fields.Many2one('res.country', string="Country")
    phone = fields.Char(string="Phone")
    mobile = fields.Char(string="Mobile")
    website = fields.Char(string="Website")
    user_id = fields.Many2one('res.users', string='User', default=lambda self: self.env.uid)
    base_preview = fields.Char('Preview', default="Preview")
    preview_image = fields.Binary(string="Logo", attachment=True)
    format_type = fields.Selection([('docx', 'Document'), ('pdf', 'PDF')], default='pdf', string='Format Type')

    @api.multi
    def account_token(self):
        user_token = self.env['iap.account'].get('analytic_service')
        return user_token

    @api.model
    def default_get(self, fields):
        res = super(TemplateSettings, self).default_get(fields)
        token = self.account_token()
        if token:
            category_api, category_status = self.env['template.request'].template_service_iap(token=token, call='get', type='category')

            if category_api in [200, 201]:
                # category_api = category_api.json()
                if category_status['Available_categories']:
                    for categ in category_status['Available_categories']:
                        if categ['id']:
                            categories_id = self.env['template.category'].search([('code', '=', categ['id'])])
                            if not categories_id:
                                vals = {
                                    'name': categ['name'],
                                    'code': categ['id'],
                                }
                                categories_id = self.env['template.category'].create(vals)
            template_api, template_status = self.env['template.request'].template_service_iap(token=token, call='get', type='templates')

            if template_api in [200, 201]:
                template_category = ''
                if template_status['parameters'] and template_status['parameters']['Available_templates']:
                    for line in template_status['parameters']['Available_templates']:
                        template_category = self.env['template.category'].search([('code', '=', int(line['category_id']))])
                        if line['id']:
                            template_list = self.env['template.list'].search([('code', '=', line['id'])], limit=1)
                            if not template_list:
                                vals = {
                                    'name': line['name'],
                                    'code': line['id'],
                                    'company_id': self.env.user.company_id.id,
                                    'template_category': template_category.id or None
                                }
                                template_list = self.env['template.list'].create(vals)
            logo = False
            street = False
            street2 = False
            zip = False
            city = False
            state_id = False
            country_id = False
            phone = False
            mobile = False
            website = False
            if self.env.user.partner_id.parent_id and self.env.user.partner_id.parent_id.image:
                logo = self.env.user.partner_id.parent_id.image
            if self.env.user.partner_id.parent_id and self.env.user.partner_id.parent_id.street:
                street = self.env.user.partner_id.parent_id.street
            if self.env.user.partner_id.parent_id and self.env.user.partner_id.parent_id.street2:
                street2 = self.env.user.partner_id.parent_id.street2
            if self.env.user.partner_id.parent_id and self.env.user.partner_id.parent_id.zip:
                zip = self.env.user.partner_id.parent_id.zip
            if self.env.user.partner_id.parent_id and self.env.user.partner_id.parent_id.city:
                city = self.env.user.partner_id.parent_id.city
            if self.env.user.partner_id.parent_id and self.env.user.partner_id.parent_id.state_id:
                state_id = self.env.user.partner_id.parent_id.state_id
            if self.env.user.partner_id.parent_id and self.env.user.partner_id.parent_id.country_id:
                country_id = self.env.user.partner_id.parent_id.country_id
            if self.env.user.partner_id.parent_id and self.env.user.partner_id.parent_id.phone:
                phone = self.env.user.partner_id.parent_id.phone
            if self.env.user.partner_id.parent_id and self.env.user.partner_id.parent_id.mobile:
                mobile = self.env.user.partner_id.parent_id.mobile
            if self.env.user.partner_id.parent_id and self.env.user.partner_id.parent_id.website:
                website = self.env.user.partner_id.parent_id.website
            res.update({
                'logo': logo,
                'street': street if street else '',
                'street2': street2 if street2 else '',
                'zip': zip if zip else '',
                'city': city if city else '',
                'state_id': state_id.id if state_id else '',
                'country_id': country_id.id if country_id else '',
                'phone': phone if phone else '',
                'mobile': mobile if mobile else '',
                'website': website if website else '',
            })
            return res

    @api.onchange('template_category')
    def _onchange_template_category(self):
        self.base_template_id = None
        if self.template_category and self.template_category.code:
            category_code = self.template_category.code
            token = self.account_token()
            if token:
                template_api, template_status = self.env['template.request'].template_service_iap(token=token, call='get', category_code=category_code)
                template_code = []
                if template_api in [200, 201]:
                    template_category = ''
                    if template_status['status'] == 'COMPLETE' and template_status['templates'] and template_status['templates']:
                        for temp in template_status['templates']:
                            for line in temp['available_template']:
                                template_category = self.env['template.category'].search(
                                    [('code', '=', int(line['category_id']))])
                                template_list = self.env['template.list'].search([('code', '=', line['id'])], limit=1)
                                if template_list:
                                    template_code.append(template_list.code)
                                else:
                                    vals = {
                                        'name': line['name'],
                                        'code': line['id'],
                                        'company_id': self.env.user.company_id.id,
                                        'template_category': template_category.id or None
                                    }
                                    template_list = self.env['template.list'].create(vals)
                                    template_code.append(template_list.code)

    @api.onchange('base_template_id')
    def _onchange_base_template_id(self):
        self.upload_filedata = False
        self.upload_filename = False
        self.add_sections = False

        if self.base_template_id:
            """Image Preview"""
            image_template_code = self.base_template_id.code
            token = self.account_token()
            if token:
                api_image, api_image_status = self.env['template.request'].template_service_iap(token=token, call='get', template_code=image_template_code, preview=True)
                if api_image in [200, 201]:
                    if api_image_status.get('preview_image', False):
                        image = api_image_status['preview_image'].encode()
                        self.preview_image = image

                new_template = self.env.ref('match_analytic.new_template_creation', False)
                template_code = self.base_template_id.code
                api, api_status = self.env['template.request'].template_service_iap(token=token, call='get', template_code=image_template_code)
                section_ids = []
                if api in [200, 201]:
                    if api_status.get('sections', False):
                        if self.add_sections:
                            for sect in self.add_sections:
                                sect.unlink()
                        model_name = 'hr.applicant'
                        for line in api_status['sections']:
                            if line['name'].lower() == 'summary':
                                field_name = 'report_objective'
                                style = line['showAs'].lower()
                                optional = line['optional']
                                sequence = line['sequence']
                                model_id, ir_model_field, style, optional_value = self._get_section_details(model_name, field_name, style, optional)
                                vals = {
                                    'model_id': model_id.id,
                                    'ir_fields': ir_model_field.id,
                                    'styling': style,
                                    'section_id': self.id,
                                    'is_optional': optional_value,
                                    'sequence': sequence
                                }
                                section_id = self.env['add.sections'].create(vals)
                                section_ids.append(section_id)
                            elif line['name'].lower() == 'education':
                                field_name = 'educational_details'
                                style = line['showAs'].lower()
                                optional = line['optional']
                                sequence = line['sequence']
                                model_id, ir_model_field, style, optional_value = self._get_section_details(model_name, field_name, style, optional)
                                vals = {
                                    'model_id': model_id.id,
                                    'ir_fields': ir_model_field.id,
                                    'styling': style,
                                    'section_id': self.id,
                                    'is_optional': optional_value,
                                    'sequence': sequence
                                }
                                section_id = self.env['add.sections'].create(vals)
                                section_ids.append(section_id)

                            elif line['name'].lower() == 'skills':
                                field_name = 'skills'
                                style = line['showAs'].lower()
                                optional = line['optional']
                                sequence = line['sequence']
                                model_id, ir_model_field, style, optional_value = self._get_section_details(model_name, field_name, style, optional)
                                vals = {
                                    'model_id': model_id.id,
                                    'ir_fields': ir_model_field.id,
                                    'styling': style,
                                    'section_id': self.id,
                                    'is_optional': optional_value,
                                    'sequence': sequence
                                }
                                section_id = self.env['add.sections'].create(vals)
                                section_ids.append(section_id)

                            elif line['name'].lower() == 'employment':
                                field_name = 'employment_details'
                                style = line['showAs'].lower()
                                optional = line['optional']
                                sequence = line['sequence']
                                model_id, ir_model_field, style, optional_value = self._get_section_details(model_name, field_name, style, optional)
                                vals = {
                                    'model_id': model_id.id,
                                    'ir_fields': ir_model_field.id,
                                    'styling': style,
                                    'section_id': self.id,
                                    'is_optional': optional_value,
                                    'sequence': sequence
                                }
                                section_id = self.env['add.sections'].create(vals)
                                section_ids.append(section_id)

                            elif line['name'].lower() == 'certifications':
                                field_name = 'certifications'
                                style = line['showAs'].lower()
                                optional = line['optional']
                                sequence = line['sequence']
                                model_id, ir_model_field, style, optional_value = self._get_section_details(model_name, field_name, style, optional)
                                vals = {
                                    'model_id': model_id.id,
                                    'ir_fields': ir_model_field.id,
                                    'styling': style,
                                    'section_id': self.id,
                                    'is_optional': optional_value,
                                    'sequence': sequence
                                }
                                section_id = self.env['add.sections'].create(vals)
                                section_ids.append(section_id)

                if section_ids:
                    self.add_sections = [(4, rec.id, None) for rec in section_ids]

    @api.model
    def create(self, vals):
        res = super(TemplateSettings, self).create(vals)
        if res:
            category = ''
            if res.template_category:
                category = res.template_category.code
            elif res.base_template_id:
                category = res.base_template_id.template_category.code
            template = ''
            if res.base_template_id:
                template = res.base_template_id.code
            sections = []
            if res.add_sections:
                for line in res.add_sections:
                    style = ''
                    if line.styling == 'comma_separated':
                        style = 'csv'
                    elif line.styling == 'edu_list':
                        style = 'custom_edu_list'
                    elif line.styling == 'emp_list':
                        style = 'custom_emp_list'
                    elif line.styling == 'list':
                        style = 'list'
                    elif line.styling == 'para':
                        style = 'p'
                    name = ''
                    if line.ir_fields and line.ir_fields.field_description.lower() == 'objective':
                        name = 'SUMMARY'
                    elif line.ir_fields and line.ir_fields.field_description.lower() == 'skills':
                        name = 'SKILLS'
                    elif line.ir_fields and line.ir_fields.field_description.lower() == 'educational details':
                        name = 'EDUCATION'
                    elif line.ir_fields and line.ir_fields.field_description.lower() == 'employment details':
                        name = 'EMPLOYMENT'
                    else:
                        name = line.ir_fields.field_description

                    vals = {
                        "name": name,
                        "showAs": style,
                        "optional": line.is_optional,
                        "sequence": line.sequence
                    }
                    sections.append(vals)

            logo = ''
            if res.logo:
                logo = res.logo.decode()
            org_address_line1 = ''
            org_address_line2 = ''
            org_contact = ''
            org_website = ''
            if res.street:
                org_address_line1 += res.street
            if res.street2:
                org_address_line1 += " " + res.street2
            if res.city:
                org_address_line2 += res.city
            if res.state_id:
                org_address_line2 += " " + res.state_id.name
            if res.country_id:
                org_address_line2 += " " + res.country_id.name
            if res.zip:
                org_address_line2 += " " + res.zip
            if res.phone:
                org_contact = res.phone
            elif res.mobile:
                org_contact = res.mobile
            if res.website:
                org_website = res.website
            address = {
                "org_address_line1": org_address_line1,
                "org_address_line2": org_address_line2,
                "org_contact": org_contact,
                "org_website": org_website
            }
            header = {
                "company_logo": logo,
                "address": address
            }
            format_type = False
            if res.format_type:
                format_type = res.format_type
            data = {
                "category_id": category,
                "template_id": template,
                "new_template_name": res.name,
                "sections_formats": sections,
                "header": header,
                "file_type": format_type
            }
            token = self.account_token()
            if token:
                api, api_status = self.env['template.request'].template_service_iap(token=token, call='post', data=data)
                if api in [200, 201]:
                    if api_status['parameters'] and api_status['parameters']['template_id']:
                        name = ''
                        if api_status['parameters']['template_name']:
                            name = api_status['parameters']['template_name']
                        template_category = None
                        if api_status['parameters']['category_id']:
                            template_category = self.env['template.category'].search([('code', '=', int(api_status['parameters']['category_id']))])
                        vals = {
                            'name': name,
                            'code': int(api_status['parameters']['template_id']),
                            'template_category': template_category.id,
                            'is_base_template': False,
                            'company_id': self.env.user.company_id.id
                        }
                        if vals:
                            template_id = self.env['template.list'].create(vals)
                            res.template_id = template_id.id
        return res

    @api.model
    def _get_section_details(self, model_name='', field_name='', style='', optional_value=False):
        model_id = ''
        ir_model_field = ''
        if model_name:
            model_id = self.env['ir.model'].search([('model', '=', model_name)], limit=1)
        if field_name:
            ir_model_field = self.env['ir.model.fields'].search([('name', '=', field_name)], limit=1)
        format = ''
        if style:
            if style == 'list':
                format = 'list'
            elif style == 'csv':
                format = 'comma_separated'
            elif style == 'custom_edu_list':
                format = 'edu_list'
            elif style == 'custom_emp_list':
                format = 'emp_list'
            elif style == 'p':
                format = 'para'

        return model_id, ir_model_field, format, optional_value

    @api.multi
    def compute_print_preview(self):
        template = self.base_template_id.code
        action = self.env.ref('hiredrate_dts.action_print_wizard')
        result = {
            'name': action.name,
            'help': action.help,
            'type': action.type,
            'view_type': action.view_type,
            'view_mode': action.view_mode,
            'target': action.target,
            'context': {'default_template_settings': self.id if self else False},
            'res_model': action.res_model,
        }
        return result

class TemplateList(models.Model):
    _name = "template.list"

    name = fields.Char('Name')
    code = fields.Integer('Id', readonly=True)
    template_category = fields.Many2one('template.category', 'Template Category')
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.user.company_id, readonly=True)
    is_base_template = fields.Boolean('Is Tempalte')