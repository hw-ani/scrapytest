import re
import json
import json_repair
import logging

from transformers import pipeline

from scrapytest.models import ExtractionResponse
from scrapytest.prompts import build_prompt
from scrapytest.utils import chunk_text


logger = logging.getLogger(__name__)


class RelationshipExtractor:

    def __init__(
        self,
        model_name="HuggingFaceTB/SmolLM2-1.7B-Instruct",
    ):

        logger.info("Loading LLM: %s", model_name)

        self.generator = pipeline(
            task="text-generation",
            model=model_name,
            device=0,
            trust_remote_code=True,
        )

        logger.info("LLM loaded successfully.")

    def extract(self, text: str, page_url: str) -> ExtractionResponse:
        all_facts = []
        chunks = chunk_text(text)
        logger.info("Processing %d chunks", len(chunks))

        for chunk in chunks:
            prompt = build_prompt(chunk, page_url)
            result = self.generator(
                prompt,
                max_new_tokens=2048, # 로그에 찍힌 토큰 수에 맞춰 상향
                do_sample=False,
                return_full_text=False,
            )
            output = result[0]["generated_text"]
            parsed = self.parse_json(output)

            if parsed is None:
                continue

            try:
                response = ExtractionResponse.model_validate(parsed)
                all_facts.extend(response.facts)
            except Exception as e:
                logger.warning(e)

        return ExtractionResponse(
            source_doc_id="PLACEHOLDER",
            source_url=page_url,
            facts=all_facts
        )

    def parse_json(self, text):
        # 1. 마크다운 태그 일괄 제거
        cleaned = re.sub(r'```(?:json)?|```', '', text).strip()
        
        # 2. 첫 번째 '{' 기호부터 마지막 '}' 기호까지만 정규식으로 추출
        # (만약 최상위가 리스트라면 r'(\{.*\}|\[.*\])' 로 변경)
        match = re.search(r'(\{.*\})', cleaned, re.DOTALL)
        
        if match:
            json_str = match.group(1)
            try:
                return json_repair.loads(json_str)
            except Exception as e:
                logger.warning(f"JSON loads failed: {e}\nExtracted string: {json_str[:100]}...")
                return None
        else:
            logger.warning("No JSON structure found in model output.")
            logger.warning(text)
            return None
    
    def parse_llm_json(llm_output: str):
        # 1. 마크다운 백틱(```json ... ```) 제거
        cleaned = re.sub(r'```(?:json)?|```', '', llm_output).strip()
        
        # 2. 첫 번째 '{' 또는 '[' 부터 마지막 '}' 또는 ']' 까지 추출
        match = re.search(r'(\{.*\}|\[.*\])', cleaned, re.DOTALL)
        
        if match:
            json_str = match.group(0)
            try:
                return json_repair.loads(json_str)
            except json.JSONDecodeError as e:
                print(f"JSON 파싱 실패: {e}")
                return None
        return None

'''
| Component               | Function                                   |
| ----------------------- | ------------------------------------------ |
| `RelationshipExtractor` | Main LLM wrapper                           |
| `pipeline()`            | Loads Hugging Face model                   |
| `extract()`             | Converts webpage text into structured data |
| `chunk_text()`          | Splits large pages                         |
| `build_prompt()`        | Creates LLM instructions                   |
| `parse_json()`          | Converts model output into Python data     |
| `ExtractionResponse`    | Validates final structure                  |
'''