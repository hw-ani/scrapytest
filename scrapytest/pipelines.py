# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

'''
FIRST DRAFT
# useful for handling different item types with a single interface
from itemadapter import ItemAdapter


class ScrapytestPipeline:
    def process_item(self, item):
        return item
'''

'''
SECOND DRAFT

import json

from scrapytest.llm import RelationshipExtractor
from scrapytest.utils import chunk_text


class RelationshipExtractionPipeline:
    """
    Pipeline that receives crawled pages,
    extracts relationships using the LLM,
    and writes one JSON object per webpage.
    """

    def open_spider(self, spider):

        spider.logger.info("Loading LLM...")

        self.extractor = RelationshipExtractor()

        self.output = open(
            "relationships.jsonl",
            "w",
            encoding="utf-8",
        )

    ###############################################################

    def process_item(self, item, spider):

        text = item["text"]

        url = item["url"]

        chunks = chunk_text(
            text,
            chunk_size=3000,
            overlap=300,
        )

        people = []

        ###########################################################

        for chunk in chunks:

            spider.logger.info(
                f"Processing chunk ({len(chunk)} chars)"
            )

            response = self.extractor.extract(
                chunk,
                url,
            )

            people.extend(
                response.people
            )

        ###########################################################
        ## Save page
        ###########################################################

        page_json = {

            "source_url": url,

            "title": item["title"],

            "people": [
                person.model_dump()
                for person in people
            ]
        }

        self.output.write(
            json.dumps(
                page_json,
                ensure_ascii=False,
                indent=4,
            )
        )

        self.output.write("\n")

        return item

    ###############################################################

    def close_spider(self, spider):

        self.output.close()
'''

import json

from scrapytest.llm import RelationshipExtractor
from scrapytest.utils import merge_people


class RelationshipExtractionPipeline:

    def open_spider(self, spider):

        spider.logger.info("Loading Relationship Extractor...")

        self.extractor = RelationshipExtractor()

        # Stores every extracted relationship
        self.people = []

    def process_item(self, item, spider):

        spider.logger.info(
            f"Extracting relationships from {item['url']}"
        )

        response = self.extractor.extract(
            text=item["text"],
            page_url=item["url"],
        )

        # Remove duplicates produced by chunking
        page_people = merge_people(response.people)

        self.people.extend(page_people)

        return item

    def close_spider(self, spider):

        spider.logger.info(
            f"Writing {len(self.people)} relationships..."
        )

        output = {
            "people": [
                person.model_dump()
                for person in self.people
            ]
        }

        with open(
            "relationships.json",
            "w",
            encoding="utf-8",
        ) as f:

            json.dump(
                output,
                f,
                indent=4,
                ensure_ascii=False,
            )

        spider.logger.info(
            "relationships.json saved successfully."
        )

'''
| Stage                       | What happens                         |
| --------------------------- | ------------------------------------ |
| 1. Spider starts            | Scrapy begins crawling websites.     |
| 2. `open_spider()`          | Loads the LLM extractor.             |
| 3. Spider yields `PageItem` | Contains `url`, `text`, `html`, etc. |
| 4. `process_item()`         | Sends webpage text to the LLM.       |
| 5. LLM extraction           | Finds people and relationships.      |
| 6. Store results            | Adds data to `self.people`.          |
| 7. Crawl ends               | `close_spider()` runs.               |
| 8. Save output              | Creates `relationships.json`.        |
'''