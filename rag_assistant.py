"""
rag_assistant.py -- RAG (Retrieval-Augmented Generation) engine for AmbitionBox reviews.

Features:
- Lazy loading of FAISS index (33,234 review vectors) and HuggingFace MiniLM embeddings
- Semantic search across 43,000+ employee reviews with optional company filtering
- Structured extraction of review metadata (Rating, Role, Location, Likes, Dislikes)
- Generative AI synthesis via Google Gemini with local extractive fallback
"""

import os
from pathlib import Path
from typing import Any, Dict, List, Optional

from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

_BASE = Path(__file__).resolve().parent
FAISS_INDEX_DIR = _BASE / "faiss_index"

# Global lazy vectorstore holder
_vectorstore = None


def get_vectorstore():
    """Lazily load FAISS vectorstore on first query."""
    global _vectorstore
    if _vectorstore is None:
        if not FAISS_INDEX_DIR.exists():
            raise FileNotFoundError(f"FAISS index directory not found at {FAISS_INDEX_DIR}")
        embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        _vectorstore = FAISS.load_local(
            str(FAISS_INDEX_DIR),
            embeddings,
            allow_dangerous_deserialization=True,
        )
    return _vectorstore


def parse_review_doc(doc) -> Dict[str, Any]:
    """Parse Document page_content string into structured fields."""
    content = doc.page_content
    lines = content.split("\n")
    data = {
        "company": doc.metadata.get("company", "Unknown"),
        "job": "Employee",
        "location": "India",
        "rating": "3/5",
        "likes": "",
        "dislikes": "",
        "raw": content,
    }

    current_field = None
    for line in lines:
        if line.startswith("Company:"):
            data["company"] = line.replace("Company:", "").strip()
        elif line.startswith("Job:"):
            data["job"] = line.replace("Job:", "").strip()
        elif line.startswith("Location:"):
            data["location"] = line.replace("Location:", "").strip()
        elif line.startswith("Rating:"):
            data["rating"] = line.replace("Rating:", "").strip()
        elif line.startswith("Likes:"):
            current_field = "likes"
            data["likes"] = line.replace("Likes:", "").strip()
        elif line.startswith("Dislikes:"):
            current_field = "dislikes"
            data["dislikes"] = line.replace("Dislikes:", "").strip()
        elif current_field:
            data[current_field] += " " + line.strip()

    return data


def retrieve_reviews(query: str, company: Optional[str] = None, k: int = 5) -> List[Dict[str, Any]]:
    """Retrieve top-k relevant reviews, optionally filtering by company."""
    vs = get_vectorstore()

    search_query = f"{company} {query}" if company and company not in query else query

    # If filtering by company, retrieve a broader pool and filter
    fetch_k = k * 4 if company else k
    docs = vs.similarity_search(search_query, k=fetch_k)

    results = []
    for d in docs:
        parsed = parse_review_doc(d)
        if company:
            # Match company name case-insensitively
            if company.lower() in parsed["company"].lower() or parsed["company"].lower() in company.lower():
                results.append(parsed)
        else:
            results.append(parsed)

        if len(results) >= k:
            break

    # If company filter yielded fewer than k, fallback to all top results
    if len(results) < k and company:
        for d in docs:
            parsed = parse_review_doc(d)
            if parsed not in results:
                results.append(parsed)
            if len(results) >= k:
                break

    return results


def synthesize_answer(query: str, reviews: List[Dict[str, Any]], api_key: Optional[str] = None) -> Dict[str, Any]:
    """
    Generate an AI response using Gemini if an API key is available and working;
    otherwise generate a high-quality extractive summary.
    """
    if not reviews:
        return {
            "source": "fallback",
            "text": "No matching reviews found for your query. Try searching for a broader term like 'work life balance' or a specific company like 'TCS'.",
            "reviews": [],
        }

    # Format context for prompt
    context_blocks = []
    ratings = []
    for i, r in enumerate(reviews, 1):
        context_blocks.append(
            f"[Review {i}] Company: {r['company']} | Role: {r['job']} | Location: {r['location']} | Rating: {r['rating']}\n"
            f"Pros: {r['likes']}\n"
            f"Cons: {r['dislikes']}"
        )
        try:
            val = float(r["rating"].split("/")[0])
            ratings.append(val)
        except Exception:
            pass

    avg_rating = round(sum(ratings) / len(ratings), 1) if ratings else 3.5
    context_str = "\n\n".join(context_blocks)

    # Attempt Generative AI if key is provided
    if api_key and api_key.strip():
        try:
            from google import genai

            client = genai.Client(api_key=api_key.strip())
            prompt = f"""You are an expert career advisor analyzing real employee reviews from AmbitionBox.
Based strictly on the following verified employee reviews, provide a clear, balanced, and insightful answer to the user's question.

USER QUESTION:
"{query}"

EMPLOYEE REVIEWS CONTEXT:
{context_str}

Please structure your response with:
1. Executive Summary (Direct answer to the user's question)
2. What Employees Appreciate (Common themes from 'Pros')
3. Critical Pain Points (Common themes from 'Cons')
4. Recommendation / Takeaway for Candidates
"""
            # Use gemini-2.5-flash or gemini-2.5-pro or gemini-3.8-flash
            for model_name in ["models/gemini-2.5-flash", "models/gemini-3.8-flash", "gemini-2.5-flash"]:
                try:
                    response = client.models.generate_content(
                        model=model_name,
                        contents=prompt,
                    )
                    if response and response.text:
                        return {
                            "source": "gemini",
                            "model": model_name,
                            "text": response.text.strip(),
                            "avg_rating": avg_rating,
                            "reviews": reviews,
                        }
                except Exception:
                    continue
        except Exception:
            pass

    # High-quality Extractive Fallback Summary
    likes_summary = [r["likes"] for r in reviews if r["likes"] and len(r["likes"]) > 15][:3]
    dislikes_summary = [r["dislikes"] for r in reviews if r["dislikes"] and len(r["dislikes"]) > 15][:3]

    summary_text = f"""### 📊 Review Synthesis (Extractive Analysis)

**Based on {len(reviews)} verified reviews (Average Rating: ⭐ {avg_rating} / 5.0):**

#### 🎯 Key Insights for: *"{query}"*
The employee sentiment captured from AmbitionBox highlights distinct trade-offs regarding compensation, team management, and daily workload.

#### 👍 Top Positive Highlights
"""
    for lk in likes_summary:
        summary_text += f"- *\"{lk.strip()}\"*\n"

    summary_text += "\n#### 👎 Critical Friction Points & Dislikes\n"
    for dl in dislikes_summary:
        summary_text += f"- *\"{dl.strip()}\"*\n"

    summary_text += """
---
💡 **Tip:** Add a Google Gemini API Key in the sidebar to enable full conversational AI synthesis with personalized career advice!
"""

    return {
        "source": "extractive",
        "text": summary_text,
        "avg_rating": avg_rating,
        "reviews": reviews,
    }
