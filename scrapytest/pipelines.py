import json
from scrapytest.llm import RelationshipExtractor
from scrapytest.utils import merge_facts # merge_people 대신 merge_facts 사용

class RelationshipExtractionPipeline:
    def open_spider(self, spider):
        spider.logger.info("Loading Relationship Extractor...")
        self.extractor = RelationshipExtractor()
        # 모든 추출된 fact를 저장
        self.facts = []

    def process_item(self, item, spider):
        spider.logger.info(f"Extracting relationships from {item['url']}")
        response = self.extractor.extract(
            text=item["text"],
            page_url=item["url"],
        )

        # 청크 분할로 인한 중복 데이터 제거
        page_facts = merge_facts(response.facts)
        self.facts.extend(page_facts)

        return item

    def close_spider(self, spider):
        spider.logger.info(f"Writing {len(self.facts)} relationships...")
        output = {
            "source_doc_id": "PLACEHOLDER",
            "facts": [
                fact.model_dump()
                for fact in self.facts
            ]
        }
        with open("relationships.json", "w", encoding="utf-8") as f:
            json.dump(output, f, indent=4, ensure_ascii=False)
            
        spider.logger.info("relationships.json saved successfully.")

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