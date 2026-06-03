import json
import re
from google import genai
from src.config import Config
from src.utils import setup_logger
from src.otc_data import OTC_LIST_DATA

logger = setup_logger(__name__)

class OTCManager:
    OTC_LIST = OTC_LIST_DATA

    def __init__(self):
        # ✅ NEW GEMINI CLIENT
        self.client = genai.Client(api_key=Config.GOOGLE_API_KEY)

        # Vector Store
        from src.vector_store import VectorStoreManager
        self.vector_store = VectorStoreManager()

        self.otc_namespace = "otc_medicines"
        self._initialize_otc_db()

    def _initialize_otc_db(self):
        try:
            logger.info("Initializing OTC Vector DB...")

            texts = [item['medicine_name'] for item in self.OTC_LIST]

            metadatas = []
            for item in self.OTC_LIST:
                meta = item.get('metadata', {}).copy()
                meta['source'] = 'general_otc_list'
                metadatas.append(meta)

            self.vector_store.add_texts(
                texts,
                metadatas,
                namespace=self.otc_namespace
            )

            logger.info("OTC List Ingested into Pinecone.")

        except Exception as e:
            logger.error(f"Failed to initialize OTC DB: {e}")

    def search_otc_db(self, query, top_k=10):
        matches = self.vector_store.search(
            query,
            namespace=self.otc_namespace,
            top_k=top_k
        )

        results = []
        for m in matches:
            results.append({
                "Medicine Name": m.metadata['text'],
                "Type": m.metadata.get('type', 'Unknown'),
                "Score": round(m.score, 2)
            })

        return results

    def get_otc_list(self):
        return self.OTC_LIST

    def check_medicines_with_llm(self, medicine_list):
        logger.info("Checking medicines against OTC list using Vector + Gemini 2.5")

        results = {"otc_medicines": [], "consult_medicines": []}

        for med in medicine_list:
            med_str = str(med)

            # 🔍 VECTOR SEARCH
            matches = self.vector_store.search(
                med_str,
                namespace=self.otc_namespace,
                top_k=3
            )

            candidates = [
                m.metadata['text'] for m in matches if m.score > 0.7
            ]

            if not candidates:
                results["consult_medicines"].append({
                    "name": med_str.split('(')[0],
                    "reason": "No OTC match found"
                })
                continue

            candidates_str = "\n".join(candidates)

            prompt = f"""
            You are a medical assistant.

            Check if the medicine matches any OTC candidate.

            Extracted Medicine: {med_str}

            Candidates:
            {candidates_str}

            Return JSON:
            {{
                "is_otc": true/false,
                "matched_candidate": "",
                "reason": ""
            }}
            """

            try:
                # ✅ NEW GEMINI CALL
                response = self.client.models.generate_content(
                    model=Config.GEMINI_MODEL_NAME,
                    contents=prompt
                )

                text = response.text.strip()

                print("\n🔥 OTC RAW RESPONSE:\n", text)

                # 🔥 CLEAN JSON
                if "```" in text:
                    text = text.split("```")[1].replace("json", "").strip()

                match = re.search(r"\{.*\}", text, re.DOTALL)

                if match:
                    verification = json.loads(match.group())
                else:
                    raise ValueError("JSON not found")

                name_clean = med_str.split(':')[0].strip("- ").strip()

                if verification.get("is_otc"):
                    results["otc_medicines"].append({
                        "name": name_clean,
                        "reason": f"Matched with {verification.get('matched_candidate')}"
                    })
                else:
                    results["consult_medicines"].append({
                        "name": name_clean,
                        "reason": verification.get("reason", "Not OTC")
                    })

            except Exception as e:
                logger.error(f"Error checking {med_str}: {e}")

                results["consult_medicines"].append({
                    "name": med_str,
                    "reason": "Verification failed"
                })

        return results