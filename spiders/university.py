import scrapy

from bs4 import BeautifulSoup
from urllib.parse import urldefrag

from scrapytest.items import PageItem
from scrapytest.utils import clean_text


class UniversitySpider(scrapy.Spider):

    name = "university"

    allowed_domains = [
        "ngws-knu.github.io"
    ]

    start_urls = [
        "ngws-knu.github.io/"
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
            "ngws-knu.github.io/"
        )