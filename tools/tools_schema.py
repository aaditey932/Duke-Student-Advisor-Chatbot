TOOLS_SCHEMA = [
    {
        "type": "function",
        "function": {
            "name": "mem_search",
            "description": "Retrieve detailed information about the MEM (Master of Engineering Management) program at Duke University, including structure, specializations, admissions, and faculty.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query about MEM program"
                    },
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "pratt_search",
            "description": "Provides official, detailed information about Duke’s Pratt School of Engineering professional master’s programs—including admissions, degree requirements, academic policies, tuition, student resources, and program options for 2024-2025. Use it to answer questions about Pratt School or Duke engineering graduate education, policies, and student life",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query about Pratt programs"
                    },
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_courses",
            "description": "Get a list of courses for a specific subject or department at Duke University. Useful when a user asks about course offerings in a subject (e.g., 'What courses are offered in ECE?'). !!! When asked about the AIPI curriculum make sure to use this tool in your planning !!!",
            "parameters": {
                "type": "object",
                "properties": {
                    "subject": {
                        "type": "string",
                        "description": "The subject code or name (e.g., 'AIPI', 'CS', 'ECE')"
                    }
                },
                "required": ["subject"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_course_details",
            "description": "Get detailed information for a specific course at Duke University by subject and either course number or course title. Best used when a user mentions a specific course code or name",
            "parameters": {
                "type": "object",
                "properties": {
                    "subject": {
                        "type": "string",
                        "description": "The subject name like 'Artificial Intelligence' or 'AI'"
                    },
                    "course_title": {
                        "type": "string",
                        "description": "The course title to search for like 'Sourcing Data' or 'Supply Chain Management'",
                        "default": None

                    },
                    "course_number": {
                        "type": "string",
                        "description": "The course number to search for like '590' or '710'",
                        "default": None
                    }
                },
                "required": ["subject"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_events",
            "description": "Get upcoming events listed in the Duke University Events system. Best used when a user asks about events, lectures, or seminars happening on campus.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The query to search for events"
                    }
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "rate_my_professor_info",
            "description": "Uses public data from RateMyProfessors to search for basic information and student ratings about a professor based on their name. Use this to get professor rating and reviews details that students have shared.",
            "parameters": {
                "type": "object",
                "properties": {
                    "professor_query": {
                        "type": "string",
                        "description": "The professor name to search for (e.g., 'Eric Fouh', 'Smith Computer Science')"
                    }
                },
                "required": ["professor_query"]
            }
        }
    },

    {
        "type": "function",
        "function": {
            "name": "get_AIPI_details",
            "description": "Get detailed information about the Artificial Intelligence for Product Innovation (AIPI) program at Duke. This includes program details, admissions, and faculty info. If a professor is known to be part of AIPI, use this tool to retrieve relevant information about them.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The query to search for information about the AIPI or the Artificial Intelligence for Product Innovation Program"
                    }
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "web_search",
            "description": "Search the web for Duke-specific queries when other tools do not apply or fail to provide results. Use this for fresh, uncommon, or non-standard Duke-related information (e.g., student organizations, niche policies).",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The query to search the web for"
                    }
                },
                "required": ["query"]
            }
        }
    },

]