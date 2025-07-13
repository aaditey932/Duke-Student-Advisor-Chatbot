import json
from utils.openai_client import get_chat_completion
from tools.memDatabaseTool import search as mem_search
from tools.prattDatabaseTool import search as pratt_search
from tools.curriculumTool import get_courses, get_course_details
from tools.eventsTool import get_events
from tools.professorsTool import rate_my_professor_info
from tools.aipiDatabaseTool import get_AIPI_details
from tools.webSearchTool import web_search
from tools.tools_schema import TOOLS_SCHEMA

def get_tool_function(tool_name: str):
    """Get the actual function implementation for a tool name"""
    tool_functions = {
        "mem_search": mem_search,
        "pratt_search": pratt_search,
        "get_courses": get_courses,
        "get_course_details": get_course_details,
        "get_events": get_events,
        "rate_my_professor_info": rate_my_professor_info,
        "get_AIPI_details": get_AIPI_details,
        "web_search": web_search
    }
    return tool_functions.get(tool_name)

tool_status_messages = {
    "mem_search": "Searching MEM database...",
    "pratt_search": "Searching Pratt database...",
    "get_courses": "Getting courses...",
    "get_course_details": "Getting course details...",
    "get_events": "Getting events...",
    "rate_my_professor_info": "Getting professor info from RateMyProfessors...",
    "get_AIPI_details": "Searching AIPI database...",
    "web_search": "Searching the web..."
}

def get_response(messages, first_call=True):
    
    if first_call:
        yield "Analyzing question..."
    else:
        yield "Analyzing whether another tool call is needed..."
    response_message = get_chat_completion(messages, tools=TOOLS_SCHEMA)

    if response_message.content:
        yield response_message.content
    
    # Check if the model wants to call a function
    if response_message.tool_calls:
        # Get the function call
        tool_call = response_message.tool_calls[0]
        function_name = tool_call.function.name
        function_args = json.loads(tool_call.function.arguments)
        
        yield f"{tool_status_messages[function_name]}..."
        
        # Get the function implementation
        function_to_call = get_tool_function(function_name)
        
        # Add the API key to the function call
        function_response = function_to_call(**function_args)

        # Add the function response to the messages
        messages.append({
            "role": "assistant",
            "content": None,
            "tool_calls": [{
                "id": tool_call.id,
                "type": "function",
                "function": {
                    "name": function_name,
                    "arguments": tool_call.function.arguments
                }
            }]
        })
        
        messages.append({
            "role": "tool",
            "tool_call_id": tool_call.id,
            "content": str(function_response)
        })
        
        yield "Tool Call Completed. Processing the results..."
        
        for status in get_response(messages, first_call=False):
            yield status

        return
    
    yield "Generating final response..."
    yield response_message