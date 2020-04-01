# -*- coding: utf-8 -*-
from odoo import http
from odoo.exceptions import AccessError, MissingError
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal
from openerp.addons.web.controllers.main import serialize_exception,content_disposition
import base64

class CustomerPortal(CustomerPortal):

	@http.route(['/my/analytics_result/<int:order_id>'], type='http', auth="public", website=True)
	def portal_my_analytics_result(self, order_id=None, access_token=None, **kw):
		try:
			order_sudo = self._document_check_access('match.run.history', order_id, access_token=access_token)
		except (AccessError, MissingError):
			return request.redirect('/my')
		values = {
			'order': order_sudo
		}
		return request.render("hiredrate_ras.portal_my_analytics_result", values)

class Binary(http.Controller):

	@http.route('/web/binary/download_document', type='http', auth="public")
	@serialize_exception
	def download_document(self, model, field, id, filename=None, **kw):
		fields = [field]
		res = request.env[model].search([("id", "=", int(id))])
		res = res.read(fields)[0]
		filecontent = base64.b64decode(res.get(field) or '')
		if not filecontent:
			return request.not_found()
		else:
			if filename:
				return request.make_response(filecontent, [('Content-Type', 'application/octet-stream'), ('Content-Disposition', content_disposition(filename))])