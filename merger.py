import openpyxl
from openpyxl import load_workbook

workbook = load_workbook(filename = 'cvc.xlsx',read_only=True)
first_sheet = workbook.get_sheet_names()[0]
worksheet = workbook.get_sheet_by_name(first_sheet)
worksheet_company_names = worksheet['I']#worksheet['I2:I259065']
for x in xrange(100):
	print(worksheet_company_names[x].value)