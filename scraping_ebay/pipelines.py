# -*- coding: utf-8 -*-
from scrapy.exceptions import DropItem
from scraping_ebay.items import SellerItem


class DuplicateSellerPipeline:
    """Drop duplicate SellerItems — keep only the first occurrence per seller name."""

    def open_spider(self):
        self.seen_sellers = set()

    def process_item(self, item):
        if not isinstance(item, SellerItem):
            return item
        name = item.get('Seller_Name')
        if name in self.seen_sellers:
            raise DropItem(f"Duplicate seller: {name}")
        self.seen_sellers.add(name)
        return item
