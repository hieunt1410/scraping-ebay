# -*- coding: utf-8 -*-
import json
import scrapy
from scrapy_playwright.page import PageMethod
from scraping_ebay.items import SellerItem


class SellersSpider(scrapy.Spider):

	name = "sellers"
	allowed_domains = ["ebay.com"]

	# Input file produced by the ebay spider
	products_file = "data/products.json"

	def start_requests(self):
		with open(self.products_file) as f:
			products = json.load(f)

		seen = set()
		for product in products:
			seller = product.get("Seller_Name")
			if not seller or seller in seen:
				continue
			seen.add(seller)
			url = f"https://www.ebay.com/usr/{seller}"
			yield scrapy.Request(
				url,
				callback=self.parse_seller,
				meta={
					"playwright": True,
					"playwright_page_methods": [
						PageMethod("wait_for_load_state", "load"),
					],
					"seller_name": seller,
				},
			)

	def parse_seller(self, response):
		seller_name = response.meta["seller_name"]

		# Feedback score (number in parentheses next to seller name)
		seller_spans = response.css('div.str-seller-card__info span.ux-textspans::text').getall()
		feedback_score = None
		for span in seller_spans:
			stripped = span.strip('()')
			if stripped.isdigit() or (stripped.replace(',', '').isdigit()):
				feedback_score = stripped
				break

		# Positive feedback percentage
		positive_feedback = response.xpath(
			'//span[contains(text(), "positive")]/text()'
		).get()

		# Items sold
		items_sold_parts = response.xpath(
			'//span[contains(@class, "ux-textspans")]/text()'
		).getall()
		items_sold = None
		for i, part in enumerate(items_sold_parts):
			if 'items sold' in part and i > 0:
				items_sold = items_sold_parts[i-1].strip() + ' ' + part.strip()
				break

		# Seller Detailed Ratings (DSR)
		dsr = {}
		for rating_item in response.css('div.fdbk-detail-seller-rating'):
			label = rating_item.css('div.fdbk-detail-seller-rating__label span::text').get()
			value = rating_item.css('span.fdbk-detail-seller-rating__value::text').get()
			if label and value and label not in dsr:
				dsr[label] = value

		# Total feedback count
		feedback_total = response.xpath(
			'//*[contains(text(), "Seller feedback")]/following-sibling::span[@class="SECONDARY"]/text()'
		).get()
		if feedback_total:
			feedback_total = feedback_total.strip('()')

		yield SellerItem(
			Seller_Name=seller_name,
			Seller_Feedback_Score=feedback_score,
			Seller_Positive_Feedback=positive_feedback,
			Seller_Items_Sold=items_sold,
			Seller_Detailed_Ratings=dsr if dsr else None,
			Feedback_Total=feedback_total,
		)
