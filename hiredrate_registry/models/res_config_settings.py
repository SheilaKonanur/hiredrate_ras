# -*- coding: utf-8 -*-
from odoo import fields, models, api
import requests
from openerp.exceptions import UserError
from odoo.addons.iap import jsonrpc, InsufficientCreditError
import json

class ResConfigSettings(models.TransientModel):
	_inherit = 'res.config.settings'

	api_key_id = fields.Char('Api Key', related='company_id.api_key_id', readonly=False)
	client_id = fields.Char('Client Id', related='company_id.client_id', readonly=False)
	customer_id = fields.Char('Customer Id', related='company_id.customer_id', readonly=False)
	customer_host = fields.Char('Host', related='company_id.customer_host', readonly=False)
	cmplify_company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.user.company_id.id)

	@api.multi
	def link_existing_company(self):
		if not self.customer_id and self.cmplify_company_id:
			# data = {}
			location = ''
			if self.cmplify_company_id.street:
				location += self.cmplify_company_id.street
			if self.cmplify_company_id.street2:
				location += ','
				location += self.cmplify_company_id.street2
			if self.cmplify_company_id.city:
				location += ','
				location += self.cmplify_company_id.city
			if self.cmplify_company_id.state_id:
				location += ','
				location += self.cmplify_company_id.state_id.name
			if self.cmplify_company_id.country_id:
				location += ','
				location += self.cmplify_company_id.country_id.name
			data = {
				"sso_name": self.cmplify_company_id.name,
				"legal_name": self.cmplify_company_id.name,
				"location": location,
				"email": self.cmplify_company_id.email,
				"contact_name": self.cmplify_company_id.name,
				"contact_no": self.cmplify_company_id.phone
			}
			endpoint = self.env.user.company_id.customer_host
			if not endpoint:
				raise UserError("Please configure company host in HIREdrate Settings!")
			sso_url = endpoint + "/customer_creation_credit"
			if data:
				params = {
					'data': data,
					'call': 'post',
					'currency': self.env.user.company_id.currency_id.name
				}
				headers = {'Content-type': 'application/json', 'Accept': 'application/json'}
				response, status_code = jsonrpc(sso_url, params=params)
				if response in [200, 201]:
					if status_code and status_code.get('customer_information', False) and 'id' in status_code['customer_information'].keys():
						update_url = endpoint + '/customer_key_creation'
						key_vals = {
							"name": status_code['customer_information']['sso_name'],
							"note": ""
						}
						if key_vals:
							param_data = {
							'data': key_vals,
							'customer_id': status_code['customer_information']['id'],
							'call': 'post'
							}
							api_response, api_status_code = jsonrpc(update_url, params=param_data)
							if api_response in [200, 201]:
								if api_status_code and api_status_code.get('customer_key_information', False) and 'client_id' in api_status_code['customer_key_information'] and 'key' in api_status_code['customer_key_information']:
									self.client_id = api_status_code['customer_key_information']['client_id']
									self.api_key_id = api_status_code['customer_key_information']['key']
									self.customer_id = api_status_code['customer_key_information']['sso_customer_id']
		else:
			raise UserError("Customer Id is already entered!")

	@api.multi
	def reset_api_key(self):
		if self.customer_id:
			update_url = sso_url + str(self.customer_id) + "/keys"
			key_vals = {
				"name": self.cmplify_company_id.name,
				"note": ""
			}
			if key_vals:
				key_vals = json.dumps(key_vals)
				headers = {'Content-type': 'application/json', 'Accept': 'application/json'}
				api_response = requests.post(update_url, key_vals, headers=headers)
				if api_response.status_code in [200, 201]:
					api_key = api_response.json()
					if api_key and api_key.get('customer_key_information', False) and 'client_id' in api_key[
						'customer_key_information'] and 'key' in api_key['customer_key_information']:
						self.client_id = api_key['customer_key_information']['client_id']
						self.api_key_id = api_key['customer_key_information']['key']
						self.customer_id = api_key['customer_key_information']['sso_customer_id']