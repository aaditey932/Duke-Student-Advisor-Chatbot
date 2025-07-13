from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException
import time
import json
import os
import random
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='rmp_scraper.log',
    filemode='w'
)
console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
console.setFormatter(formatter)
logging.getLogger('').addHandler(console)

def setup_driver():
    options = Options()
    # Essential options to avoid detection
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    
    # Options to handle graphics issues
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-software-rasterizer")
    options.add_argument("--disable-webgl")
    options.add_argument("--disable-dev-shm-usage")
    
    # General options
    options.add_argument("--no-sandbox")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--incognito")
    
    # User agent rotation
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15"
    ]
    options.add_argument(f"user-agent={random.choice(user_agents)}")
    
    # Comment the next line if you want to see the browser
    # options.add_argument("--headless")
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    
    # Execute CDP commands to avoid detection
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": '''
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
        '''
    })
    
    return driver

def wait_for_element(driver, by, selector, timeout=15, condition=EC.presence_of_element_located):
    """Wait for an element with explicit logging and retries"""
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            wait = WebDriverWait(driver, 5)
            element = wait.until(condition((by, selector)))
            logging.info(f"Found element {selector}")
            return element
        except (TimeoutException, StaleElementReferenceException) as e:
            logging.warning(f"Retry finding {selector}: {str(e)}")
            time.sleep(1)
    
    logging.error(f"Failed to find element {selector} after {timeout} seconds")
    return None

def accept_cookies(driver):
    """Try multiple methods to accept cookies"""
    try:
        selectors = [
            (By.ID, "onetrust-accept-btn-handler"),
            (By.XPATH, "//button[contains(text(), 'Accept')]"),
            (By.XPATH, "//button[contains(text(), 'Accept All')]"),
            (By.XPATH, "//button[contains(@class, 'cookie')]")
        ]
        
        for by, selector in selectors:
            try:
                element = wait_for_element(driver, by, selector, timeout=5, 
                                          condition=EC.element_to_be_clickable)
                if element:
                    element.click()
                    logging.info(f"Clicked cookie consent using {selector}")
                    time.sleep(2)
                    return True
            except Exception as e:
                logging.debug(f"No cookie button found with {selector}: {str(e)}")
                continue
                
        logging.info("No cookie consent prompt found or already accepted")
        return False
    except Exception as e:
        logging.warning(f"Error handling cookies: {str(e)}")
        return False

def get_professor_card_selector(driver):
    """Find the correct selector for professor cards"""
    selectors = [
        '.TeacherCard__StyledTeacherCard-syjs0d-0',
        '[data-testid="TeacherCard"]',
        '.CardRoot-vjwzfl-0'
    ]
    
    for selector in selectors:
        cards = driver.find_elements(By.CSS_SELECTOR, selector)
        if cards:
            logging.info(f"Found professor cards using selector: {selector}")
            return selector
    
    return None

def extract_professor_data(card):
    """Extract data from a single professor card"""
    prof_data = {
        'name': 'Unknown',
        'department': 'Unknown',
        'rating': 'N/A',
        'would_take_again': 'N/A',
        'num_ratings': 'N/A'
    }
    
    try:
        # Extract professor name
        name_selectors = [
            '[data-testid="cardName"]', 
            '.CardName__StyledCardName-sc-1gyrgim-0',
            '.NameTitle__Name-dowf0z-0'
        ]
        
        for selector in name_selectors:
            try:
                name_elem = card.find_element(By.CSS_SELECTOR, selector)
                prof_data['name'] = name_elem.text.strip()
                break
            except:
                continue
        
        # Extract department
        dept_selectors = [
            '[data-testid="cardSchoolName"]',
            '.CardSchool__Department-sc-19lmz2k-0',
            '.CardSchool__School-sc-19lmz2k-1'
        ]
        
        for selector in dept_selectors:
            try:
                dept_elem = card.find_element(By.CSS_SELECTOR, selector)
                prof_data['department'] = dept_elem.text.strip()
                break
            except:
                continue
        
        # Extract rating
        rating_selectors = [
            '[data-testid="cardRating"]',
            '.CardNumRating__CardNumRatingNumber-sc-17t4b9u-2',
            '.CardNumRating-xir6a4-0'
        ]
        
        for selector in rating_selectors:
            try:
                rating_elem = card.find_element(By.CSS_SELECTOR, selector)
                prof_data['rating'] = rating_elem.text.strip()
                break
            except:
                continue
        
        # Extract would take again percentage
        wta_selectors = [
            '[data-testid="cardWouldTakeAgain"]',
            '.CardFeedback__CardFeedbackNumber-lq6nix-2',
            '.CardFeedback-xn2mng-0'
        ]
        
        for selector in wta_selectors:
            try:
                wta_elem = card.find_element(By.CSS_SELECTOR, selector)
                wta_text = wta_elem.text.strip()
                # Extract percentage value if it exists
                if "%" in wta_text:
                    prof_data['would_take_again'] = wta_text
                else:
                    prof_data['would_take_again'] = wta_text + "%" if wta_text.replace('.', '').isdigit() else wta_text
                break
            except:
                continue
        
        # Extract number of ratings
        ratings_count_selectors = [
            '[data-testid="cardNumRatings"]',
            '.CardNumRating__CardNumRatingCount-sc-17t4b9u-3',
            '.TeacherInfo__StyledTeacherInfo-ti1fio-0 span'
        ]
        
        for selector in ratings_count_selectors:
            try:
                ratings_count_elem = card.find_element(By.CSS_SELECTOR, selector)
                ratings_text = ratings_count_elem.text.strip()
                
                # Clean up the ratings text
                if "ratings" in ratings_text.lower():
                    # Extract just the number
                    import re
                    numbers = re.findall(r'\d+', ratings_text)
                    if numbers:
                        prof_data['num_ratings'] = numbers[0]
                    else:
                        prof_data['num_ratings'] = ratings_text
                else:
                    prof_data['num_ratings'] = ratings_text
                break
            except:
                continue
        
    except Exception as e:
        logging.warning(f"Error extracting professor data: {str(e)}")
    
    return prof_data

def click_show_more(driver):
    """Try multiple methods to click 'Show More' button"""
    try:
        show_more_selectors = [
            "//button[contains(text(), 'Show More')]",
            "//button[contains(@class, 'PaginationButton')]",
            "//button[contains(@class, 'Buttons__Button')]"
        ]
        
        for selector in show_more_selectors:
            try:
                show_more = driver.find_element(By.XPATH, selector)
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", show_more)
                time.sleep(1)
                show_more.click()
                logging.info(f"Clicked 'Show More' button")
                time.sleep(random.uniform(3, 5))  # Random delay after clicking
                return True
            except:
                continue
        
        return False
    except Exception as e:
        logging.warning(f"Error clicking 'Show More': {str(e)}")
        return False

def save_to_json(professors_data, filename="duke_professors.json"):
    try:
        with open(filename, 'w', encoding='utf-8') as jsonfile:
            json.dump(professors_data, jsonfile, indent=4)
        
        logging.info(f"Successfully saved {len(professors_data)} professors to {filename}")
        logging.info(f"File saved at: {os.path.abspath(filename)}")
    except Exception as e:
        logging.error(f"Error saving to JSON: {str(e)}")

def load_existing_professors(filename="duke_professors.json"):
    """Load existing professor data to avoid duplicates"""
    try:
        if os.path.exists(filename):
            with open(filename, 'r', encoding='utf-8') as jsonfile:
                existing_data = json.load(jsonfile)
                logging.info(f"Loaded {len(existing_data)} existing professors from {filename}")
                return existing_data
        else:
            logging.info(f"No existing file found at {filename}")
            return []
    except Exception as e:
        logging.warning(f"Error loading existing data: {str(e)}")
        return []

def main():
    driver = None
    output_file = "duke_professors.json"
    
    try:
        logging.info("Starting RateMyProfessors scraper for Duke University")
        
        # Load existing data to avoid duplicates
        existing_professors = load_existing_professors(output_file)
        existing_names = {prof['name'] for prof in existing_professors}
        
        driver = setup_driver()
        driver.set_page_load_timeout(30)
        
        logging.info("Opening RateMyProfessors search page for Duke University...")
        
        # Try accessing the site with retry mechanism
        max_retries = 3
        for attempt in range(max_retries):
            try:
                driver.get("https://www.ratemyprofessors.com/search/professors/1350?q=*")
                break
            except Exception as e:
                if attempt < max_retries - 1:
                    logging.warning(f"Failed to load page (attempt {attempt+1}/{max_retries}): {str(e)}")
                    time.sleep(5)
                else:
                    logging.error(f"Failed to load page after {max_retries} attempts: {str(e)}")
                    return
        
        # Wait for page to initialize
        time.sleep(5)
        
        # Handle cookie consent
        accept_cookies(driver)
        
        # Find the correct card selector
        card_selector = get_professor_card_selector(driver)
        if not card_selector:
            logging.error("Could not find professor cards selector")
            return
        
        # Track professors to avoid duplicates during this session
        all_professors = []
        seen_names = existing_names.copy()
        
        # Process all visible professors initially
        visible_cards = driver.find_elements(By.CSS_SELECTOR, card_selector)
        logging.info(f"Initially found {len(visible_cards)} professor cards")
        
        # Process the initial cards
        for i, card in enumerate(visible_cards):
            try:
                prof_data = extract_professor_data(card)
                
                # Add professor if we have at least a valid name and not seen before
                if prof_data['name'] != 'Unknown' and prof_data['name'] not in seen_names:
                    seen_names.add(prof_data['name'])
                    all_professors.append(prof_data)
                    
                    if i < 3 or i % 10 == 0:  # Log a sample of the processed data
                        logging.info(f"Processed professor {i+1}: {prof_data['name']} | "
                                    f"{prof_data['department']} | Rating: {prof_data['rating']} | "
                                    f"Would Take Again: {prof_data['would_take_again']} | "
                                    f"# Ratings: {prof_data['num_ratings']}")
            except Exception as e:
                logging.warning(f"Error processing card {i+1}: {str(e)}")
                continue
        
        # Remember how many cards we've seen so far
        processed_count = len(visible_cards)
        logging.info(f"Initial processing complete. Found {len(all_professors)} professors")
        
        # Continue clicking "Show More" to get more professors
        max_clicks = 302  # Set based on total professors / 8 (new professors per click)
        click_count = 0
        
        while click_count < max_clicks:
            # Try to click "Show More" button
            if not click_show_more(driver):
                logging.info("No more 'Show More' button found, ending collection")
                break
            
            # Get all current cards
            current_cards = driver.find_elements(By.CSS_SELECTOR, card_selector)
            
            # Only process the new cards that appeared
            if len(current_cards) > processed_count:
                new_cards = current_cards[processed_count:]
                logging.info(f"Found {len(new_cards)} new cards after clicking 'Show More'")
                
                # Process just the new cards
                new_count = 0
                for i, card in enumerate(new_cards):
                    try:
                        prof_data = extract_professor_data(card)
                        
                        # Add professor if valid and not seen before
                        if prof_data['name'] != 'Unknown' and prof_data['name'] not in seen_names:
                            seen_names.add(prof_data['name'])
                            all_professors.append(prof_data)
                            new_count += 1
                            
                            if i < 3 or i % 10 == 0:  # Log a sample
                                logging.info(f"New professor {new_count}: {prof_data['name']} | "
                                            f"{prof_data['department']} | Rating: {prof_data['rating']}")
                    except Exception as e:
                        logging.warning(f"Error processing new card {i+1}: {str(e)}")
                        continue
                
                # Update our counter of processed cards
                processed_count = len(current_cards)
                logging.info(f"Found {new_count} new professors after click {click_count+1}")
                
                # Break if we didn't find any new professors
                if new_count == 0:
                    logging.info("No new professors found, possibly reached the end")
                    # One more chance - sometimes there's a rendering delay
                    time.sleep(2)
                    continue
            else:
                logging.info("No new cards appeared after clicking 'Show More'")
                # Give it one more chance - sometimes there's a loading delay
                time.sleep(3)
            
            click_count += 1
            
            # Save intermediately every 10 clicks to avoid losing data
            if click_count % 10 == 0:
                combined_professors = existing_professors.copy()
                for prof in all_professors:
                    if prof['name'] not in existing_names:
                        combined_professors.append(prof)
                save_to_json(combined_professors, f"{output_file}.partial")
                logging.info(f"Saved partial results with {len(combined_professors)} professors")
        
        # Combine with existing data
        combined_professors = existing_professors.copy()
        
        # Add new professors that weren't in the existing data
        for prof in all_professors:
            if prof['name'] not in existing_names:
                combined_professors.append(prof)
        
        # Print summary
        logging.info(f"Data collection complete. Found {len(all_professors)} new professors")
        logging.info(f"Total professors after combining with existing data: {len(combined_professors)}")
        
        # Save final results to JSON
        save_to_json(combined_professors, output_file)
        
    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}")
    finally:
        if driver:
            driver.quit()
            logging.info("Driver closed successfully")

if __name__ == "__main__":
    main()