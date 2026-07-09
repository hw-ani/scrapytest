'''
import scrapy

from scrapy_llm.config import LLM_EXTRACTED_DATA_KEY
from scrapytest.models import ResponseModel
'''

'''
FIRST DRAFT
class UniversitySpider(scrapy.Spider):

    name = "university"

    response_model = ResponseModel

    start_urls = [
        "https://sites.google.com/view/knuvrlab/home"
    ]

    visited = set()

    def parse(self, response):
        extracted = response.request.meta.get(LLM_EXTRACTED_DATA_KEY)

        if extracted:
            yield extracted

        for href in response.css("a::attr(href)").getall():
            next_url = response.urljoin(href)

            if (
                next_url.startswith("https://sites.google.com/view/knuvrlab")
                and next_url not in self.visited
            ):
                self.visited.add(next_url)
                yield response.follow(next_url, callback=self.parse)
'''

'''
SECOND DRAFT

import scrapy

from urllib.parse import urldefrag, urlparse

from bs4 import BeautifulSoup, Comment

from scrapytest.items import PageItem


class UniversitySpider(scrapy.Spider):
    """
    Recursively crawls an entire university website.

    This spider ONLY collects pages.
    Relationship extraction is done later by the pipeline.
    """

    name = "university"

    start_urls = [
        "https://sites.google.com/view/knuvrlab/home"
    ]

    allowed_domains = [
        "sites.google.com"
    ]

    custom_settings = {
        "DEPTH_LIMIT": 10,
        "ROBOTSTXT_OBEY": False,
    }

    visited = set()

    ######################################################################
    ## Parse
    ######################################################################

    def parse(self, response):

        canonical_url, _ = urldefrag(response.url)

        if canonical_url in self.visited:
            return

        self.visited.add(canonical_url)

        item = PageItem()

        item["url"] = canonical_url

        item["title"] = response.css("title::text").get(default="")

        item["html"] = self.clean_html(response.text)

        item["text"] = self.extract_text(item["html"])

        yield item

        ###########################################################
        ## Follow every internal link
        ###########################################################

        for href in response.css("a::attr(href)").getall():

            next_url = response.urljoin(href)

            next_url, _ = urldefrag(next_url)

            if self.is_internal(next_url):

                yield response.follow(
                    next_url,
                    callback=self.parse,
                )

    ######################################################################
    ## HTML Cleaning
    ######################################################################

    def clean_html(self, html):

        soup = BeautifulSoup(html, "html.parser")

        for tag in soup(
            [
                "script",
                "style",
                "noscript",
                "iframe",
                "svg",
                "footer",
                "header",
                "nav",
                "form",
            ]
        ):
            tag.decompose()

        for comment in soup.find_all(
            string=lambda text: isinstance(text, Comment)
        ):
            comment.extract()

        return str(soup)

    ######################################################################
    ## Visible Text
    ######################################################################

    def extract_text(self, html):

        soup = BeautifulSoup(html, "html.parser")

        text = soup.get_text(
            separator="\n",
            strip=True,
        )

        return text

    ######################################################################
    ## Stay inside website
    ######################################################################

    def is_internal(self, url):

        parsed = urlparse(url)

        if parsed.scheme not in ("http", "https"):
            return False

        if parsed.netloc != "sites.google.com":
            return False

        return parsed.path.startswith("/view/knuvrlab")
'''

import scrapy

from bs4 import BeautifulSoup
from urllib.parse import urldefrag

from scrapytest.items import PageItem
from scrapytest.utils import clean_text


class UniversitySpider(scrapy.Spider):

    name = "university"

    allowed_domains = [
        "sites.google.com"
    ]

    start_urls = [
        "https://ngws-knu.github.io/"
    ]

    custom_settings = {
        "DEPTH_LIMIT": 10,
    }

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.visited = set()

    def parse(self, response):

        url, _ = urldefrag(response.url)

        if url in self.visited:
            return

        self.visited.add(url)

        self.logger.info(f"Crawling {url}")

        soup = BeautifulSoup(
            response.text,
            "html.parser"
        )

        # Remove unnecessary elements
        for tag in soup([
            "script",
            "style",
            "noscript",
            "svg",
            "footer"
        ]):
            tag.decompose()

        text = soup.get_text(
            separator="\n",
            strip=True
        )

        text = clean_text(text)

        yield PageItem(
            url=url,
            title=response.css("title::text").get(default=""),
            text=text,
            html=str(soup)
        )

        # Crawl every page inside the same website

        for href in response.css("a::attr(href)").getall():

            next_url = response.urljoin(href)

            next_url, _ = urldefrag(next_url)

            if self.is_internal(next_url):

                yield response.follow(
                    next_url,
                    callback=self.parse
                )

    def is_internal(self, url):

        return url.startswith(
            "https://sites.google.com/view/knuvrlab"
        )