# -*- coding: utf-8 -*-
import re
import scrapy
from scrapy_playwright.page import PageMethod
from scraping_ebay.items import ProductItem


class EbaySpider(scrapy.Spider):
    name = "ebay"
    allowed_domains = ["ebay.com"]

    # Allow a custom parameter (-a flag in the scrapy command)
    def __init__(self, search="nintendo switch console"):
        self.search_string = search

    @staticmethod
    def _playwright_meta(**extra):
        """Build meta dict for Playwright requests.
        Waits for the challenge JS to redirect, then waits for page load."""
        meta = {
            "playwright": True,
            "playwright_page_methods": [
                PageMethod("wait_for_url", "**/**/sch/**", timeout=60000),
                PageMethod("wait_for_load_state", "load"),
            ],
        }
        meta.update(extra)
        return meta

    @staticmethod
    def _playwright_detail_meta(**extra):
        """Build meta dict for Playwright product detail page requests."""
        meta = {
            "playwright": True,
            "playwright_page_methods": [
                PageMethod("wait_for_url", "**/**/itm/**", timeout=60000),
                PageMethod("wait_for_load_state", "load"),
                # Scroll to trigger lazy-loaded recommendation sections
                PageMethod("evaluate", "window.scrollTo(0, document.body.scrollHeight / 2)"),
                PageMethod("wait_for_timeout", 1000),
                PageMethod("evaluate", "window.scrollTo(0, document.body.scrollHeight)"),
                PageMethod("wait_for_timeout", 1500),
            ],
        }
        meta.update(extra)
        return meta

    @staticmethod
    def _rec_ids(response, *headings):
        """Extract item IDs from a recommendation section matched by heading text.
        Searches both <section> and <div> containers."""
        for heading in headings:
            low = heading.lower()
            hrefs = response.xpath(
                f'//*[self::section or self::div]'
                f'[.//*[contains(translate(normalize-space(.), '
                f'"ABCDEFGHIJKLMNOPQRSTUVWXYZ", "abcdefghijklmnopqrstuvwxyz"), "{low}")]]'
                f'//a[contains(@href, "/itm/")]/@href'
            ).getall()
            if hrefs:
                return list(dict.fromkeys(
                    h.split("/itm/")[1].split("?")[0].split("/")[0]
                    for h in hrefs if "/itm/" in h
                )) or None
        return None

    def start_requests(self):
        search_url = (
            "https://www.ebay.com/sch/i.html?_from=R40"
            "&_nkw=" + self.search_string.replace(" ", "+") + "&_ipg=200"
        )
        yield scrapy.Request(
            search_url,
            callback=self.parse_link,
            meta=self._playwright_meta(),
        )

    # Parse the search results
    def parse_link(self, response):
        results = response.css("ul.srp-results li.s-card")
        self.logger.info("Search page URL: %s", response.url)
        self.logger.info("Found %d products on page", len(results))

        for product in results:
            product_url = product.css("a.s-card__link::attr(href)").get()
            if not product_url or "itm/" not in product_url:
                continue

            product_url = product_url.split("&hash=")[0].split("&itmmeta=")[0]

            name = product.css("div.s-card__title span::text").get() or "ERROR"
            price = product.css("span.s-card__price::text").get()
            status = product.css("div.s-card__subtitle span::text").get()

            summary_data = {
                "Name": name,
                "Status": status,
                "Price": price,
                "URL": product_url,
            }

            yield scrapy.Request(
                product_url,
                meta=self._playwright_detail_meta(summary_data=summary_data),
                callback=self.parse_product_details,
            )

        next_page_url = response.css("a.pagination__next::attr(href)").get()
        if not next_page_url:
            next_page_url = response.xpath(
                '//a[contains(@class, "pagination__next")]/@href'
            ).get()

        if next_page_url and not str(next_page_url).endswith("#"):
            self.logger.info("Next page: %s", next_page_url)
            yield scrapy.Request(
                next_page_url,
                callback=self.parse_link,
                meta=self._playwright_meta(),
            )
        else:
            self.logger.info("eBay products collected successfully !!!")

    # Parse details page for each product
    def parse_product_details(self, response):
        summary = response.meta["summary_data"]

        # --- Item Specifics ---
        item_specifics = {}
        for row in response.css("div.ux-layout-section--features dl.ux-labels-values"):
            label = row.css("dt.ux-labels-values__labels span.ux-textspans::text").get()
            parts = row.css(
                "dd.ux-labels-values__values span.ux-textspans::text"
            ).getall()
            _skip = {"read more", "read less"}
            value = (
                " ".join(
                    p.strip()
                    for p in parts
                    if p.strip() and p.strip().lower() not in _skip
                )
                or None
            )
            if label and value:
                item_specifics[label] = value

        # --- Seller Info ---
        seller_card = response.css("div.x-sellercard-atf__info")
        seller_name = seller_card.css("span.ux-textspans::text").get()

        # --- Feedback counts ---
        feedback_total = response.xpath(
            '//*[contains(text(), "Seller feedback")]/following-sibling::span[@class="SECONDARY"]/text()'
        ).get()
        if feedback_total:
            feedback_total = feedback_total.strip("()")

        this_item_tab = response.xpath(
            '//div[contains(@class, "tabs__item")]//span[contains(text(), "This item")]/text()'
        ).get()
        feedback_this_item = None
        if this_item_tab:
            m = re.search(r"\(([0-9,]+)\)", this_item_tab)
            feedback_this_item = m.group(1) if m else None

        all_items_tab = response.xpath(
            '//div[contains(@class, "tabs__item")]//span[contains(text(), "All items")]/text()'
        ).get()
        feedback_all_items = None
        if all_items_tab:
            m = re.search(r"\(([0-9,]+)\)", all_items_tab)
            feedback_all_items = m.group(1) if m else None

        # --- Feedback Topics ---
        feedback_panels = response.css("div.fdbk-detail-list div.tabs__panel")

        feedback_topics_this_item = None
        if len(feedback_panels) >= 1:
            topics = list(
                dict.fromkeys(
                    t.strip()
                    for t in feedback_panels[0]
                    .css("li.fdbk-detail-list__ai-topic span::text")
                    .getall()
                    if t.strip()
                )
            )
            feedback_topics_this_item = topics if topics else None

        feedback_topics_all_items = None
        if len(feedback_panels) >= 2:
            topics = list(
                dict.fromkeys(
                    t.strip()
                    for t in feedback_panels[1]
                    .css("li.fdbk-detail-list__ai-topic span::text")
                    .getall()
                    if t.strip()
                )
            )
            feedback_topics_all_items = topics if topics else None

        # --- Popular Categories from Store ---
        categories = list(
            dict.fromkeys(
                t.strip()
                for t in response.css(
                    "span.x-category-pills__list-item span.ux-textspans::text"
                ).getall()
                if t.strip()
            )
        )

        # Extract item ID from URL (e.g. /itm/123456789 → "123456789")
        item_id = None
        if "/itm/" in response.url:
            item_id = response.url.split("/itm/")[1].split("?")[0].split("/")[0]

        # --- Recommendation sections (lazy-loaded after scroll) ---
        yield ProductItem(
            ID=item_id,
            Name=summary["Name"],
            Status=summary["Status"],
            Price=summary["Price"],
            URL=summary["URL"],
            UPC=response.xpath('//h2[@itemprop="gtin13"]/text()').extract_first(),
            Item_Specifics=item_specifics,
            Seller_Name=seller_name,
            Store_Categories=categories if categories else None,
            Feedback_Topics_This_Item=feedback_topics_this_item,
            Feedback_Topics_All_Items=feedback_topics_all_items,
            Feedback_This_Item=feedback_this_item,
            Feedback_All_Items=feedback_all_items,
            You_May_Also_Like=self._rec_ids(response, "you may also like"),
            Similar_Customers_Also_Bought=self._rec_ids(response, "similar customers also bought", "customers also bought", "customers who bought this also bought", "customers who viewed this also bought"),
            Sellers_Other_Items=self._rec_ids(response, "seller's other items", "sellers other items", "more from this seller", "other items from this seller"),
            Related_To_This_Item=self._rec_ids(response, "related to this item", "related items", "similar items"),
            Explore_Related_Items=self._rec_ids(response, "explore related items", "explore similar items", "more like this"),
            People_Who_Viewed_Also_Viewed=self._rec_ids(response, "people who viewed this also viewed", "people who viewed this item also viewed"),
        )
