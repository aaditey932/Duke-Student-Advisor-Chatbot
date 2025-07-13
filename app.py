import streamlit as st
from utils.function_calling import get_response
import os
from dotenv import load_dotenv
from utils.openai_client import get_openai_client

load_dotenv()
try:
    openai_api_key = os.getenv("OPENAI_API_KEY")
except:
    openai_api_key = None

# Duke University color palette
DUKE_BLUE = "#00539B"  # Primary Duke Blue
DUKE_NAVY = "#012169"  # Duke Navy Blue
DUKE_WHITE = "#FFFFFF"
DUKE_GRAY = "#666666"

# Configure the page
st.set_page_config(
    page_title="Blue Devils in the Details",
    page_icon="🔵",
    layout="wide",
)

# Apply Duke styling with CSS
st.markdown(
    f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=EB+Garamond:wght@400;500;600;700&display=swap');

    body, h1 {{
        font-family: 'EB Garamond', serif !important;
    }}

    .main-title {{
        font-size: 4rem;
        font-weight: 100;
        margin: 0;
        text-align: center;
        letter-spacing: 0.02em;
    }}

    .stTextInput > label, .stTextArea > label {{
        color: {DUKE_WHITE};
        font-weight: bold;
    }}
    .stButton > button {{
        background-color: {DUKE_BLUE};
        color: {DUKE_WHITE};
        border-radius: 4px;
        border: none;
        padding: 0.5rem 1rem;
    }}

    .stSidebar {{
        background-color: {DUKE_NAVY};
        color: {DUKE_WHITE};
    }}
   
    .css-1d391kg {{
        background-color: {DUKE_NAVY};
    }}
    .sidebar .sidebar-content {{
        background-color: {DUKE_NAVY};
    }}
    .title-container {{
        display: flex;
        align-items: center;
        justify-content: center;
        margin-bottom: 2rem;
        padding: 1rem;
        border-radius: 4px;
        color: {DUKE_NAVY};
    }}

    .input-container {{
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        padding: 1rem 2rem;
        background-color: #ffffff;
        z-index: 100;
    }}

    .stChatInputContainer {{
        margin-bottom: 80px;
    }}
    </style>
    """,
    unsafe_allow_html=True,
)


# Title and header
st.markdown("""
    <div class="title-container" style="margin-top: -50px ;">
        <h1 class="main-title">Blue Devils in the Details</h1>
    </div>
    """, 
    unsafe_allow_html=True
)

# Sidebar - Duke University logo and instructions
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/e/e1/Duke_Athletics_logo.svg/1200px-Duke_Athletics_logo.svg.png", width=120)
    
    st.markdown("### How to Use")
    st.markdown("""Ask me anything about Duke University. I can help you with:

- MEM (Master of Engineering Management) program information
- Pratt School of Engineering programs
- Course information and details
                """)
    
    st_openai_api_key = st.text_input("OpenAI API Key", type="password", help="Enter your OpenAI API key")

    # Clear chat button
    if st.button("Clear Chat"):
        st.session_state.messages = []
        st.success("Chat history cleared!")

system_prompt = """You are a helpful assistant for Duke University. You answer questions about Duke's programs, courses, professors, events, and related information using a set of tools. Be thorough, polite, and accurate. If something is unclear, ask follow-up questions to get more context.

Guidelines:
1. **If a user query is vague or underspecified**, do not assume. Instead, ask follow-up questions. For example, if someone asks "Who is Dr. Smith?" ask what program or department they're in before calling a professor-related tool.
2. **Use tools only when needed**. Think through the query: Is it about a program, course, professor, or event? Then pick the tool that best fits that need. If a name match seems fuzzy or incorrect, avoid responding with false confidence.
3. **Avoid inaccurate tool calls**: For example, if a professor's name does not have an exact match, don't return information about someone with a similar name. Instead, say "I couldn't find a match — could you clarify which program they're associated with?"
4. **For professor-related questions**, try to get their department or program (e.g., AIPI or MEM since you have tools for both) before selecting a tool. Some professors are only listed in specific databases. 
5. **Use the web search tool** as a fallback for Duke-related queries that don't fit neatly into any other tool (e.g., "What is Dr. X researching currently?" or "What does Duke's housing policy look like?") OR if the data you get back from the other tools is not helpful, instead of saying "I dont know" try to use the web search tool to answer the question. Incase web search doesn't work either, you can use your own knowledge to answer the question.
6. You are **not** allowed to answer questions that are not related to Duke University. This is very important. If a user query is **not related to Duke University**, respond by saying it's out of scope and that you're here to help with Duke-related questions.
7. Always follow safe and ethical practices when answering questions.
8. Provide links, references, and citations when relevant.
9. !!!!!!! When asked about the Artificial Intelligence for Product Innovation or AIPI course make sure to use the get_courses tool in your planning !!!!!!!!!
10. Use "pratt_search" tool to get general information about Pratt School of Engineering and their programs please!.

Be concise when appropriate, but offer long, elaborate answers when more detail would be helpful.
"""

# Initialize session state variables
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": system_prompt}]


if openai_api_key or st_openai_api_key:
    st.session_state.api_key = openai_api_key or st_openai_api_key
    st.session_state.client = get_openai_client(st.session_state.api_key)
else:
    st.session_state.api_key = None
    st.session_state.client = None


# Display chat messages from session state
for message in st.session_state.messages:
    if message["role"] == "user" or message["role"] == "assistant":
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

if st.session_state.client:
    # User input
    if user_input := st.chat_input("Enter your message here..."):
        
        st.session_state.messages.append({"role": "user", "content": user_input})

        with st.chat_message("user"):
            st.markdown(f"**User**: {user_input}")

        # Agent response handling
        with st.chat_message("assistant"):
            status_container = st.empty()
            response_container = st.empty()
            
            status_container.info("Initializing...")
            
            response = None
            for status in get_response(st.session_state.messages):
                if isinstance(status, str):
                    status_container.info(status)
                else:
                    response = status
                    break
            
            if response and response.content:
                status_container.empty()
                with response_container.container():
                    st.markdown(response.content)
                st.session_state.messages.append({"role": "assistant", "content": response.content})

else:
    st.warning("Please enter your OpenAI API key here or add it to the .env file to continue.")