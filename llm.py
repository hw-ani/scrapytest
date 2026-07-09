'''
SECOND DRAFT

import json
import re

from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
)

from scrapytest.models import ResponseModel
from scrapytest.prompts import build_prompt


class RelationshipExtractor:

    def __init__(
        self,
        model_name="Qwen/Qwen2.5-3B-Instruct",
        max_new_tokens=1024,
    ):

        print("Loading tokenizer...")

        self.tokenizer = AutoTokenizer.from_pretrained(
            model_name,
            trust_remote_code=True,
        )

        print("Loading model (CPU)...")

        self.model = AutoModelForCausalLM.from_pretrained(
            model_name,
            trust_remote_code=True,
            device_map=None,      # CPU only
            torch_dtype=None
        )

        self.model.eval()

        self.max_new_tokens = max_new_tokens

        print("Model loaded successfully!")

    ##############################################################

    def extract(
        self,
        page_text: str,
        source_url: str,
    ) -> ResponseModel:

        prompt = build_prompt(page_text)

        messages = [
            {
                "role": "system",
                "content": "You are an information extraction assistant."
            },
            {
                "role": "user",
                "content": prompt
            }
        ]

        text = self.tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True,
        )

        inputs = self.tokenizer(
            text,
            return_tensors="pt",
        )

        outputs = self.model.generate(
            **inputs,
            max_new_tokens=self.max_new_tokens,
            temperature=0.0,
            do_sample=False,
            pad_token_id=self.tokenizer.eos_token_id,
        )

        generated = self.tokenizer.decode(
            outputs[0][inputs.input_ids.shape[1]:],
            skip_special_tokens=True,
        )

        return self.parse_json(
            generated,
            source_url,
        )

    ##############################################################

    def parse_json(
        self,
        text: str,
        source_url: str,
    ) -> ResponseModel:

        text = text.strip()

        # Remove markdown if present
        text = re.sub(r"^```json", "", text)
        text = re.sub(r"^```", "", text)
        text = re.sub(r"```$", "", text)

        text = text.strip()

        try:

            data = json.loads(text)

        except Exception:

            print("\nInvalid JSON returned by LLM:\n")
            print(text)

            return ResponseModel(
                people=[]
            )

        ##############################################################
        # Add source URL automatically
        ##############################################################

        for person in data.get("people", []):

            relationships = person.get(
                "relationships",
                {},
            )

            for rel in relationships.get(
                "groups_projects_programs",
                [],
            ):
                rel["source_url"] = source_url

            for rel in relationships.get(
                "waiting_events",
                [],
            ):
                rel["source_url"] = source_url

            for rel in relationships.get(
                "event_participation",
                [],
            ):
                rel["source_url"] = source_url

        ##############################################################

        try:

            return ResponseModel.model_validate(data)

        except Exception as e:

            print("\nPydantic validation error:\n")
            print(e)

            return ResponseModel(
                people=[]
            )
'''

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
            device=-1,           # CPU
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