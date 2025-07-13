import pytz
from datetime import datetime
from langchain_core.tools import tool
from tools.memDatabaseTool import mem_search
from tools.prattDatabaseTool import pratt_search
from tools.curriculumTool import get_courses, get_course_details
from tools.eventsTool import get_events
from tools.professorsTool import rate_my_professor_info
from tools.aipiDatabaseTool import get_AIPI_details
from tools.webSearchTool import web_search
from langchain.utilities import GoogleSerperAPIWrapper
from langchain.agents import Tool
from dotenv import load_dotenv
import os

load_dotenv()

GOOGLE_API_KEY=os.getenv("GOOGLE_API_KEY")

@tool
def get_current_date(timezone: str = "US/Eastern") -> str:
    """
   **EVENTS TOOL**: Find current and upcoming Duke campus events.
    
    **PREREQUISITE**: MUST call get_current_date first to understand current date context.
    
    **Use when:** Query mentions:
    - "events", "seminars", "workshops", "conferences"
    - "this week/weekend", "upcoming", "happening now"
    - "what's going on at Duke"
    
    **Required workflow:**
    1. First call get_current_date() to get current date/time
    2. Then call get_events() with enhanced query including date context
    
    **Query should include date context like:**
    - "events this weekend" (when today is Friday June 13, 2025)
    - "events on Friday June 13, 2025" (for today's events)
    - "events from June 13-19, 2025" (for this week)
    
    Returns: Event name, date, time, location, description
    
    Example workflow:
    1. get_current_date() → "Today is Friday, June 13, 2025"
    2. get_events("events this weekend starting June 14-15, 2025")
    """
    try:
        tz = pytz.timezone(timezone)
        now = datetime.now(tz)
        
        # Determine semester
        month = now.month
        if month >= 8 and month <= 12:
            semester = "Fall"
        elif month >= 1 and month <= 5:
            semester = "Spring"
        else:
            semester = "Summer"
        
        academic_year = f"{now.year}-{now.year + 1}" if month >= 8 else f"{now.year - 1}-{now.year}"
        
        return f"""Current Date & Time:
- Today: {now.strftime('%A, %B %d, %Y')}
- Time: {now.strftime('%I:%M %p %Z')}
- Academic Year: {academic_year}
- Current Semester: {semester}"""
        
    except Exception as e:
        return f"Error getting current date: {str(e)}"

@tool
def final_answer(answer: str, tools_used: list[str]) -> str:
    """
    **REQUIRED FINAL STEP**: Provide the complete response to the user.

    This tool MUST be called to deliver the final answer after gathering information.
    Do not respond without using this tool.

    Parameters:
    - answer (str): Complete, well-formatted response to the user's question
    - tools_used (list): Names of all tools used during research

    Example:
    final_answer(
        answer="Dr. Bent is a professor in the AIPI program...", 
        tools_used=["get_AIPI_details", "rate_my_professor_info"]
    )
    """
    return {"answer": answer, "tools_used": tools_used}

google_search = GoogleSerperAPIWrapper(serper_api_key=GOOGLE_API_KEY)

google_search = [
    Tool(
        name="Google Search",
        func=google_search.run,
        description="useful for when you need to ask with search",
        verbose=True
    )
]

tools = [get_current_date,
         rate_my_professor_info,
         mem_search, 
         pratt_search,
         get_courses,
         get_course_details,
         get_events,
         get_AIPI_details,
         web_search]
