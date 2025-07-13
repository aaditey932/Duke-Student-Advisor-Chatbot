import streamlit as st
from langchain.agents import create_openai_tools_agent, AgentExecutor
from langchain_openai import ChatOpenAI
from tools.finalTools import tools as available_tools
from langchain import hub
from langchain_core.messages import HumanMessage, AIMessage
from datetime import datetime
import json

# Page config
st.set_page_config(
    page_title="Duke University Assistant",
    page_icon="🏫",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize the chatbot in session state
@st.cache_resource
def initialize_agent():
    """Initialize the agent (cached to avoid recreating)."""
    prompt = hub.pull("hwchase17/openai-functions-agent")
    llm = ChatOpenAI(model='gpt-4o-mini', temperature=0.1)
    
    agent = create_openai_tools_agent(
        prompt=prompt, 
        llm=llm, 
        tools=available_tools
    )
    
    agent_executor = AgentExecutor(
        agent=agent, 
        tools=available_tools, 
        verbose=True, 
        handle_parsing_errors=True, 
        max_iterations=10,
        return_intermediate_steps=True
    )
    
    return agent_executor

def main():
    st.title("🏫 Duke University Assistant")
    st.markdown("Ask me about Duke's programs, courses, professors, events, and more!")
    
    # Initialize session state
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "agent_executor" not in st.session_state:
        st.session_state.agent_executor = initialize_agent()
    
    # Sidebar
    with st.sidebar:
        st.header("💬 Chat Controls")
        
        if st.button("🗑️ Clear Chat History"):
            st.session_state.chat_history = []
            st.session_state.messages = []
            st.success("Chat history cleared!")
        
        st.header("📊 Session Info")
        st.write(f"Messages: {len(st.session_state.messages)}")
        st.write(f"History length: {len(st.session_state.chat_history)}")
        
        if st.button("💾 Download Chat"):
            chat_data = {
                'timestamp': datetime.now().isoformat(),
                'messages': st.session_state.messages
            }
            st.download_button(
                label="Download JSON",
                data=json.dumps(chat_data, indent=2),
                file_name=f"duke_chat_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )
        
        st.header("🛠️ Available Tools")
        st.write("- Current Date & Time")
        st.write("- MEM Program Info")
        st.write("- Pratt School Info") 
        st.write("- Course Listings")
        st.write("- Course Details")
        st.write("- Campus Events")
        st.write("- AIPI Program Info")
    
    # Main chat interface
    chat_container = st.container()
    
    # Display chat messages
    with chat_container:
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.write(message["content"])
                
                # Show tools used if available
                if "tools_used" in message and message["tools_used"]:
                    with st.expander("🔧 Tools used"):
                        st.write(", ".join(message["tools_used"]))
    
    # Chat input
    if prompt := st.chat_input("Ask me about Duke University..."):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display user message
        with st.chat_message("user"):
            st.write(prompt)
        
        # Generate response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    # Invoke the agent
                    result = st.session_state.agent_executor.invoke({
                        "input": prompt,
                        "chat_history": st.session_state.chat_history
                    })
                    
                    response = result.get('output', 'I apologize, but I encountered an issue.')
                    intermediate_steps = result.get('intermediate_steps', [])
                    tools_used = [step[0].tool for step in intermediate_steps if hasattr(step[0], 'tool')]
                    
                    # Display response
                    st.write(response)
                    
                    # Show tools used
                    if tools_used:
                        with st.expander("🔧 Tools used in this response"):
                            st.write(", ".join(tools_used))
                    
                    # Update session state
                    st.session_state.messages.append({
                        "role": "assistant", 
                        "content": response,
                        "tools_used": tools_used
                    })
                    
                    # Update chat history for agent context
                    st.session_state.chat_history.extend([
                        HumanMessage(content=prompt),
                        AIMessage(content=response)
                    ])
                    
                    # Limit chat history
                    if len(st.session_state.chat_history) > 20:
                        st.session_state.chat_history = st.session_state.chat_history[-20:]
                
                except Exception as e:
                    error_msg = f"I encountered an error: {str(e)}. Please try rephrasing your question."
                    st.error(error_msg)
                    st.session_state.messages.append({"role": "assistant", "content": error_msg})

if __name__ == "__main__":
    main()

# To run: streamlit run duke_chatbot_web.py