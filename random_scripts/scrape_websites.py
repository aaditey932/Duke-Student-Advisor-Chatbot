import os
import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urlparse

def create_output_folder(folder_name="scraped_websites"):
    """Create folder to store scraped content if it doesn't exist."""
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)
    return folder_name

def clean_filename(title):
    """Convert title to a valid filename."""
    # Replace invalid filename characters with underscores
    clean_title = re.sub(r'[\\/*?:"<>|]', "_", title)
    # Limit filename length
    if len(clean_title) > 100:
        clean_title = clean_title[:100]
    # Make sure we have something to use as filename
    if not clean_title or clean_title.isspace():
        clean_title = "unnamed_website"
    return clean_title + ".txt"

def extract_main_content(soup):
    """Extract the main content from the webpage, removing irrelevant elements."""
    # Remove script, style, header, footer, nav, and other non-content elements
    for element in soup(['script', 'style', 'header', 'footer', 'nav', 'aside', 'form', 'iframe']):
        element.decompose()
    
    # Try to find main content containers
    main_content = soup.find('main') or soup.find('article') or soup.find(id=re.compile('content|main', re.I))
    
    # If we found a specific content container, use it; otherwise use body
    content_container = main_content if main_content else soup.body
    
    if content_container:
        # Get all text, stripping extra whitespace
        text = content_container.get_text(separator=' ')
        # Remove excessive whitespace/newlines
        text = re.sub(r'\s+', ' ', text)
        # Remove empty lines
        text = re.sub(r'^\s*$', '', text, flags=re.MULTILINE)
        return text.strip()
    
    return "No content extracted"

def scrape_website(url, output_folder):
    """Scrape content from a website and save to a text file."""
    try:
        # Send request with a user agent to avoid being blocked
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()  # Raise exception for 4XX/5XX responses
        
        # Parse the HTML content
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Get the title of the page
        title = soup.title.string if soup.title else urlparse(url).netloc
        
        # Clean the title to use as filename
        filename = clean_filename(title)
        
        # Extract main content
        content = extract_main_content(soup)
        
        # Save content to file
        file_path = os.path.join(output_folder, filename)
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(content)
        
        print(f"Successfully scraped: {url} -> {filename}")
        return True
    
    except Exception as e:
        print(f"Error scraping {url}: {e}")
        return False

def main():
    # List of websites to scrape
    websites = [
        "https://ai.meng.duke.edu/faculty/jon-reifschneider",
        "https://ai.meng.duke.edu/faculty/jeffrey-glass",
        "https://ai.meng.duke.edu/faculty/yiran-chen",
        "https://ai.meng.duke.edu/faculty/lawrence-carin",
        "https://ai.meng.duke.edu/faculty/richard-telford",
        "https://ai.meng.duke.edu/faculty/theodore-ryan",
        "https://ai.meng.duke.edu/faculty/jeffrey-ward",
        "https://ai.meng.duke.edu/industry",
        "https://ai.meng.duke.edu/news/where-are-stem-jobs-north-carolinas-charlotte-no-1-and-raleigh-no-5-new-index",
        "https://ai.meng.duke.edu/news/dukes-new-masters-degree-applies-ai-product-innovation",
        "https://ai.meng.duke.edu/news/using-ai-teach-ai-dukes-master-engineering-degree-program",
        "https://ai.meng.duke.edu/faculty/noah-gift",
        "https://ai.meng.duke.edu/faculty/natalia-summerville",
        "https://ai.meng.duke.edu/faculty/wann-jiun-ma",
        "https://ai.meng.duke.edu/news/shining-spotlight-eduardo-martinez",
        "https://ai.meng.duke.edu/news/shining-spotlight-shyamal-anadkat22",
        "https://ai.meng.duke.edu/news/shining-spotlight-diarra-bell",
        "https://ai.meng.duke.edu/faculty/alfredo-deza",
        "https://ai.meng.duke.edu/faculty/brad-fox",
        "https://ai.meng.duke.edu/contact",
        "https://masters.pratt.duke.edu/people/brinnae-bent/",
        "https://masters.pratt.duke.edu/people/xu-chen/",
        "https://masters.pratt.duke.edu/people/yiran-chen/",
        "https://masters.pratt.duke.edu/people/alfredo-deza/",
        "https://masters.pratt.duke.edu/people/brad-fox/",
        "https://scholars.duke.edu/person/Noah.Gift",
        "https://masters.pratt.duke.edu/people/jeffrey-glass/",
        "https://masters.pratt.duke.edu/people/michael-mazzoleni/",
        "https://masters.pratt.duke.edu/people/jon-reifschneider/",
        "https://masters.pratt.duke.edu/people/theodore-ryan/",
        "https://masters.pratt.duke.edu/people/pramod-singh/",
        "https://masters.pratt.duke.edu/people/natalia-summerville/",
        "https://masters.pratt.duke.edu/people/richard-telford/",
        "https://scholars.duke.edu/person/ward",
        "https://ai.meng.duke.edu/news/dr-brinnae-bent-joins-duke-ai-master-engineering-faculty",
        "https://masters.pratt.duke.edu/ai/",
        "https://masters.pratt.duke.edu/ai/overview/",
        "https://masters.pratt.duke.edu/ai/degree/",
        "https://masters.pratt.duke.edu/ai/certificate/",
        "https://masters.pratt.duke.edu/ai/courses/",
        "https://masters.pratt.duke.edu/people?s=&department=artificial-intelligence&group=faculty&submit=Filter",
        "https://masters.pratt.duke.edu/ai/leadership-staff/",
        "https://masters.pratt.duke.edu/ai/news-events/",
        "https://masters.pratt.duke.edu/life/students/",
        "https://masters.pratt.duke.edu/apply/instructions/#h-master-of-engineering-programs",
        "https://masters.pratt.duke.edu/apply/instructions/#international-applicants"

    ]
    
    # Create output folder
    output_folder = create_output_folder()
    
    # Process each website
    successful = 0
    for url in websites:
        if scrape_website(url, output_folder):
            successful += 1
    
    print(f"\nScraping completed. Successfully scraped {successful} out of {len(websites)} websites.")
    print(f"Files saved in folder: {output_folder}")

if __name__ == "__main__":
    main()