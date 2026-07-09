'''
BOT_NAME = "scrapytest"

SPIDER_MODULES = ["scrapytest.spiders"]
NEWSPIDER_MODULE = "scrapytest.spiders"

LLM_RESPONSE_MODEL = "scrapytest.models.ResponseModel"

LLM_MODEL = "HuggingFaceTB/SmolLM2-1.7B-Instruct"

DOWNLOADER_MIDDLEWARES = {
    "scrapy_llm.handler.LlmExtractorMiddleware": 543,
}

FEEDS = {
    "relationships.json": {
        "format": "json",
        "indent": 4,
        "overwrite": True,
    }
}
'''

from pathlib import Path

BOT_NAME = "scrapytest"

SPIDER_MODULES = ["scrapytest.spiders"]
NEWSPIDER_MODULE = "scrapytest.spiders"

###########################################################
# Crawl Configuration
###########################################################

ROBOTSTXT_OBEY = False

DOWNLOAD_DELAY = 0.5

CONCURRENT_REQUESTS = 8

CONCURRENT_REQUESTS_PER_DOMAIN = 4

DEPTH_LIMIT = 10

COOKIES_ENABLED = False

TELNETCONSOLE_ENABLED = False

USER_AGENT = (
    "Mozilla/5.0 "
    "(compatible; ResearchRelationshipCrawler/1.0)"
)

###########################################################
# AutoThrottle
###########################################################

AUTOTHROTTLE_ENABLED = True

AUTOTHROTTLE_START_DELAY = 1

AUTOTHROTTLE_MAX_DELAY = 5

AUTOTHROTTLE_TARGET_CONCURRENCY = 2

###########################################################
# Pipelines
###########################################################

ITEM_PIPELINES = {
    "scrapytest.pipelines.RelationshipExtractionPipeline": 300,
}

###########################################################
# Logging
###########################################################

LOG_LEVEL = "INFO"

###########################################################
# Feed
###########################################################

FEED_EXPORT_ENCODING = "utf-8"

###########################################################
# LLM
###########################################################

# Any HuggingFace model
LLM_MODEL = "SmolLM2-1.7B-Instruct"

# Maximum words per chunk
LLM_CHUNK_SIZE = 900

# Overlap between chunks
LLM_OVERLAP = 100

###########################################################
# Output
###########################################################

OUTPUT_FILE = "relationships.json"