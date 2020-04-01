# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.addons.iap import jsonrpc, InsufficientCreditError
import base64

class ApiRequest(models.Model):
	_name = "api.request"

	company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.user.company_id)

	"""Connecting with Bridge Server"""
	@api.multi
	def get_customer_id(self):
		if self.env.user and self.env.user.company_id:
			customer_id = self.env.user.company_id.customer_id
			host_name = self.env.user.company_id.ras_bridge_host
			client_id = self.env.user.company_id.client_id
			api_key = self.env.user.company_id.api_key_id
			return customer_id, host_name, client_id, api_key

	@api.multi
	def skill_suggestion_iap(self, token='', name='', job_position_id='', call=''):
		customer_id, host_name, client_id, api_key = self.get_customer_id()
		params = {
			'account_token': token.account_token,
			'call': call,
			'name': name,
			'customer_id': customer_id,
			'job_position_id': job_position_id,
			'client_id': client_id,
			'api_key': api_key
		}
		# endpoint = self.env['ir.config_parameter'].sudo().get_param('recruitment_credit.endpoint', host_name)
		endpoint = self.env.user.company_id.ras_bridge_host
		url = endpoint + "/" + "skill_fetch_credit"
		json_response, status = jsonrpc(url, params=params)
		return json_response, status

	@api.multi
	def model_fetch_iap(self, token='', name='', job_position_id='', call=''):
		customer_id, host_name, client_id, api_key = self.get_customer_id()
		params = {
			'account_token': token.account_token,
			'call': call,
			'name': name,
			'customer_id': customer_id,
			'job_position_id': job_position_id,
			'client_id': client_id,
			'api_key': api_key
		}
		# endpoint = self.env['ir.config_parameter'].sudo().get_param('recruitment_credit.endpoint', host_name)
		endpoint = self.env.user.company_id.ras_bridge_host
		url = endpoint + "/" + "model_fetch_credit"
		json_response, status = jsonrpc(url, params=params)
		return json_response, status

	@api.multi
	def document_parser_iap(self, token, job_position_id = '', job_application_id='', binary_doc='', doc_name='', call='', model=''):
		if binary_doc:
			binary_to_string = base64.b64encode(binary_doc).decode('utf-8')
		customer_id, host_name, client_id, api_key = self.get_customer_id()
		params = {
			'account_token': token.account_token,
			'call': call,
			'binary_doc': binary_to_string,
			'doc_name': doc_name,
			'customer_id': customer_id,
			'model': model,
			'job_position_id': job_position_id,
			'job_application_id': job_application_id,
			'client_id': client_id,
			'api_key': api_key
		}
		# endpoint = self.env['ir.config_parameter'].sudo().get_param('recruitment_credit.endpoint', host_name)
		endpoint = self.env.user.company_id.ras_bridge_host
		url = endpoint + "/" + "document_parsing_credit"
		json_response, status = jsonrpc(url, params=params)
		return json_response, status

	@api.multi
	def description_parser_iap(self, token, document_description='', job_position_id='', job_application_id='', call='', model=''):
		customer_id, host_name, client_id, api_key = self.get_customer_id()
		params = {
			'account_token': token.account_token,
			'call': call,
			'document_description': document_description,
			'job_position_id': job_position_id,
			'job_application_id': job_application_id,
			'customer_id': customer_id,
			'model': model,
			'client_id': client_id,
			'api_key': api_key
		}
		# endpoint = self.env['ir.config_parameter'].sudo().get_param('recruitment_credit.endpoint', host_name)
		endpoint = self.env.user.company_id.ras_bridge_host
		url = endpoint + "/" + "description_parsing_credit"
		json_response, status = jsonrpc(url, params=params)
		return json_response, status

	@api.multi
	def job_position_iap(self, data={}, token='', job_position_id='', call='', reset=0, type=''):
		response = {}
		customer_id, host_name, client_id, api_key = self.get_customer_id()
		params = {
			'account_token': token.account_token,
			'data': data,
			'customer_id': customer_id,
			'call': call,
			'job_position_id': job_position_id,
			'reset': reset,
			'type': type,
			'client_id': client_id,
			'api_key': api_key
		}
		# endpoint = self.env['ir.config_parameter'].sudo().get_param('recruitment_credit.endpoint', host_name)
		endpoint = self.env.user.company_id.ras_bridge_host
		url = endpoint + "/job_position_credit"
		json_response, status = jsonrpc(url, params=params)
		return json_response, status

	@api.multi
	def job_application_iap(self, data={}, token='', job_position_id='', job_application_id='', call='', reset=0, type=''):
		response = {}
		customer_id, host_name, client_id, api_key = self.get_customer_id()
		params = {
			'account_token': token.account_token,
			'data': data,
			'customer_id': customer_id,
			'call': call,
			'job_position_id': job_position_id,
			'reset': reset,
			'type': type,
			'job_application_id': job_application_id,
			'client_id': client_id,
			'api_key': api_key
		}
		# endpoint = self.env['ir.config_parameter'].sudo().get_param('recruitment_credit.endpoint', host_name)
		endpoint = self.env.user.company_id.ras_bridge_host
		url = endpoint + "/job_application_credit"
		json_response, status = jsonrpc(url, params=params)
		return json_response, status

	@api.multi
	def match_analytic_iap(self, data={}, token='', job_position_id='', match_analytic_id='', call=''):
		response = {}
		customer_id, host_name, client_id, api_key = self.get_customer_id()
		params = {
			'account_token': token.account_token,
			'data': data,
			'customer_id': customer_id,
			'call': call,
			'job_position_id': job_position_id,
			'match_analytic_id': match_analytic_id,
			'client_id': client_id,
			'api_key': api_key
		}
		# endpoint = self.env['ir.config_parameter'].sudo().get_param('recruitment_credit.endpoint', host_name)
		endpoint = self.env.user.company_id.ras_bridge_host
		url = endpoint + "/match_analytic_credit"
		json_response, status = jsonrpc(url, params=params)
		return json_response, status

	@api.multi
	def send_mail_iap(self, token=''):
		customer_id, host_name, client_id, api_key = self.get_customer_id()
		params = {
			'account_token': token.account_token,
			'customer_id': customer_id,
			'client_id': client_id,
			'api_key': api_key
		}
		# endpoint = self.env['ir.config_parameter'].sudo().get_param('recruitment_credit.endpoint')
		endpoint = self.env.user.company_id.ras_bridge_host
		url = endpoint + "/mail_send_credit"
		jsonrpc(url, params=params)
		return True

	@api.multi
	def delete_iap(self, token='', job_position_id='', job_application_id='', match_analytic_id='', call='', model=''):
		response = {}
		customer_id, host_name, client_id, api_key = self.get_customer_id()
		params = {
			'account_token': token.account_token,
			'customer_id': customer_id,
			'call': call,
			'job_position_id': job_position_id,
			'job_application_id': job_application_id,
			'match_analytic_id': match_analytic_id,
			'client_id': client_id,
			'api_key': api_key,
			'model': model
		}
		# endpoint = self.env['ir.config_parameter'].sudo().get_param('recruitment_credit.endpoint', host_name)
		endpoint = self.env.user.company_id.ras_bridge_host
		url = endpoint + "/delete_credit"
		json_response, status = jsonrpc(url, params=params)
		return json_response, status