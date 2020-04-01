# -*- coding: utf-8 -*-

from odoo import models, fields, api
import json
from openerp.exceptions import UserError
import requests
from odoo.addons.iap import jsonrpc, InsufficientCreditError

class TemplateRequest(models.Model):
	_name = "template.request"

	@api.multi
	def get_template_name(self, request, list_categories=False, list_templates=False, category_code=False, template_code=False, doc_generation=False, document_id=False, preview=False, data={}, job_position='', format_type=False):
		response = {}
		headers = {'Content-type': 'application/json', 'Accept': 'application/json'}
		# partner_id = self.env.user.partner_id
		customer_id = ''
		# if partner_id.parent_id and partner_id.parent_id.customer_id:
		# 	customer_id = partner_id.parent_id.customer_id
		if self.env.user.company_id and self.env.user.company_id.customer_id:
			customer_id = self.env.user.company_id.customer_id
		try:
			ras_connect, sso_connect, skill_url, model_url, template_connect, file_connect = self.url_credentials(
				job_position)
			if request == 'get' and list_categories:
				template_connect += "categories/"
				response = requests.get(template_connect, headers=headers)
			elif request == 'get' and list_templates and not category_code:
				template_connect += "customers/" + str(customer_id) + "/templates?base_templates=true"
				response = requests.get(template_connect)
			elif request == 'get' and list_templates and category_code:
				template_connect += "customers/" + str(customer_id) + "/templates" + "?categories=" + str(
					category_code) + "&base_templates=true"
				response = requests.get(template_connect)
			elif request == 'get' and template_code and not document_id and not preview:
				template_connect += "customers/" + str(customer_id) + "/templates/" + str(template_code)
				response = requests.get(template_connect, headers=headers)
			elif request == 'get' and template_code and document_id and not preview:
				if format_type == 'docx':
					template_connect += "customers/" + str(customer_id) + "/templates/" + str(
						template_code) + "/documents" + "/" + str(document_id)
				else:
					template_connect += "customers/" + str(customer_id) + "/templates/" + str(
						template_code) + "/documents" + "/" + str(document_id)
				response = requests.get(template_connect, headers=headers)
			elif request == 'get' and template_code and preview:
				template_connect += "customers/" + str(customer_id) + "/templates/" + str(template_code) + "/preview"
				response = requests.get(template_connect)
			elif request == 'post':
				if data:
					data = json.dumps(data)
					if not doc_generation:
						if format_type == 'docx':
							template_connect += "customers/" + str(customer_id) + "/templates"
						else:
							template_connect += "customers/" + str(customer_id) + "/templates"
						response = requests.post(template_connect, data, headers=headers)
					elif doc_generation:
						if format_type == 'docx':
							template_connect += "customers/" + str(customer_id) + "/templates" + "/" + str(
								template_code) + "/documents"
						else:
							template_connect += "customers/" + str(customer_id) + "/templates" + "/" + str(
								template_code) + "/documents"
						response = requests.post(template_connect, data, headers=headers)
			elif request == 'put':
				if data:
					data = json.dumps(data)
					template_connect += "customers/" + str(customer_id) + "/templates" + "/" + str(template_code)
					response = requests.put(template_connect, data, headers=headers)
		except:
			raise UserError("Failed to establish connection!")
		return response

	"""Connecting with Bridge Server"""

	@api.multi
	def get_customer_id(self):
		if self.env.user and self.env.user.company_id:
			# partner_id = self.env.user.company_id.partner_id
			# customer_id = partner_id.customer_id
			customer_id = self.env.user.company_id.customer_id
			host_name = self.env.user.company_id.dts_bridge_host
			client_id = self.env.user.company_id.client_id
			api_key = self.env.user.company_id.api_key_id
			return customer_id, host_name, client_id, api_key

	@api.multi
	def template_service_iap(self, token='', data={}, call='', type='', category_code='', template_code='', preview=False, doc_generation=False, document_id='', format_type=''):
		response = {}
		customer_id, host_name, client_id, api_key = self.get_customer_id()
		params = {
			'account_token': token.account_token,
			'data': data,
			'customer_id': customer_id,
			'call': call,
			'type': type,
			'category_code': category_code,
			'template_code': template_code,
			'preview': preview,
			'doc_generation': doc_generation,
			'document_id': document_id,
			'format_type': format_type,
			'client_id': client_id,
			'api_key': api_key
		}
		# endpoint = self.env['ir.config_parameter'].sudo().get_param('recruitment_credit.endpoint', host_name)
		endpoint = self.env.user.company_id.dts_bridge_host
		url = endpoint + "/template_service_credit"
		json_response, status = jsonrpc(url, params=params)
		return json_response, status