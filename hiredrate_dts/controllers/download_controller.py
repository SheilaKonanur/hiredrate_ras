# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
from openerp.addons.web.controllers.main import serialize_exception,content_disposition
import base64

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