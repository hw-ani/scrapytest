import re
import json
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

        all_people = []

        chunks = chunk_text(text)

        logger.info("Processing %d chunks", len(chunks))

        for chunk in chunks:

            prompt = build_prompt(chunk, page_url)

            result = self.generator(
                prompt,
                max_new_tokens=2048,
                do_sample=False,
                temperature=0.0,
                return_full_text=False,
            )

            output = result[0]["generated_text"]

            parsed = self.parse_llm_json(output)

            if parsed is None:
                continue

            try:

                response = ExtractionResponse.model_validate(parsed)

                all_people.extend(response.people)

            except Exception as e:

                logger.warning(e)

        return ExtractionResponse(
            people=all_people
        )

    def parse_json(self, text):
        text = text.strip()
        if text.startswith("```json"):
            text = text.replace("```json", "")
            text = text.replace("```", "")

        try:
            return json.loads(text)

        except Exception:
            logger.warning("Invalid JSON produced by model.")
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
                return json.loads(json_str)
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