import os
import requests
from dotenv import load_dotenv
from urllib.parse import quote
from transformers import pipeline
from config import MODEL_NAME, DEVICE

load_dotenv()
HF_TOKEN = os.getenv("HF_TOKEN")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

HEADERS = {
    "Authorization": f"Bearer {TAVILY_API_KEY}",
    "Content-Type": "application/json"
}

TAVILY_URL = "https://api.tavily.com/search"


def tavily_search(query: str, num_results: int = 5):
    payload = {
        "query": query,
        "search_depth": "advanced",
        "include_answer": True,
        "include_raw_content": False,
        "max_results": num_results
    }
    response = requests.post(TAVILY_URL, headers=HEADERS, json=payload)
    if response.status_code == 200:
        return response.json().get("results", [])
    else:
        return [{"title": "Error", "url": "", "content": response.text}]


def run_research_agent(query: str) -> str:
    try:
        # Run multiple Tavily searches
        search_terms = [
            f"{query} AI strategy",
            f"{query} AI competitors",
            f"AI trends in {query} industry"
        ]

        combined_snippets = []
        links = []
        for term in search_terms:
            results = tavily_search(term)
            for res in results:
                if res.get("content"):
                    combined_snippets.append(res["content"][:300])
                    links.append((res["title"], res["url"]))

        context = "\n\n".join(combined_snippets[:3])

        generator = pipeline(
            "text-generation",
            model=MODEL_NAME,
            device=DEVICE,
            token=HF_TOKEN
        )

        prompt = f"""
        You are a senior market research analyst. Based on the following insights, write a concise, structured summary (~300 words) on the company: its domain, AI strategy, and recent competitors.

        Context:
        {context}

        Summary:
        """

        response = generator(
            prompt,
            max_new_tokens=400,
            num_return_sequences=1,
            temperature=0.7,
            do_sample=True,
            truncation=True,
            pad_token_id=generator.tokenizer.eos_token_id
        )

        output = response[0]["generated_text"].strip()
        summary = output[len(prompt):].strip()

        if links:
            summary += "\n\n### Sources:\n"
            for title, url in links[:5]:
                if title.strip() and url.strip():
                    summary += f"- [{title}]({url})\n"

        return summary

    except Exception as e:
        return f"Error: {str(e)}"


if __name__ == "__main__":
    print("🔎 Testing Tavily search with 'Tesla AI'")
    print(run_research_agent("Tesla"))