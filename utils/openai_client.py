from dotenv import load_dotenv
from openai import OpenAI
from langchain_openai import OpenAIEmbeddings
import os
import streamlit as st
load_dotenv()

def get_openai_client(api_key):
    return OpenAI(api_key=api_key)

def get_chat_completion(messages, tools=None, tool_choice="auto"):
    client = st.session_state.client

    # Build request kwargs conditionally
    kwargs = {
        "model": "gpt-4o",
        "messages": messages,
        "temperature": 0.1
    }

    if tools:
        kwargs["tools"] = tools
        kwargs["tool_choice"] = tool_choice

    try:
        response = client.chat.completions.create(**kwargs)
        return response.choices[0].message
    except Exception as e:
        print(f"❌ OpenAI API call failed: {e}")
        return None

def get_embeddings_model():
    """
    Creates and returns an OpenAIEmbeddings object using the provided API key
    """
    api_key = st.session_state.api_key

    return OpenAIEmbeddings(
        model="text-embedding-3-small",
        openai_api_key=api_key
    )
