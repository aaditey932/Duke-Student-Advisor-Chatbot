import requests
from datetime import datetime
from urllib.parse import quote
import json
import re
from utils.openai_client import get_chat_completion
from openai import OpenAI

# Load groups and categories from the correct relative paths
GROUPS_FILE = "data/eventsData/groups.txt"
CATEGORIES_FILE = "data/eventsData/categories.txt"
OUTPUT_FILE = "data/eventsData/events_output.txt"

with open(GROUPS_FILE, "r") as f:
    groups_list = [line.strip() for line in f if line.strip()]

with open(CATEGORIES_FILE, "r") as f:
    categories_list = [line.strip() for line in f if line.strip()]

def get_event_filters_with_gpt(user_prompt, groups=['All'], categories=['All']):

    system_prompt = """"The year is 2025. You are an assistant that extracts event filters for an event calendar API. Given a user query and lists of valid 'groups' and 'categories', extract:

1. The number of future days (default to 30 if not mentioned)
2. Matching group names from the list
3. Matching category names from the list
4. The specific date (if mentioned, e.g., 'April 18') as YYYY-MM-DD format
5. Location keywords (e.g., 'downtown', 'west campus', 'chapel')

Respond in JSON format as:
{
"future_days": <int>,
"groups": [<list of strings>],
"categories": [<list of strings>],
"target_date": "<optional date in YYYY-MM-DD>",
"location_keywords": [<list of location strings>]
}"""

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"""User query: {user_prompt}

Available groups:
{groups}

Available categories:
{categories}
"""}
    ]
    response = (messages)

    content = response.content.strip()
    if content.startswith("```"):
        content = re.sub(r"```json|```", "", content).strip()

    try:
        return json.loads(content)
    except json.JSONDecodeError:
        # Fallback in case parsing fails
        return {
            "future_days": 30,
            "groups": [],
            "categories": [],
            "target_date": None,
            "location_keywords": []
        }

def fetch_filtered_events(groups=None, categories=None, future_days=1, location_keywords=None, target_date=None):
    base_url = "https://calendar.duke.edu/events/index.json"

    fixed_params = {
        "future_days": future_days,
        "local": "true",
        "feed_type": "simple"
    }

    if isinstance(groups, str):
        groups = [groups]
    if isinstance(categories, str):
        categories = [categories]
        
    query_parts = [f"{key}={value}" for key, value in fixed_params.items()]

    if groups and not ("all" in [g.lower() for g in groups]):
        query_parts += [f"gfu[]={quote(g)}" for g in groups]
    if categories and not ("all" in [c.lower() for c in categories]):
        query_parts += [f"cfu[]={quote(c)}" for c in categories]

    full_url = f"{base_url}?{'&'.join(query_parts)}"
    print(f"\n🔍 Constructed URL: {full_url}\n")

    try:
        response = requests.get(full_url)
        response.raise_for_status()
        data = response.json()

        events = data.get("events", [])
        if not events:
            print("⚠️ No events found for the selected filters.\n")
            return

        print(f"📅 Found {len(events)} events. Saving to file...")

        with open(OUTPUT_FILE, "w", encoding="utf-8") as file:
            file.write(f"🔗 Source URL:\n{full_url}\n\n")
            file.write(f"📅 Found {len(events)} upcoming events:\n\n")
            for event in events:
                title = event.get("summary", "No Title")
                description = event.get("description", "").strip()
                start_ts = event.get("start_timestamp", "")
                location = event.get("location", {}).get("address", "TBD")
                link = event.get("link", "")

                try:
                    start_dt = datetime.strptime(start_ts, "%Y-%m-%dT%H:%M:%SZ")
                    formatted_start = start_dt.strftime("%b %d, %Y %I:%M %p")
                except:
                    formatted_start = start_ts

                if target_date:
                    try:
                        filter_date = datetime.strptime(target_date, "%Y-%m-%d").date()
                        if not start_dt or start_dt.date() != filter_date:
                            continue  # Skip if not the target date
                    except:
                        pass
                
                # Skip if location doesn't match (if location keywords are provided)
                if location_keywords and location:
                    location_lower = location.lower()
                if not any(keyword.lower() in location_lower for keyword in location_keywords):
                    continue

                file.write(f"🔹 {title}\n")
                file.write(f"   🕒 {formatted_start}\n")
                file.write(f"   📍 {location}\n")
                file.write(f"   🔗 {link}\n")
                file.write(f"   📝 {description[:150]}...\n\n" if description else "\n")

        print(f"✅ Saved to {OUTPUT_FILE}\n")

    except Exception as e:
        print(f"❌ Error fetching events: {e}")



