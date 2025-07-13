import requests
from dotenv import load_dotenv
import os
import json
from urllib.parse import quote

load_dotenv()

DUKE_API_KEY = os.getenv("DUKE_API_KEY")
base_url = "https://streamer.oit.duke.edu"

def load_subjects():
    """Load and parse the Duke subjects JSON file"""
    try:
        with open('data/curriculumData/duke_subjects.json', 'r') as f:
            subjects_data = json.load(f)
            return subjects_data
        
    except Exception as e:
        print(f"Error loading subjects: {e}")
        return {}

            
def get_courses():
    """A tool to get all courses for a given subject"""

    subjects = load_subjects()
    subjects_to_remove = []
    for code, name in subjects.items():
        subject = f"{code} - {name}"
        print(subject)
        encoded_subject = quote(subject)
        url = f"{base_url}/curriculum/courses/subject/{encoded_subject}?access_token={DUKE_API_KEY}"
        response = requests.get(url)
        summaries = []

        try:
            courses_raw = response.json()['ssr_get_courses_resp']['course_search_result']['subjects']['subject']['course_summaries']['course_summary']
            summaries.append({
                "subject": subject,
                "courses": [
                    {
                    "catalog_nbr": c.get("catalog_nbr", "").strip(),
                    "title": c.get("course_title_long", "N/A"),
                    "term": c.get("ssr_crse_typoff_cd_lov_descr", "N/A"),
                    "crse_id": c.get("crse_id"),
                    "crse_offer_nbr": c.get("crse_offer_nbr"),
                    } for c in courses_raw
                ]
            })
            

        except Exception as e:
            print(f"Error getting courses: {e}")
            subjects_to_remove.append(code)

    # remove the subjects from the json file
    for code in subjects_to_remove:
        subjects.pop(code)

    # save the subjects to the json file
    with open(f"data/curriculumData/duke_subjects.json", "w") as f:
        json.dump(subjects, f, indent=4)

    # save the summaries to the json file
    with open(f"data/curriculumData/duke_subject_courses.json", "a") as f:
        json.dump(summaries, f, indent=4)


if __name__ == "__main__":
    get_courses()


