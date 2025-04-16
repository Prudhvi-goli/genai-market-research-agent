from huggingface_hub import HfApi
import requests
from bs4 import BeautifulSoup
import re

HEADERS = {"User-Agent": "Mozilla/5.0"}


def fetch_kaggle(query):
    url = f"https://www.kaggle.com/search?q={query.replace(' ', '+')}+in%3Adatasets"
    res = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(res.text, "html.parser")
    links = soup.select("a[href*='/datasets/']")
    return f"https://www.kaggle.com{links[0]['href']}" if links else "No Kaggle dataset found"


def fetch_github(query):
    url = f"https://github.com/search?q={query.replace(' ', '+')}+dataset"
    res = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(res.text, "html.parser")
    links = soup.select("a.v-align-middle")
    return f"https://github.com{links[0]['href']}" if links else "No GitHub dataset found"


# More aggressive keyword extraction
KEYWORD_OVERRIDES = {
    "cybersecurity": "tesla cybersecurity",
    "predictive": "tesla predictive analytics",
    "charging": "tesla charging network",
    "self-driving": "tesla self driving",
    "loan": "tesla loan finance ai",
    "analytics": "tesla analytics ai"
}


def extract_keywords(text):
    text = text.lower()
    for key, override in KEYWORD_OVERRIDES.items():
        if key in text:
            return override
    # fallback: extract nouns only, short tail
    clean = re.sub(r"[^a-zA-Z0-9 ]", "", text)
    words = clean.split()
    return "tesla " + " ".join(words[:4])  # fallback short query


def fetch_resources(use_cases):
    api = HfApi()
    resource_dict = {}

    for use_case in use_cases:
        try:
            title_line = next((line for line in use_case.split("\n") if line.lower().startswith("title:")), None)
            query = extract_keywords(title_line) if title_line else "tesla ai"
        except Exception:
            query = "tesla ai"

        print(f"Searching datasets for: {query}")  # Optional debug log

        # HuggingFace
        hf_results = list(api.list_datasets(search=query, limit=1))
        hf_link = f"https://huggingface.co/datasets/{hf_results[0].id}" if hf_results else "No HF dataset found"

        # Kaggle & GitHub
        kaggle_link = fetch_kaggle(query)
        github_link = fetch_github(query)

        resource_dict[query] = {
            "huggingface": hf_link,
            "kaggle": kaggle_link,
            "github": github_link
        }

    return resource_dict