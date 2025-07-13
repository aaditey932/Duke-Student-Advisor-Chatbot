import requests
from dotenv import load_dotenv
import os
from urllib.parse import quote
import json
from difflib import SequenceMatcher

load_dotenv()

DUKE_API_KEY = os.getenv("DUKE_API_KEY")
BASE_URL = "https://streamer.oit.duke.edu"

def load_subjects():
    """Load and parse the Duke subjects JSON file"""
    try:
        with open('data/curriculumData/duke_subjects.json', 'r') as f:
            subjects_data = json.load(f)
            return subjects_data

    except Exception as e:
        print(f"Error loading subjects: {e}")
        return {}

def find_best_match(query, subjects):
    """
    Find the best matching subject code and name for a given query.
    Returns a tuple of (code, name) or None if no good match is found.
    """
    query = query.lower().strip()
    best_score = 0
    best_match = None
    
    if isinstance(subjects, dict):
        for code, name in subjects.items():
            # Create the full subject string in the format "CODE - NAME"
            full_subject = code + " - " + name
                
            # Calculate similarity scores for different parts
            code_score = SequenceMatcher(None, query, code.lower()).ratio()
            name_score = SequenceMatcher(None, query, name.lower()).ratio()
            full_score = SequenceMatcher(None, query, full_subject.lower()).ratio()
            
            # Use the best score among the three
            score = max(code_score, name_score, full_score)
            
            if score > best_score:
                best_score = score
                best_match = (code, name)

    elif isinstance(subjects, list):
        for subject in subjects:
            # Create the full subject string in the format "CODE - NAME"
            full_subject = subject
                
            # Calculate similarity scores for different parts
            score = SequenceMatcher(None, query, full_subject.lower()).ratio()
   
            if score > best_score:
                best_score = score
                best_match = subject

    else:
        return {"error": "Invalid subjects data structure."}
    
    # Only return a match if the similarity score is above a threshold
    if best_score > 0.5:  # Adjust this threshold as needed
        return best_match
    return None

def get_courses(subject):
    """A tool to get all courses for a given subject"""
    
    # Load subjects and find the best match
    subjects = load_subjects()
    match = find_best_match(subject, subjects)
    
    if not match:
        return {"error": f"No matching subject found for '{subject}'. Please provide a more specific subject name or code."}
    
    code, name = match
    formatted_subject = f"{code} - {name}"
    
    encoded_subject = quote(formatted_subject)
    url = f"{BASE_URL}/curriculum/courses/subject/{encoded_subject}?access_token={DUKE_API_KEY}"
    response = requests.get(url)

    if response.status_code != 200:
        return {"error": response.status_code, "message": response.text}

    try:
        courses_raw = response.json()['ssr_get_courses_resp']['course_search_result']['subjects']['subject']['course_summaries']['course_summary']
        summaries = [
            {
                "catalog_nbr": c.get("catalog_nbr", "").strip(),
                "title": c.get("course_title_long", "N/A"),
                "term": c.get("ssr_crse_typoff_cd_lov_descr", "N/A"),
                "crse_id": c.get("crse_id"),
                "crse_offer_nbr": c.get("crse_offer_nbr"),
            }
            for c in courses_raw
        ]
        return summaries
    except KeyError:
        return {"error": "No courses found or unexpected response structure."}


def get_course_details_helper(crse_id, crse_offer_nbr):
    """A tool to get detailed course info for a specific course using its ID and offering number"""

    url = f"{BASE_URL}/curriculum/courses/crse_id/{crse_id}/crse_offer_nbr/{crse_offer_nbr}?access_token={DUKE_API_KEY}"
    response = requests.get(url)

    if response.status_code != 200:
        return {"error": response.status_code, "message": response.text}

    try:
        data = response.json()['ssr_get_course_offering_resp']['course_offering_result']['course_offering']
        course_info = {
            "title": data.get("course_title_long", "N/A"),
            "description": data.get("descrlong", "No description available."),
            "units": data.get("units_range", "N/A"),
            "term": data.get("ssr_crse_typoff_cd_lov_descr", "N/A"),
            "grading_basis": data.get("grading_basis_lov_descr", "N/A"),
            "career": data.get("acad_career_lov_descr", "N/A"),
            "school": data.get("acad_group_lov_descr", "N/A"),
            "department": data.get("acad_org_lov_descr", "N/A"),
            "consent": data.get("consent_lov_descr", "N/A"),
            "component": data.get("course_components", {}).get("course_component", {}).get("ssr_component_lov_descr", "N/A"),
            "scheduled": "*** This course has not been scheduled. ***" not in response.text
        }
        return course_info
    except KeyError:
        return {"error": "Unexpected structure in course detail response."}


def get_course_details(subject, course_title=None, course_number=None, api_key = None):
    """
    Search for course details by the subject it belongs to with the course title or course number.
    Course can be AI, AIPI, or "Artificial Intelligence", "Eng Management" etc
    Subject title can be "Sourcing Data", "Supply Chain Management" etc
    Subject number can be 590, 710 etc
    """

    course_list = get_courses(subject)
    if isinstance(course_list, dict) and "error" in course_list:
        return course_list

    if course_title:
        query = course_title
        match = find_best_match(query, [course['title'] for course in course_list])

        for course in course_list:
            if course['title'] == match:
                course_details = course
                break

        course_details = get_course_details_helper(course_details['crse_id'], course_details['crse_offer_nbr'])
     
        return course_details
    
    elif course_number:
        query = course_number
        match = find_best_match(query, [course['catalog_nbr'] for course in course_list])

        # based on the catalog number match, get the course details
        for course in course_list:
            if course['catalog_nbr'] == match:
                course_details = course
                break

        course_details = get_course_details_helper(course_details['crse_id'], course_details['crse_offer_nbr'])

        return course_details

    else:
        return {"error": "No course title or number provided."}


if __name__ == "__main__":
 
    all_courses = get_courses("AI")
    for c in all_courses:
        print(f"{c['catalog_nbr']}: {c['title']} ({c['term']})")

    course_details = get_course_details("AI", course_title="Sourcing Data", course_number="590")
    print(course_details)
