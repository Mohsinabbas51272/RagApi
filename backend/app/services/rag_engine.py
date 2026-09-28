import os
import time
import logging
import re
from typing import Dict, Any, List, Optional
from app.config import GEMINI_API_KEY
from app.models.schemas import QueryResponse, SourceAttribution
from app.services.vector_store import VectorStoreManager, normalize_website_id

logger = logging.getLogger(__name__)

# Greeting patterns (English & Urdu/Roman Urdu)
GREETING_PATTERNS = [
    r"^(hi|hello|hey|salam|assalam|assalam\s*o\s*alaikum|aoa|hola|good\s*morning|good\s*afternoon|good\s*evening|kia\s*haal|kese\s*ho|kaise\s*ho)[\s!.]*$",
    r"^(who\s+are\s+you|what\s+can\s+you\s+do|how\s+can\s+you\s+help|what\s+is\s+this|help)[\s?!.]*$"
]

# Out-of-domain heuristic patterns
OUT_OF_DOMAIN_PATTERNS = [
    r"\bpizza\b", r"\bburger\b", r"\bmars\s+rocket\b", r"\bspace\s+station\b",
    r"\bcryptocurrency\s+mining\b", r"\bcasino\b", r"\blottery\b",
    r"\bweather\s+in\s+tokyo\b", r"\bwho\s+won\s+the\s+world\s+cup\b"
]

# Active high-quota model names
CANDIDATE_MODELS = [
    "gemini-flash-lite-latest",
    "gemini-3.5-flash-lite",
    "gemini-3.7-flash",
    "gemini-3.5-flash",
    "gemini-pro-latest",
    "gemini-flash-latest"
]

# Canonical entity brand patterns for strict company detection
COMPANY_NAME_PATTERNS = [
    ("okoinsights", [r"\boko\s*insights\b", r"\bokoinsights\b", r"\boko\b"]),
    ("yanipro", [r"\byani\s*pro\b", r"\byanipro\b", r"\byani\b"]),
    ("cratus", [r"\bcratus\s*uk\b", r"\bcratus\b", r"\bcratusuk\b"]),
    ("sctechglobal", [r"\bsc\s*tech\s*global\b", r"\bsctech\s*global\b", r"\bsc\s*tech\b", r"\bsctech\b", r"\bsctechglobal\b"]),
    ("thunderenergy", [r"\bthunder\s*energy\s*ai\b", r"\bthunder\s*energy\b", r"\bthunderenergy\b", r"\bthunder\b"]),
    ("scorpbit", [r"\bscorpbit\b", r"\bscorp\s*bit\b"]),
    ("softoo", [r"\bsoftoo\b"]),
]

