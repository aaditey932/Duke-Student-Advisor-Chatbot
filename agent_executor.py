import json 
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, ToolMessage
from langchain_core.runnables import RunnableSerializable
from typing import Dict, Any, List

class CustomAgentExecutor:
    def __init__(self, prompt, llm, tools, max_iterations: int = 5):
        self.chat_history: List[BaseMessage] = []
        self.max_iterations = max_iterations
        self.name2tool = {tool.name: tool.func for tool in tools}
        self.tools = tools

        # Create agent with tools but don't force tool use
        self.agent: RunnableSerializable = (
            {
                "input": lambda x: x["input"],
                "chat_history": lambda x: x["chat_history"],
                "agent_scratchpad": lambda x: x.get("agent_scratchpad", [])
            }
            | prompt
            | llm.bind_tools(tools)  # Remove tool_choice="any" to allow flexibility
        )

    def invoke(self, input_text: str) -> Dict[str, Any]:
        """
        Invoke the agent and return the final answer.
        
        Args:
            input_text (str): User input
            
        Returns:
            Dict[str, Any]: Dictionary containing the answer
        """
        count = 0
        agent_scratchpad = []
        final_answer = None
        
        try:
            while count < self.max_iterations:
                print(f"\n--- Iteration {count + 1} ---")
                
                # Invoke the agent
                response = self.agent.invoke({
                    "input": input_text,
                    "chat_history": self.chat_history,
                    "agent_scratchpad": agent_scratchpad
                })
                
                # Add the response to scratchpad
                agent_scratchpad.append(response)
                
                # Check if the response has tool calls
                has_tool_calls = (
                    hasattr(response, 'tool_calls') and 
                    response.tool_calls and 
                    len(response.tool_calls) > 0
                )
                
                if not has_tool_calls:
                    # No tool calls - direct response from the model
                    final_answer = response.content if hasattr(response, 'content') else str(response)
                    print(f"Direct response: {final_answer}")
                    break
                
                # Process tool calls
                for i, tool_call in enumerate(response.tool_calls):
                    try:
                        tool_name = tool_call.get("name", "unknown")
                        tool_args = tool_call.get("args", {})
                        tool_call_id = tool_call.get("id", f"call_{count}_{i}")
                        
                        print(f"Executing: {tool_name}({tool_args})")
                        
                        # Check if tool exists
                        if tool_name not in self.name2tool:
                            error_msg = f"Tool '{tool_name}' not found in available tools: {list(self.name2tool.keys())}"
                            print(f"❌ {error_msg}")
                            
                            tool_message = ToolMessage(
                                content=error_msg,
                                tool_call_id=tool_call_id
                            )
                            agent_scratchpad.append(tool_message)
                            continue
                        
                        # Execute the tool
                        tool_output = self.name2tool[tool_name](**tool_args)
                        print(f"✅ Tool output type: {type(tool_output)}")
                        
                        # Create tool message
                        tool_message = ToolMessage(
                            content=str(tool_output),
                            tool_call_id=tool_call_id
                        )
                        agent_scratchpad.append(tool_message)
                        
                        # Check if this is the final answer
                        if tool_name == "final_answer":
                            if isinstance(tool_output, dict) and "answer" in tool_output:
                                final_answer = tool_output["answer"]
                            else:
                                final_answer = str(tool_output)
                            print(f"🎯 Final answer found: {final_answer}")
                            count = self.max_iterations  # Exit outer loop
                            break
                            
                    except Exception as e:
                        error_msg = f"Error executing {tool_name}: {str(e)}"
                        print(f"❌ {error_msg}")
                        
                        tool_message = ToolMessage(
                            content=error_msg,
                            tool_call_id=tool_call.get("id", f"error_{count}_{i}")
                        )
                        agent_scratchpad.append(tool_message)
                
                count += 1
            
            # Ensure we have a final answer
            if final_answer is None:
                if count >= self.max_iterations:
                    final_answer = "I apologize, but I couldn't complete your request within the allowed number of steps. Please try rephrasing your question or asking something more specific."
                else:
                    final_answer = "I encountered an issue while processing your request. Please try again."
            
        except Exception as e:
            final_answer = f"I encountered an unexpected error: {str(e)}. Please try again."
            print(f"❌ Unexpected error: {str(e)}")
        
        # Update chat history
        try:
            self.chat_history.extend([
                HumanMessage(content=input_text),
                AIMessage(content=final_answer)
            ])
        except Exception as e:
            print(f"⚠️ Could not update chat history: {str(e)}")
        
        print(f"\n🎯 Final Answer: {final_answer}")
        return {"answer": final_answer}

    def clear_history(self):
        """Clear the chat history."""
        self.chat_history = []
        print("Chat history cleared.")