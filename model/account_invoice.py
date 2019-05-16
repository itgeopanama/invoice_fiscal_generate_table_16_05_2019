# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api, _
import logging
from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning
import json

_logger = logging.getLogger(__name__)

class FiscalHeader(models.Model):
	_name="fiscal.header"
	_rec_name="invoice_number"
	
	invoice_date = fields.Date('Invoice Date')
	seller =  fields.Char('Seller')
	customer_code = fields.Char('Customer Code')
	customer_name = fields.Char('Customer Name')
	invoice_number = fields.Char('Invoice NO')
	ref = fields.Char('Internal Reference')
	tax = fields.Float('Tax Amount')
	sell_term = fields.Char('Sell Term')
	transaction_type = fields.Char('Transaction Type')
	total = fields.Float('Total')
	sub_total = fields.Float('Sub Total')
	fisc_sequence = fields.Char('Sequence')
	fiscal_details = fields.One2many('fiscal.details', 'fiscal_details_id')
	company_id = fields.Many2one('res.company')
	ruc = fields.Char('RUC Code')
	printed = fields.Boolean('Printed', default=False)
	
	@api.model
	def create(self, vals):
		vals['fisc_sequence'] = self.env['ir.sequence'].next_by_code('fiscal.header')
		return super(FiscalHeader, self).create(vals)
	
class FiscalDetails(models.Model):
	_name="fiscal.details"
	
	item_code = fields.Char()
	item_desc =  fields.Char()
	tax = fields.Char()
	quantity = fields.Char()
	unit_price = fields.Char()
	discount = fields.Char()
	total_amount = fields.Char()
	fiscal_details_id = fields.Many2one('fiscal.header')
	
class AccountInvoice(models.Model):
	_inherit='account.invoice'
	
	fiscal_header = fields.Many2one('fiscal.header', string='Fiscal Info')
	
	@api.multi
	def action_invoice_open(self):
		res = super(AccountInvoice, self).action_invoice_open()
		
		header = {
			'invoice_date': self.date_invoice,
			'seller': self.company_id.name,
			'customer_code': self.partner_id.zip,
			'customer_name': self.partner_id.name,
			'invoice_number': self.number,
			'company_id': self.company_id.id,
			'ref': self.name,
			'tax': self.amount_tax,
			'sell_term': 'Normal' if self.type in ['out_invoice', 'in_invoice'] else 'Credit',
			'total': self.amount_total,
			'sub_total': self.amount_untaxed,
			'transaction_type': 'invoice' if self.type in ['out_invoice', 'in_invoice'] else 'cnote',
		}
		
		for num in self.partner_id.id_numbers:
			header['ruc'] = num.category_id.code
			break
			
		detail_line = []
		for line in self.invoice_line_ids:
			taxp = 0
			mapped = line.invoice_line_tax_ids.mapped('amount')
			if mapped:
				taxp = mapped[0]
				
			detail_line.append((0,0,{
				'item_code': line.product_id.name,
				'item_desc': line.name,
				'tax': taxp,
				'quantity': line.quantity,	
				'unit_price': line.price_unit,
				'discount': 0,
				'total_amount': (line.quantity * (line.price_unit - 0))
			}))
			
		header.update({
			'fiscal_details': detail_line
		})
		h_id = self.env['fiscal.header'].create(header)
		self.write({'fiscal_header': h_id.id })
		return res