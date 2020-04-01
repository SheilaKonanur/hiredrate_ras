# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.addons.iap import jsonrpc, InsufficientCreditError
from odoo.exceptions import UserError

class ResCompany(models.Model):
	_inherit = "res.company"

	api_key_id = fields.Char('Api Key')
	client_id = fields.Char('Client Id')
	customer_id = fields.Char('Customer Id')
	customer_host = fields.Char('Customer Host', default="http://registry.hiredrate.com")

	@api.model
	def create(self, vals):
		res = super(ResCompany, self).create(vals)
		if res:
			name= ''
			if res.name:
				name = res.name.split()
			f_name = name[0]
			name.pop(0)
			l_name = " ".join(name)
			location = ''
			if res.street:
				location += res.street
			if res.street2:
				location += ','
				location += res.street2
			if res.city:
				location += ','
				location += res.city
			if res.state_id:
				location += ','
				location += res.state_id.name
			if res.country_id:
				location += ','
				location += res.country_id.name
			email = ''
			if res.email:
				email = res.email
			else:
				email = res.name
			contact_no = ''
			if res.phone:
				contact_no = res.phone
			state_id = ''
			if res.state_id:
				state_id = res.state_id.name
			country_id = ''
			if res.country_id:
				country_id = res.country_id.name
			currency_id = ''
			if res.currency_id:
				currency_id = res.currency_id.name
			company_id = {
				'name': res.name,
				'street': res.street,
				'street2': res.street2,
				'city': res.city,
				'state_id': state_id,
				'zip': res.zip,
				'country_id': country_id,
				'website': res.website,
				'phone': res.phone,
				'email': res.email,
				'currency_id': currency_id
			}

			data = {
				"sso_name": res.name,
				"legal_name": res.name,
				"location": location,
				"email": email,
				"contact_no": contact_no,
				"contact_name": res.name
					}
		params = {
				# 'account_token': token.account_token,
				'data': data,
				'call': 'post',
				'company_id': company_id
			}
		endpoint = self.env.user.company_id.customer_host
		if not endpoint:
			raise UserError("Please configure company host in HIREdrate Settings!")
		url = endpoint + "/customer_creation_credit"

		api, status = jsonrpc(url, params=params)
		if api in [200, 201]:
			if status and status.get('customer_information', False) and 'id' in status['customer_information'].keys():
				key_vals = {
					"name": status['customer_information']['sso_name'],
					"note": ""
				}
				endpoint = self.env.user.company_id.customer_host
				url = endpoint + "/customer_key_creation"
				params = {
					'data': key_vals,
					'call': 'post',
					'customer_id': status['customer_information']['id']
				}

				response_api, response_status = jsonrpc(url, params=params)
				if response_api in [200, 201]:
					if response_status and response_status.get('customer_key_information', False):
						res.api_key_id = response_status['customer_key_information']['key']
						res.client_id = response_status['customer_key_information']['client_id']
						res.customer_id = response_status['customer_key_information']['sso_customer_id']
		return res