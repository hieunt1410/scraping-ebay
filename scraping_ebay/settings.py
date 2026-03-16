# -*- coding: utf-8 -*-

# Scrapy settings for scraping_ebay project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://doc.scrapy.org/en/latest/topics/settings.html
#     https://doc.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://doc.scrapy.org/en/latest/topics/spider-middleware.html

import os

BOT_NAME = 'scraping_ebay'

SPIDER_MODULES = ['scraping_ebay.spiders']
NEWSPIDER_MODULE = 'scraping_ebay.spiders'


# Use a browser-like user-agent to avoid being blocked
USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

CONCURRENT_REQUESTS = 8

DOWNLOAD_DELAY = 0.5
# The download delay setting will honor only one of:
#CONCURRENT_REQUESTS_PER_DOMAIN = 16
#CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
#COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
#TELNETCONSOLE_ENABLED = False

# Override the default request headers:
DEFAULT_REQUEST_HEADERS = {
   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
   'Accept-Language': 'en-US,en;q=0.9',
   'Accept-Encoding': 'gzip, deflate, br',
}

# Enable or disable spider middlewares
# See https://doc.scrapy.org/en/latest/topics/spider-middleware.html
#SPIDER_MIDDLEWARES = {
#    'scraping_ebay.middlewares.ScrapingEbaySpiderMiddleware': 543,
#}

# Enable or disable downloader middlewares
# See https://doc.scrapy.org/en/latest/topics/downloader-middleware.html
DOWNLOADER_MIDDLEWARES = {
    'scraping_ebay.middlewares.CaptchaAIMiddleware': 542,
    #'scraping_ebay.middlewares.ScrapingEbayDownloaderMiddleware': 543,
}

# CaptchaAI settings (https://captchaai.com)
# Set your API key via environment variable or directly here
CAPTCHAAI_API_KEY = os.environ.get('CAPTCHAAI_API_KEY', '')
# Enable/disable the CaptchaAI middleware
CAPTCHAAI_ENABLED = bool(CAPTCHAAI_API_KEY)

# --- Playwright (headless browser) settings ---
# Used to bypass eBay's JS-based challenge pages (Argon2 proof-of-work)
DOWNLOAD_HANDLERS = {
    "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
    "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
}

TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"

PLAYWRIGHT_BROWSER_TYPE = "chromium"
PLAYWRIGHT_LAUNCH_OPTIONS = {
    "headless": True,
    "args": [
        "--disable-blink-features=AutomationControlled",
    ],
}

# Block images, fonts, and media to speed up page loads significantly
def PLAYWRIGHT_ABORT_REQUEST(req):
    return req.resource_type in {"image", "media", "font"}

# Enable or disable extensions
# See https://doc.scrapy.org/en/latest/topics/extensions.html
#EXTENSIONS = {
#    'scrapy.extensions.telnet.TelnetConsole': None,
#}

# Drop duplicate sellers (same Seller_Name seen more than once)
ITEM_PIPELINES = {
    'scraping_ebay.pipelines.DuplicateSellerPipeline': 100,
}

# SellerItem → data/sellers.json (written by the sellers spider)
# ProductItem output is controlled per-run via -O flag in run_all.sh
FEEDS = {
    'data/sellers.json': {
        'format': 'json',
        'encoding': 'utf8',
        'overwrite': True,
        'item_classes': ['scraping_ebay.items.SellerItem'],
    },
}

# Enable and configure the AutoThrottle extension (disabled by default)
# See https://doc.scrapy.org/en/latest/topics/autothrottle.html
#AUTOTHROTTLE_ENABLED = True
# The initial download delay
#AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
#AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
#AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
#AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See https://doc.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
#HTTPCACHE_ENABLED = True
#HTTPCACHE_EXPIRATION_SECS = 0
#HTTPCACHE_DIR = 'httpcache'
#HTTPCACHE_IGNORE_HTTP_CODES = []
#HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'
