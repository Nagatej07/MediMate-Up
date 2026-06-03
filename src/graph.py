from typing import TypedDict, List, Optional
from langgraph.graph import StateGraph, END
from src.config import Config
from src.vector_store import VectorStoreManager
from src.memory import MemoryManager
from src.utils import setup_logger, remove_stopwords
from google import genai

logger = setup_logger(__name__)

class GraphState(TypedDict):
    question: str
    prescription_id: Optional[str]
    session_id: str
    language: str
    context: List[str]
    answer: str

class RAGGraph:
    def __init__(self):
        self.vector_store = VectorStoreManager()
        self.memory = MemoryManager()
        self.client = genai.Client(api_key=Config.GOOGLE_API_KEY)

    def retrieve(self, state: GraphState):
        logger.info("Node: Retrieve")

        question = state["question"]
        prescription_id = state.get("prescription_id")

        results = self.vector_store.search(
            query=question,
            prescription_id=prescription_id,
            namespace="prescriptions"   # 🔥 FIX
        )

        context = [m.metadata.get("text", "") for m in results]

        print("🔍 CONTEXT:", context)

        return {"context": context}

    def generate(self, state: GraphState):
        logger.info("Node: Generate")

        question = state["question"]
        context = state.get("context", [])
        language = state.get("language", "English")

        context_str = "\n\n".join(context) if context else "No context"

        history = self.memory.get_history(state["session_id"], limit=5)

        history_str = "\n".join([
            f"{msg['role']}: {remove_stopwords(msg['content'])}"
            for msg in history
        ]) if history else "No history"

        prompt = f"""
        You are a medical assistant.

        Context:
        {context_str}

        Question:
        {question}

        Answer clearly.
        """

        try:
            response = self.client.models.generate_content(
                model=Config.GEMINI_MODEL_NAME,
                contents=prompt
            )

            answer = response.text if response.text else None

            if not answer:
                try:
                    answer = response.candidates[0].content.parts[0].text
                except:
                    answer = "No answer generated"

            print("🔥 ANSWER:", answer)

        except Exception as e:
            logger.error(f"Error: {e}")
            answer = "AI error"

        self.memory.add_message(state["session_id"], "user", question)
        self.memory.add_message(state["session_id"], "ai", answer)

        return {"answer": str(answer)}

    def build_graph(self):
        workflow = StateGraph(GraphState)

        workflow.add_node("retrieve", self.retrieve)
        workflow.add_node("generate", self.generate)

        workflow.set_entry_point("retrieve")
        workflow.add_edge("retrieve", "generate")
        workflow.add_edge("generate", END)

        return workflow.compile()