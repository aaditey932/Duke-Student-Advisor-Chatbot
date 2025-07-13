from langchain_openai import OpenAIEmbeddings, ChatOpenAI
import os
from dotenv import load_dotenv
import streamlit as st
from langchain_core.messages import BaseMessage
from typing import List, Optional
import json 
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, ToolMessage
from langchain_core.runnables import RunnableSerializable

load_dotenv()

def get_chat_completion(messages: List[BaseMessage],
                         tools: Optional[list] = None,
                         tool_choice: str = "auto"):
    """
    Invoke the ChatOpenAI model with LangChain message format and optional tools.
    """
    model = ChatOpenAI(model='gpt-4o-mini')

    try:
        # Bind tools if needed
        if tools:
            runnable = model.bind_tools(tools, tool_choice=tool_choice)
        else:
            runnable = model

        # Call invoke() on the message list
        response = runnable.invoke(messages)
        return response

    except Exception as e:
        print(f"❌ LangChain ChatOpenAI call failed: {e}")
        return None
    
def get_embeddings_model():
    """
    Creates and returns an OpenAIEmbeddings object using the provided API key
    """
    api_key = os.getenv("OPENAI_API_KEY")

    return OpenAIEmbeddings(
        model="text-embedding-3-small",
        openai_api_key=api_key
    )

class CustomAgentExecutor:
    chat_history: list[BaseMessage]

    def __init__(self, prompt, llm, tools, max_iterations: int = 3):
        self.chat_history = []
        self.max_iterations = max_iterations
        self.name2tool = {tool.name: tool.func for tool in tools}

        self.agent: RunnableSerializable = (
            {
                "input": lambda x: x["input"],
                "chat_history": lambda x: x["chat_history"],
                "agent_scratchpad": lambda x: x.get("agent_scratchpad", [])
            }
            | prompt
            | llm.bind_tools(tools, tool_choice="any")  # we're forcing tool use again
        )

    def invoke(self, input: str) -> dict:
        # invoke the agent but we do this iteratively in a loop until
        # reaching a final answer
        count = 0
        agent_scratchpad = []
        while count < self.max_iterations:
            # invoke a step for the agent to generate a tool call
            tool_call = self.agent.invoke({
                "input": input,
                "chat_history": self.chat_history,
                "agent_scratchpad": agent_scratchpad
            })
            # add initial tool call to scratchpad
            agent_scratchpad.append(tool_call)
            # otherwise we execute the tool and add it's output to the agent scratchpad
            tool_name = tool_call.tool_calls[0]["name"]
            tool_args = tool_call.tool_calls[0]["args"]
            tool_call_id = tool_call.tool_calls[0]["id"]
            tool_out = self.name2tool[tool_name](**tool_args)
            # add the tool output to the agent scratchpad
            tool_exec = ToolMessage(
                content=f"{tool_out}",
                tool_call_id=tool_call_id
            )
            agent_scratchpad.append(tool_exec)
            # add a print so we can see intermediate steps
            print(f"{count}: {tool_name}({tool_args})")
            count += 1
            # if the tool call is the final answer tool, we stop
            if tool_name == "final_answer":
                break
        # add the final output to the chat history
        final_answer = tool_out["answer"]
        self.chat_history.extend([
            HumanMessage(content=input),
            AIMessage(content=final_answer)
        ])
        # return the final answer in dict form
        return json.dumps(tool_out)