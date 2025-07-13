# Duke Student Advisor Chatbot

An intelligent AI-powered agentic chatbot designed to assist students with comprehensive information about Duke University's programs, courses, professors, and events. The chatbot leverages multiple specialized tools, databases, and APIs to provide accurate, contextual responses to student queries.

## Live Deployment

🚀 **Access the live application**: [Duke Student Advisor Chatbot](http://13.222.34.153:8501)

The application is deployed on AWS EC2 with Streamlit serving the web interface.

## Purpose

The Duke Student Advisor Chatbot serves as a virtual assistant for students, providing instant access to information about:

- **Academic Programs**: MEM, AIPI, and all Pratt School of Engineering programs
- **Course Information**: Detailed course listings, descriptions, prerequisites, and scheduling
- **Professor Information**: Faculty profiles, ratings, and student reviews
- **University Events**: Current and upcoming campus events, seminars, workshops
- **General Information**: Duke policies, facilities, and student resources

## Technical Architecture

### Core Technologies
- **Frontend**: Streamlit web application with interactive chat interface
- **Backend**: Python with LangChain agent framework
- **AI/ML**: OpenAI GPT-4o-mini for conversational AI and embeddings
- **Vector Database**: Pinecone for semantic search and document retrieval
- **APIs**: Duke University APIs, Google Custom Search, RateMyProfessors data
- **Agent Framework**: Custom ReAct agent with tool calling capabilities

### Data Sources
- **Pinecone Vector Stores**: 
  - MEM Program handbook (vectorized PDF)
  - Pratt School handbook (vectorized PDF) 
  - AIPI Program documents (vectorized content)
- **Live APIs**: Duke curriculum API, Duke events API
- **Scraped Data**: Professor ratings, course information
- **Web Search**: Google Custom Search for fallback queries

## Available Tools

The chatbot utilizes 9 specialized tools organized in a hierarchical approach:

### 1. **Date and Time Tool** (`get_current_date`)
- Provides current date, time, academic year, and semester information
- Essential for event queries and academic calendar context

### 2. **MEM Program Search** (`mem_search`)
- **Primary tool** for Master of Engineering Management queries
- Covers program structure, curriculum, specializations, admissions, and faculty
- Uses Pinecone vector search on MEM handbook

### 3. **Pratt School Search** (`pratt_search`)
- **General tool** for Pratt School of Engineering information (excluding MEM/AIPI specifics)
- Includes all engineering programs (MEng, MS, PhD), admissions, policies, facilities
- Uses Pinecone vector search on Pratt bulletin

### 4. **Course Information Tools**
   - **`get_courses`**: Retrieves course listings for specific departments (AIPI, ECE, ME, etc.)
   - **`get_course_details`**: Provides detailed information about specific courses
   - Integrates with Duke's official curriculum API

### 5. **Events System** (`get_events`)
- Uses GPT to extract filters from user queries
- Fetches events from Duke's official events API
- Provides natural language summaries of filtered events

### 6. **Professor Information** (`rate_my_professor_info`)
- Accesses student ratings and reviews from RateMyProfessors
- Includes teaching quality, difficulty ratings, and student feedback
- Uses fuzzy matching to find professors

### 7. **AIPI Program Details** (`get_AIPI_details`)
- **Primary tool** for Artificial Intelligence for Product Innovation program
- Comprehensive coverage of program overview, curriculum, admissions, faculty
- Uses advanced Pinecone retrieval with document reconstruction

### 8. **Web Search** (`web_search`)
- **Fallback tool** for Duke-specific queries not covered by specialized tools
- Custom Google Search implementation with content extraction
- Used for recent developments, student organizations, policies

### 9. **Final Answer** (`final_answer`)
- **Required final step** for all conversations
- Ensures proper response formatting and tool tracking

## System Features

### Agent Architecture
- **Custom Agent Executor**: Implements ReAct pattern with tool calling
- **Conversation Memory**: Maintains chat history for context
- **Error Handling**: Robust error management and parsing
- **Tool Orchestration**: Intelligent tool selection based on query analysis

### Advanced Capabilities
- **Semantic Search**: Vector-based document retrieval using OpenAI embeddings
- **Document Reconstruction**: Reassembles full documents from vector chunks
- **Query Understanding**: GPT-powered query analysis and filter extraction
- **Fuzzy Matching**: Intelligent matching for professor and course names
- **Multi-source Integration**: Combines multiple data sources for comprehensive answers

### User Interface
- **Chat Interface**: Streamlit-based conversational UI
- **Tool Transparency**: Shows which tools were used for each response
- **Session Management**: Chat history preservation and download
- **Sidebar Controls**: Clear chat, session info, and available tools overview

## API Dependencies

The chatbot integrates with several external services:

1. **OpenAI API**: GPT-4o-mini for conversation and text-embedding-3-small for embeddings
2. **Pinecone**: Vector database for semantic search
3. **Duke University APIs**: Official course and events data
4. **Google Custom Search**: Web search capabilities
5. **RateMyProfessors**: Professor rating data (via web scraping)

## Usage Examples

### Academic Program Queries
- "Tell me about the MEM program specializations"
- "What are the AIPI program admission requirements?"
- "What engineering master's programs does Pratt offer?"

### Course Information
- "What AIPI courses are available?"
- "Tell me about ECE 590"
- "Show me the Machine Learning course details"

### Events and Activities
- "What events are happening this weekend at Duke?"
- "Any AI seminars coming up?"
- "What's going on at Duke today?"

### Professor Information
- "What do students think about Professor [Name]?"
- "Tell me about [Professor Name] and their ratings"

## Evaluation Framework

The project includes evaluation capabilities through:

- **Reference-free evaluation**: Uses LLM-based assessment
- **Multi-criteria scoring**: Relevance, clarity, accuracy, completeness
- **Tool usage tracking**: Monitors which tools are used for responses
- **Response quality metrics**: Automated scoring of chatbot performance


## Limitations and Future Enhancements

### Current Limitations
- Limited to Duke University information only
- Depends on external API availability
- Vector database requires periodic updates for new documents

### Planned Enhancements
- Integration with more Duke systems (Canvas, DukeHub)
- Support for more nuanced academic planning queries
- Enhanced multilingual support
- Real-time document updates
