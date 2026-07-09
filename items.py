import scrapy


class PageItem(scrapy.Item):
    """
    Represents one crawled webpage before LLM extraction.
    """

    url = scrapy.Field()

    title = scrapy.Field()

    text = scrapy.Field()

    html = scrapy.Field()

'''
| Component        | Purpose                     |
| ---------------- | --------------------------- |
| `PageItem`       | Represents one webpage      |
| `url`            | Stores webpage address      |
| `title`          | Stores page title           |
| `text`           | Stores cleaned page content |
| `html`           | Stores raw HTML             |
| `scrapy.Field()` | Defines Scrapy data fields  |
'''