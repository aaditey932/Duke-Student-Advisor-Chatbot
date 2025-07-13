import json
from difflib import SequenceMatcher

def load_professors():
    """Load and parse the professors JSON file"""
    try:
        with open('data/professorsData/duke_professors.json', 'r') as f:
            professors_data = json.load(f)
            return professors_data

    except Exception as e:
        print(f"Error loading professors: {e}")
        return []

def find_best_match(query, professors):
    """
    Find the best matching professor for a given query.
    Returns the professor object or None if no good match is found.
    """
    query = query.lower().strip()
    best_score = 0
    best_match = None
    
    for professor in professors:
        name = professor.get('name', '').lower()
        department = professor.get('department', '').lower()
        
        # Calculate similarity scores for different parts
        name_score = SequenceMatcher(None, query, name).ratio()
        
        # Check if department is part of the query
        dept_score = SequenceMatcher(None, query, department).ratio()
        
        # Also check combined "name - department"
        combined = f"{name} - {department}"
        combined_score = SequenceMatcher(None, query, combined).ratio()
        
        # Use the best score among the three
        score = max(name_score, dept_score, combined_score)
        
        if score > best_score:
            best_score = score
            best_match = professor
    
    # Only return a match if the similarity score is above a threshold
    if best_score > 0.5:  # Adjust this threshold as needed
        return best_match
    return None

def rate_my_professor_info(professor_query):
    """
    Get information about a professor based on name or department.
    Returns professor rating information or an error message.
    
    Example:
    >>> rate_my_professor_info("Eric Fouh")
    {
        "name": "Eric Fouh",
        "department": "Computer Science",
        "rating": "1.3",
        "would_take_again": "9%",
        "num_ratings": "24"
    }
    """
    professors = load_professors()
    
    if not professors:
        return {"error": "Could not load professor data."}
    
    match = find_best_match(professor_query, professors)
    
    if not match:
        return {"error": f"No matching professor found for '{professor_query}'. Please provide a more specific name or department."}
    
    return {
        "name": match.get('name', 'N/A'),
        "department": match.get('department', 'N/A'),
        "rating": match.get('rating', 'N/A'),
        "would_take_again": match.get('would_take_again', 'N/A'),
        "num_ratings": match.get('num_ratings', 'N/A')
    }


if __name__ == "__main__":
    # Example usage
    print("Example professor lookup:")
    prof_info = rate_my_professor_info("Eric Fouh")
    print(prof_info)