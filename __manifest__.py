{
	'name': "Invoice Fiscal Generate Details",
	'category': '',
	'author': "Onedoos",
	'website': 'https://www.onedoos.com',
	'description': """
		Generate invoice fiscal info in table name fiscal_header and fiscal_header for panama fiscal printer
	""",
	'depends': ['account', 'partner_panama_itgeo'],
	'data': [
		'views/account_invoice_view.xml',
		'data/fisc_data.xml',
	],
	'installable': True,
	'application': True,
}
