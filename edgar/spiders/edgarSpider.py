import scrapy
from scrapy.item import Item, Field
import term_values
from term_values import *
import re
from re import findall, IGNORECASE
import json
from json import dumps

def calculateFocus(a_dict, raw_form_data):
	term_frequency = {} # { 'term' : frequency }
	total_count = 0 # total # of terms counted
	total_weight = 0 # total weight of all terms

	for term, weight in a_dict.iteritems():
		matches = findall('\\b' + term + '\\b', raw_form_data, IGNORECASE) # get list of terms matched
		number_of_matches = len(matches) # number of matches for this term

		if number_of_matches > 0: # if match found
			total_count += number_of_matches # increase total number of matches
			total_weight += number_of_matches * weight # increase total weight
	if total_count > 0: # if matched at least once
		return total_weight/total_count # return focus value
	else:
		return 0 

class EdgarSpider(scrapy.Spider):
	name = "edgar" # name of spider

	with open("url-final.txt","rt") as url_file:
		start_urls = [url.strip() for url in url_file.readlines()] # fetch all urls from url-final.txt

	def parse(self, response):
		# click Documents button
		for href in response.xpath('//a[@id="documentsbutton"]/@href').extract():
			yield response.follow(href, self.clicked_document_button)

	def clicked_document_button(self, response): 
		# pick up meta data on page listing documents related to 10-K
		filing_date = response.css('div.info::text').extract_first()
		year = filing_date.split('-')[0]
		company_name = response.css('span.companyName::text').extract_first().split(' (')[0]
		
		# click on actual document
		href = response.xpath('//td[text()="Complete submission text file"]/following-sibling::td/a/@href').extract_first()
		if not href:
			href = response.xpath('//td[text()="10-K"]/preceding-sibling::td/a/@href').extract_first()
			if not href: 
				href = response.xpath('//td[text()="10-K/A"]/preceding-sibling::td/a/@href').extract_first()
				if not href:
					href = response.xpath('//td[text()="10-K405"]/preceding-sibling::td/a/@href').extract_first()
					if not href:
						href = response.xpath('//td[@scope="row"]/a[contains(text(),"10k")]/@href').extract_first()
						
		yield response.follow(href, self.parse_document, meta={'year':year, 'company_name':company_name})

	def parse_document(self, response):
		# store metadata from previous page
		year = response.meta['year']
		company_name = response.meta['company_name']

		# raw text file of 10-K content
		raw_form_data = response.xpath('//type[contains(text(),"10-K")]').extract_first()

		# calculate focuses
		eco_focus = calculateFocus(eco_dict, raw_form_data)
		financial_focus = calculateFocus(financial_dict, raw_form_data)
		learning_focus = calculateFocus(learning_dict, raw_form_data)
		
		with open("output.txt", "a") as output_file:
			# dump all words
			output_file.write(company_name + '\t' + year + '\t' + str(eco_focus) + '\t' + str(financial_focus) + '\t' + str(learning_focus) +'\n')

		yield