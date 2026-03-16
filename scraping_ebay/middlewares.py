# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/spider-middleware.html

import logging
import time
import urllib.parse
import urllib.request

from scrapy import signals

logger = logging.getLogger(__name__)


class CaptchaAIMiddleware:
    """Downloader middleware that detects eBay CAPTCHA/challenge pages
    and solves them using the CaptchaAI API (https://captchaai.com).

    Set CAPTCHAAI_API_KEY in settings or via the CAPTCHAAI_API_KEY
    environment variable to enable. When the key is empty the
    middleware is a no-op.
    """

    SUBMIT_URL = 'https://ocr.captchaai.com/in.php'
    RESULT_URL = 'https://ocr.captchaai.com/res.php'
    POLL_INTERVAL = 5       # seconds between result polls
    MAX_POLL_ATTEMPTS = 24  # 24 * 5s = 2 minutes max wait

    @classmethod
    def from_crawler(cls, crawler):
        api_key = crawler.settings.get('CAPTCHAAI_API_KEY', '')
        enabled = crawler.settings.getbool('CAPTCHAAI_ENABLED', bool(api_key))
        return cls(api_key=api_key, enabled=enabled)

    def __init__(self, api_key='', enabled=False):
        self.api_key = api_key
        self.enabled = enabled and bool(api_key)

    # ------------------------------------------------------------------
    # Detection
    # ------------------------------------------------------------------

    @staticmethod
    def _is_challenge(response):
        """Return True if the response is an eBay challenge/CAPTCHA page."""
        url = response.url
        if 'splashui/challenge' in url:
            return True
        body = response.text if hasattr(response, 'text') else ''
        if 'g-recaptcha' in body or 'data-sitekey' in body:
            return True
        return False

    @staticmethod
    def _extract_sitekey(body):
        """Pull the reCAPTCHA sitekey out of the page HTML."""
        import re
        # data-sitekey="..."
        m = re.search(r'data-sitekey=["\']([^"\']+)', body)
        if m:
            return m.group(1)
        # grecaptcha.render(…, {sitekey: "..."})
        m = re.search(r'sitekey\s*:\s*["\']([^"\']+)', body)
        if m:
            return m.group(1)
        return None

    @staticmethod
    def _extract_original_url(response):
        """Try to find the URL eBay will redirect back to after solving."""
        import re
        url = response.url
        parsed = urllib.parse.urlparse(url)
        qs = urllib.parse.parse_qs(parsed.query)
        if 'ru' in qs:
            return qs['ru'][0]
        body = response.text if hasattr(response, 'text') else ''
        m = re.search(r'name=["\']?ru["\']?\s+value=["\']([^"\']+)', body)
        if m:
            return m.group(1)
        return None

    # ------------------------------------------------------------------
    # CaptchaAI API helpers
    # ------------------------------------------------------------------

    def _submit_captcha(self, sitekey, page_url):
        """Submit a reCAPTCHA task to CaptchaAI. Returns the task ID."""
        params = urllib.parse.urlencode({
            'key': self.api_key,
            'method': 'userrecaptcha',
            'googlekey': sitekey,
            'pageurl': page_url,
            'json': '1',
        }).encode()
        req = urllib.request.Request(self.SUBMIT_URL, data=params)
        with urllib.request.urlopen(req, timeout=30) as resp:
            import json
            data = json.loads(resp.read())
        if data.get('status') == 1:
            return data['request']
        raise RuntimeError(f"CaptchaAI submit error: {data}")

    def _poll_result(self, task_id):
        """Poll CaptchaAI until the solution is ready. Returns the token."""
        import json
        params = urllib.parse.urlencode({
            'key': self.api_key,
            'action': 'get',
            'id': task_id,
            'json': '1',
        })
        url = f'{self.RESULT_URL}?{params}'
        for _ in range(self.MAX_POLL_ATTEMPTS):
            time.sleep(self.POLL_INTERVAL)
            with urllib.request.urlopen(url, timeout=30) as resp:
                data = json.loads(resp.read())
            if data.get('status') == 1:
                return data['request']
            if data.get('request') != 'CAPCHA_NOT_READY':
                raise RuntimeError(f"CaptchaAI error: {data}")
        raise TimeoutError("CaptchaAI solve timed out")

    # ------------------------------------------------------------------
    # Scrapy downloader middleware interface
    # ------------------------------------------------------------------

    def process_response(self, request, response, spider):
        if not self.enabled:
            return response

        if not self._is_challenge(response):
            return response

        body = response.text if hasattr(response, 'text') else ''
        sitekey = self._extract_sitekey(body)
        original_url = self._extract_original_url(response) or request.url

        if not sitekey:
            logger.warning(
                'CaptchaAI: challenge detected but no sitekey found at %s',
                response.url,
            )
            return response

        logger.info(
            'CaptchaAI: solving reCAPTCHA for %s (sitekey=%s…)',
            original_url, sitekey[:12],
        )

        try:
            task_id = self._submit_captcha(sitekey, response.url)
            token = self._poll_result(task_id)
        except Exception:
            logger.exception('CaptchaAI: failed to solve CAPTCHA')
            return response

        logger.info('CaptchaAI: solved! Retrying original URL %s', original_url)

        # Retry the original request with the CAPTCHA token cookie
        new_request = request.replace(
            url=original_url,
            dont_filter=True,
            cookies={'captcha_token': token},
        )
        new_request.meta['captchaai_solved'] = True
        return new_request


class ScrapingEbaySpiderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, dict or Item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Response, dict
        # or Item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn't have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class ScrapingEbayDownloaderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        # Called for each request that goes through the downloader
        # middleware.

        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called
        return None

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        pass

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)
