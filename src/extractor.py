from google import genai
from google.genai import types
from src.config import Config
import json
import re
from src.utils import setup_logger

logger = setup_logger(__name__)

class PrescriptionExtractor:

    def __init__(self):
        if not Config.GOOGLE_API_KEY:
            raise ValueError("❌ GOOGLE_API_KEY missing")

        self.client = genai.Client(api_key=Config.GOOGLE_API_KEY)

    def extract_data(self, file_path):

        prompt = """
        Extract prescription details in JSON format:

        {
            "date": "",
            "medicines": [],
            "notes": ""
        }

        Return ONLY JSON.
        """

        try:
            import PIL.Image
            img = PIL.Image.open(file_path)

            response = self.client.models.generate_content(
                model=Config.GEMINI_MODEL_NAME,
                contents=[prompt, img]
            )

            text = response.text.strip()

            print("\n🔥 RAW GEMINI RESPONSE:\n", text)

            # Extract JSON safely
            match = re.search(r"\{.*\}", text, re.DOTALL)

            if match:
                return json.loads(match.group())

            return {
                "raw_text": text,
                "medicines": [],
                "notes": "Fallback parsing"
            }

        except Exception as e:
            logger.error(f"❌ Extraction failed: {e}")

            return {
                "error": str(e),
                "medicines": [],
                "notes": "Extraction failed"
            }