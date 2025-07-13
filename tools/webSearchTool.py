import requests
import os
from bs4 import BeautifulSoup
from readability import Document
from langchain_core.tools import tool

def fetch_page_content(url):
    """Scrapes the given URL and extracts clean text content along with metadata."""
    headers = {"User-Agent": "Mozilla/5.0"} 
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        doc = Document(response.text)
        soup = BeautifulSoup(doc.summary(), "html.parser")
        extracted = soup.get_text()

        return {
            "title": Document(response.text).title(),
            "content": extracted.strip(),
            "restricted": "NO",
            "url": url
        }

    except requests.exceptions.RequestException as e:
        return {"title" : "", "content": str(e), "restricted" : "YES", "url": url}

@tool
def web_search(query):
    """
    **FALLBACK TOOL**: Search the web for Duke information not covered by specialized tools.
    
    **Use as LAST RESORT when:**
    - Specialized tools don't have sufficient information
    - Query is about very recent developments or news
    - Looking for student organizations, clubs, or activities
    - Seeking information about policies not in databases
    - Need current/real-time information
    
    **Don't use first**: Always try relevant specialized tools before web search
    
    Example: "What AI student clubs exist at Duke?" (after other tools don't provide this)
    """

    num_results = 3
    API_KEY = os.getenv("GOOGLE_API_KEY")
    SEARCH_ENGINE_ID = os.getenv("GOOGLE_SEARCH_ENGINE_ID")
    
    search_url = f"https://www.googleapis.com/customsearch/v1?q={query}&key={API_KEY}&cx={SEARCH_ENGINE_ID}"

    response = requests.get(search_url)
    urls = []
    if response.status_code == 200:
        results = response.json()
        for item in results.get("items", [])[:num_results]:
            url = item["link"]
            urls.append(url)
    else:
        print("Failed to fetch search results.")

    all_content = []
    for url in urls:
        content = fetch_page_content(url)
        all_content.append(content)

    return all_content


if __name__ == "__main__":
    print(web_search("What is the best way to learn about the AIPI program at Duke University?"))