def fetch_filtered_events_data(categories=None, future_days=1, groups=None, location_keywords=None, target_date=None):
    base_url = "https://calendar.duke.edu/events/index.json"

    fixed_params = {
        "future_days": future_days,
        "local": "true",
        "feed_type": "simple"
    }

    # Defensive fix
    if isinstance(groups, str):
        groups = [groups]
    if isinstance(categories, str):
        categories = [categories]

    query_parts = [f"{key}={value}" for key, value in fixed_params.items()]

    if groups and not ("all" in [g.lower() for g in groups]):
        query_parts += [f"gfu[]={quote(g)}" for g in groups]
    if categories and not ("all" in [c.lower() for c in categories]):
        query_parts += [f"cfu[]={quote(c)}" for c in categories]

    full_url = f"{base_url}?{'&'.join(query_parts)}"
    print(f"\n🔍 Constructed URL: {full_url}\n")

    try:
        response = requests.get(full_url)
        response.raise_for_status()
        data = response.json()

        events = data.get("events", [])
        if not events:
            return "⚠️ No events found for the selected filters."
        
        events_data = []
        for event in events:
            title = event.get("summary", "No Title")
            description = event.get("description", "").strip()
            start_ts = event.get("start_timestamp", "")
            location = event.get("location", {}).get("address", "TBD")
            link = event.get("link", "")

            try:
                start_dt = datetime.strptime(start_ts, "%Y-%m-%dT%H:%M:%SZ")
                formatted_start = start_dt.strftime("%b %d, %Y %I:%M %p")
            except:
                formatted_start = start_ts

            # Filter by exact date (if provided)
            if target_date:
                try:
                    filter_date = datetime.strptime(target_date, "%Y-%m-%d").date()
                    if not start_dt or start_dt.date() != filter_date:
                        continue  # Skip if not the target date
                except:
                    pass

            # Skip if location doesn't match (if location keywords are provided)
            if location_keywords and location:
                location_lower = location.lower()
                if not any(keyword.lower() in location_lower for keyword in location_keywords):
                    continue

            events_data.append({
                "title": title,
                "start_time": formatted_start,
                "location": location,
                "link": link,
                "description": description[:150] if description else ""
            })

        return events_data

    except Exception as e:
        return f"❌ Error fetching events: {e}"

def get_events(query, api_key=None):
    filters = get_event_filters_with_gpt(query, groups_list, categories_list)

    groups = filters.get("groups", [])
    categories = filters.get("categories", [])
    future_days = filters.get("future_days", 30)

    target_date = filters.get("target_date", None)
    location_keywords = filters.get("location_keywords", [])

    return fetch_filtered_events_data(
        groups=groups,
        categories=categories,
        future_days=future_days,
        target_date=target_date,
        location_keywords=location_keywords
    )
  
if __name__ == "__main__":
    api_key = input("Please enter your OpenAI API Key: ")
    user_query = input("What kind of events are you looking for?\n> ")
    filters = get_event_filters_with_gpt(user_query, groups_list, categories_list)

    print("\n🧠 GPT-Extracted Filters:")
    print(json.dumps(filters, indent=2))

    groups = filters.get("groups", [])
    categories = filters.get("categories", [])
    future_days = filters.get("future_days", 30)
    target_date = filters.get("target_date")
    location_keywords = filters.get("location_keywords", [])

    fetch_filtered_events(
        groups=groups,
        categories=categories,
        future_days=future_days,
        target_date=target_date,
        location_keywords=location_keywords
    )