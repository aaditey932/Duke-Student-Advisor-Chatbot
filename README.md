# Duke Student Advisor Chatbot

An AI-powered agentic chatbot designed to assist students with information about Duke University's programs, courses, professors, and events. The chatbot leverages multiple specialized tools and databases to provide accurate and comprehensive responses to student queries.

## Purpose

The Duke Student Advisor Chatbot serves as a virtual assistant for students, providing instant access to information about:
- Academic programs (MEM, AIPI, Pratt School of Engineering)
- Course details and curriculum
- Professor information and ratings
- University events
- General Duke University information

## Technical Stack

- **Frontend**: Streamlit
- **Backend**: Python
- **AI/ML**: OpenAI API
- **Evaluation**: Ollama (LLM-based evaluation)
- **Data Storage**: Pinecone + Web Scraping + Local Storage 

## Available Tools

The chatbot utilizes several specialized tools to provide accurate information:

1. **MEM Program Search** (`mem_search`)
   - Provides detailed information about the Master of Engineering Management program
   - Covers program structure, specializations, admissions, and faculty

2. **Pratt School Search** (`pratt_search`)
   - Offers comprehensive information about Pratt School of Engineering programs
   - Includes admissions, degree requirements, academic policies, and student resources

3. **Course Information** (`get_courses`, `get_course_details`)
   - Retrieves course listings and detailed information
   - Supports searching by subject, course number, or title

4. **Events System** (`get_events`)
   - Provides information about upcoming Duke University events
   - Covers lectures, seminars, and campus activities

5. **Professor Information** (`rate_my_professor_info`)
   - Accesses public data from RateMyProfessors
   - Provides student ratings and reviews

6. **AIPI Program Details** (`get_AIPI_details`)
   - Specialized tool for Artificial Intelligence for Product Innovation program
   - Includes program details, admissions, and faculty information

7. **Web Search** (`web_search`)
   - Fallback tool for Duke-specific queries
   - Used when other tools don't provide sufficient information

## Evaluation System

The project includes a robust evaluation framework:
- Uses Ollama for reference-free evaluation
- Assesses responses based on:
  - Relevance to Duke University
  - Clarity of answers
  - Accuracy and completeness
- Generates detailed evaluation reports

## Live Demo
Access the deployed app here:
👉 Duke Student Advisor Chatbot [Live App](http://13.218.146.34:8503)
## Getting Started

1. **Prerequisites**
   - Python 3.x
   - OpenAI API key
   - Required Python packages (see `requirements.txt`)

2. **Installation**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configuration**
   - Create a `.env` file with your OpenAI API key or add it to the streamlit UI

4. **Running the Application**
   ```bash
   streamlit run app.py
   ```
