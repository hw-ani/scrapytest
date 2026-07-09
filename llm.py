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
                max_new_tokens=768,
                do_sample=False,
                temperature=0.0,
                return_full_text=False,
            )

            output = result[0]["generated_text"]

            parsed = self.parse_json(output)

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