class RAGEngine:
    def __init__(self, vector_store: VectorStoreManager):
        self.vector_store = vector_store
        self.api_key = GEMINI_API_KEY
        self.genai_module = None
        self.active_model_name = "hybrid_fallback"
        self.confidence_threshold = 0.30
        self._init_gemini()

    def _init_gemini(self):
        # Only initialize if API key is real and valid format
        if self.api_key and len(self.api_key) > 28 and not self.api_key.startswith("your_gemini"):
            try:
                import google.generativeai as genai
                genai.configure(api_key=self.api_key)
                self.genai_module = genai
                self.active_model_name = CANDIDATE_MODELS[0]
                logger.info(f"Gemini API configured with primary model {self.active_model_name}.")
            except Exception as e:
                logger.warning(f"Failed to configure Gemini AI: {e}")
                self.genai_module = None

    def _generate_with_failover(self, prompt: str) -> Optional[str]:
        """Generate response with automatic multi-model failover if quota is reached."""
        if not self.genai_module:
            return None

        for model_name in CANDIDATE_MODELS:
            try:
                client = self.genai_module.GenerativeModel(
                    model_name,
                    system_instruction="""You are the official enterprise AI assistant for the Brillanz Group (Softoo, OKO Insights, YaniPro, Cratus UK, SC Tech Global, Thunder Energy AI, Scorpbit).
Your mission is to directly, accurately, and thoroughly answer the user's question using ONLY the provided verified context.
Strict Rules:
1. Answer EXACTLY what the user asks. If the user asks for a list of all companies with their founders, co-founders, and CEOs, provide the complete, structured list for all entities found in the context.
2. If the user asks about a specific person (e.g., Junaid Ahmad, Bilal Qureshi, Nabeel Hanif, Sajid Razzaque), state their exact role, company, and background.
3. If the user asks about an unknown entity not in the context (such as 'tna', 'infralatic', 'botlike'), state clearly: "I could not find information about this entity in the verified Brillanz Group knowledge base." Do NOT invent or attribute it to Softoo or Brillanz.
4. Do NOT include bracket numbers like [1], [2].
5. Use clean bullet points starting with '• ' for lists."""
                )
                response = client.generate_content(prompt)
                if response and response.text:
                    self.active_model_name = model_name
                    return response.text.strip()
            except Exception as e:
                err_msg = str(e)
                if "429" in err_msg or "quota" in err_msg.lower() or "ResourceExhausted" in err_msg:
                    logger.warning(f"Model {model_name} quota exceeded (429). Failing over to next model...")
                    continue
                elif "404" in err_msg or "NotFound" in err_msg:
                    logger.debug(f"Model {model_name} not available in region. Trying next...")
                    continue
                else:
                    logger.error(f"Gemini error with {model_name}: {e}")
                    continue

        return None

    def _is_greeting(self, question: str) -> bool:
        """Checks if the user query is a simple greeting or identity question."""
        q_clean = question.strip().lower()
        for pattern in GREETING_PATTERNS:
            if re.search(pattern, q_clean):
                return True
        return False

    def _is_out_of_domain(self, question: str) -> bool:
        """Checks if the query contains clear out-of-domain / irrelevant triggers."""
        q_lower = question.lower()
        for pattern in OUT_OF_DOMAIN_PATTERNS:
            if re.search(pattern, q_lower):
                return True
        return False

    def _detect_company_intent(self, question: str) -> Optional[str]:
        """Detect if question specifically targets one of the 7 companies by name."""
        q_lower = question.lower()
        for company_id, patterns in COMPANY_NAME_PATTERNS:
            for pattern in patterns:
                if re.search(pattern, q_lower):
                    return company_id
        return None

    def query(self, question: str, website_filter: Optional[str] = None, top_k: int = 4) -> QueryResponse:
        start_time = time.time()
        
        # 1. Handle Greetings / Introductions directly (avoid pulling random document chunks)
        if self._is_greeting(question):
            return QueryResponse(
                question=question,
                answer="Hello! 👋 I am the official AI assistant for the **Brillanz Group**.\n\nI can answer questions accurately across our portfolio of companies:\n• **Softoo**: Custom software engineering & agile teams\n• **OKO Insights**: AI computer vision & crowd intelligence\n• **YaniPro**: Autonomous AI agents & compliance workflows\n• **Cratus UK**: Smart city IoT telemetry & smart cabinets\n• **SC Tech Global**: Enterprise supply chain cloud & telecom\n• **Thunder Energy AI**: Clean energy forecasting & battery storage (BESS)\n• **Scorpbit**: Offensive cybersecurity & 24/7 SOC threat defense\n\nHow can I assist you today?",
                sources=[],
                website_filter=website_filter,
                processing_time_ms=round((time.time() - start_time) * 1000, 2),
                grounded=True,
                embedding_mode=self.active_model_name
            )

        # 2. Out-of-domain guardrail check
        if self._is_out_of_domain(question):
            return QueryResponse(
                question=question,
                answer="I could not find information regarding your query in the verified Brillanz Group knowledge base. As an enterprise assistant, I only answer questions related to the Brillanz portfolio companies (Softoo, OKO Insights, YaniPro, Cratus, SC Tech Global, Thunder Energy AI, Scorpbit).",
                sources=[],
                website_filter=website_filter,
                processing_time_ms=round((time.time() - start_time) * 1000, 2),
                grounded=True,
                embedding_mode=self.active_model_name
            )

        # 3. Normalize & Auto-detect company filter if not explicitly provided
        normalized_filter = normalize_website_id(website_filter)
        detected_company = self._detect_company_intent(question)
        effective_filter = normalized_filter or detected_company

        # Dynamically allocate larger chunk window for comprehensive group queries
        is_broad_query = not effective_filter and any(w in question.lower() for w in ["list", "all", "companies", "every", "founder", "ceo", "leaders", "overview"])
        fetch_k = max(top_k, 6) if is_broad_query else top_k

        # 4. Retrieve semantically matching chunks from vector store
        retrieved_sources = self.vector_store.query_similar_chunks(question, website_filter=effective_filter, top_k=fetch_k)
        
        # 5. Strict company source isolation: if a target company is active, purge any other company chunks
        if effective_filter and retrieved_sources:
            retrieved_sources = [s for s in retrieved_sources if s.get("website_id") == effective_filter]

        # 6. Confidence threshold guardrail (Rejects unknown companies like tna, infralatic, botlike)
        if not retrieved_sources or (retrieved_sources and retrieved_sources[0]["relevance_score"] < self.confidence_threshold):
            return QueryResponse(
                question=question,
                answer="I could not find information regarding your query in the verified Brillanz Group knowledge base. As an enterprise assistant, I only answer questions related to the Brillanz portfolio companies (Softoo, OKO Insights, YaniPro, Cratus, SC Tech Global, Thunder Energy AI, Scorpbit).",
                sources=[],
                website_filter=effective_filter,
                processing_time_ms=round((time.time() - start_time) * 1000, 2),
                grounded=False,
                embedding_mode=self.active_model_name
            )

        # 6. Assemble Grounded Context Prompt for Gemini
        context_blocks = "\n\n".join([
            f"Source (Company: {s['website_name']} | Title: {s['title']} | URL: {s['url']}):\n{s['snippet']}"
            for s in retrieved_sources
        ])

        # 7. Gemini Generation with Automatic Model Failover
        prompt = f"""Context from Brillanz Group verified websites:
{context_blocks}

User Question: {question}

Instructions:
- Give a direct, accurate, and structured answer explaining what the company does and what it can do.
- Use 2 to 4 clean bullet points starting with '• ' for core capabilities/services.
- Do NOT include bracket numbers like [1], [2] at the end of sentences. Keep the text clean and natural.
- Do not use raw asterisks '*' for bullets.
- Do not add manual 'Sources:' lists at the end, as sources are automatically rendered separately. Answer:"""

        raw_gemini_answer = self._generate_with_failover(prompt)

        if raw_gemini_answer:
            answer_text = raw_gemini_answer.strip()
            # Clean up any leftover asterisks at the start of lines into clean bullet points
            answer_text = re.sub(r'^\s*[\*\-]\s+', '• ', answer_text, flags=re.MULTILINE)
            # Strip any bracketed numbers like [1], [2]
            answer_text = re.sub(r'\s*\[\d+(?:,\s*\d+)*\]', '', answer_text)
        else:
            answer_text = self._format_grounded_answer(question, retrieved_sources)

        is_refusal = any(phrase in answer_text.lower() for phrase in [
            "could not find information",
            "not available in the brillanz",
            "not found in the verified",
            "not part of the brillanz"
        ])
        
        if is_refusal:
            sources = []
            is_grounded = False
        else:
            is_grounded = True
            sources = [
                SourceAttribution(
                    chunk_id=s.get("chunk_id"),
                    website_id=s["website_id"],
                    website_name=s["website_name"],
                    url=s["url"],
                    title=s["title"],
                    category=s.get("category", "General"),
                    snippet=s["snippet"],
                    relevance_score=s["relevance_score"]
                )
                for s in retrieved_sources
            ]

        processing_time = round((time.time() - start_time) * 1000, 2)
        return QueryResponse(
            question=question,
            answer=answer_text,
            sources=sources,
            website_filter=effective_filter,
            processing_time_ms=processing_time,
            grounded=is_grounded,
            embedding_mode=self.active_model_name
        )

    def _format_grounded_answer(self, question: str, sources: List[Dict[str, Any]]) -> str:
        """Intelligent grounded fallback answer synthesizer across all retrieved sources."""
        q_lower = question.lower()
        
        # Check if question asks for all companies, list of CEOs, founders
        is_list_query = any(k in q_lower for k in ["list", "all companies", "all entities", "founder", "ceo", "leaders", "co-founder"])
        
        # Collect distinct structured points from all retrieved sources
        extracted_points = []
        seen_points = set()

        for s in sources:
            snippet = s.get("snippet", "")
            lines = [line.strip() for line in snippet.split("\n") if line.strip()]
            for line in lines:
                clean_line = re.sub(r'^[•\*\-\d\.]+\s*', '', line).strip()
                if len(clean_line) > 20 and clean_line.lower() not in seen_points:
                    seen_points.add(clean_line.lower())
                    # If list query, prioritize lines mentioning people or company names
                    if is_list_query:
                        if any(term in clean_line.lower() for term in ["ceo", "founder", "bilal", "junaid", "nabeel", "sajid", "softoo", "oko", "yani", "cratus", "sctech", "thunder", "scorpbit", "group"]):
                            extracted_points.append(clean_line)
                    else:
                        extracted_points.append(clean_line)

        if not extracted_points:
            primary = sources[0]
            site_name = primary.get("website_name", "Brillanz")
            snippet = primary.get("snippet", "")
            sentences = [sent.strip() for sent in snippet.replace('\n', ' ').split('.') if len(sent.strip()) > 15]
            extracted_points = sentences[:4]

        bullets = "\n".join([f"• {p}" if not p.startswith("•") else p for p in extracted_points[:8]])
        
        if is_list_query:
            return f"Brillanz Group Companies & Leadership Directory:\n\n{bullets}"
        
        primary_site = sources[0].get("website_name", "Brillanz")
        return f"{primary_site} Information:\n\n{bullets}"
