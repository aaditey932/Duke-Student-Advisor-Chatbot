import json
import csv
import ollama
import time
import pandas as pd
import os
import sys

# Add the project root directory to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

from utils.function_calling import get_response

def load_qa_pairs(csv_path):
    """Load questions from a excel file."""
    df = pd.read_csv(csv_path, encoding='latin1')
    return df

def evaluate_qa_pair(question, answer, model_name):
    """Evaluate a single question-answer pair using Ollama."""
    prompt = f"""
You are evaluating a question-answer (QA) pair related to Duke University. Your task is to assess the answer based on relevance, clarity, and overall quality.

Question: {question}
Answer: {answer}

Please assess the QA pair with the following:

1. **Relevance**: Is the question clearly about Duke University or something directly connected to it (e.g., its programs, student life, policies, history, etc.)? Respond with 'yes' or 'no'.

2. **Clarity (1-5)**: Rate how clearly the answer communicates its message. Use the following scale:
   - 1 = Very unclear or confusing
   - 2 = Somewhat unclear or difficult to follow
   - 3 = Adequately clear, but could be better structured or phrased
   - 4 = Mostly clear and easy to understand
   - 5 = Very clear and well-expressed

3. **Comments**: Provide a short paragraph commenting on the **accuracy**, **completeness**, and **helpfulness** of the answer.

Please format your output as a JSON object using the structure below:

{{
    "relevant": "yes/no",
    "clarity": "1-5",
    "comments": "Your comments here"
}}
"""

    
    # Implement retry logic for API calls
    max_retries = 3
    retry_delay = 2
    
    for attempt in range(max_retries):
        try:
            response = ollama.chat(
                model=model_name,
                messages=[{"role": "user", "content": prompt}],
                stream=False
            )
            response_text = response["message"]["content"]
            
            # Extract JSON part
            try:
                # Try to find and parse JSON in the response
                response_text = response_text.strip()
                start_idx = response_text.find("{")
                end_idx = response_text.rfind("}") + 1
                
                if start_idx >= 0 and end_idx > start_idx:
                    json_str = response_text[start_idx:end_idx]
                    result = json.loads(json_str)
                    
                    # Validate the expected fields
                    if "relevant" in result and "clarity" in result and "comments" in result:
                        return result
            except json.JSONDecodeError:
                pass
            
            # If we couldn't parse JSON or it didn't have the expected structure, extract information manually
            result = {}
            
            # Extract relevance (yes/no)
            if "relevant" in response_text.lower():
                if "yes" in response_text.lower() and "no" not in response_text.lower():
                    result["relevant"] = "yes"
                elif "no" in response_text.lower():
                    result["relevant"] = "no"
                else:
                    result["relevant"] = "unclear"
            
            # Extract clarity rating (1-5)
            for i in range(1, 6):
                if f"clarity: {i}" in response_text.lower() or f"clarity rating: {i}" in response_text.lower():
                    result["clarity"] = str(i)
                    break
            if "clarity" not in result:
                result["clarity"] = "3"  # Default
            
            # Extract comments (take everything if we can't find specific comments)
            result["comments"] = response_text[:1000]  # Limit comment size
            
            return result
            
        except Exception as e:
            if attempt < max_retries - 1:
                print(f"Attempt {attempt+1} failed. Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
                retry_delay *= 2  # Exponential backoff
            else:
                print(f"Error evaluating Q&A pair: {e}")
                return {
                    "relevant": "unclear",
                    "clarity": "0",
                    "comments": f"Failed to evaluate: {str(e)}"
                }

def main():
    csv_path = "evaluation/eval_Q_data.csv"

    print(f"Loading Questions from {csv_path}...")
    questions = load_qa_pairs(csv_path)['questions']
    print(questions)
    
    model_name = "llama3:8b"
    results = []
    
    total_pairs = len(questions)
    for idx, question in enumerate(questions):
        messages = [{"role": "user", "content": question}]
        answer = "Error"  # Default value
        
        try:
            # Set a timeout for the response
            max_iterations = 5  # Maximum number of iterations to wait for response
            current_iteration = 0
            
            for status in get_response(messages):
                if isinstance(status, str):
                    print(status)
                else:
                    response = status
                    break
                    
                current_iteration += 1
                if current_iteration >= max_iterations:
                    print("Warning: Reached maximum iterations waiting for response")
                    break
            
            if response and hasattr(response, 'content'):
                answer = response.content
            else:
                print("Warning: No valid response received")
                answer = "Error"

            print(f"Evaluating pair {idx+1}/{total_pairs}...")
            evaluation = evaluate_qa_pair(question, answer, model_name)
            
            results.append({
                "Input Question": question,
                "Input Answer": answer,
                "Relevant Question to Duke university (yes/no)": evaluation.get("relevant", "unclear"),
                "Clarity of answer (1-5)": evaluation.get("clarity", "0"),
                "General Comments": evaluation.get("comments", "")
            })

        except Exception as e:
            print(f"Error evaluating pair {idx+1}/{total_pairs}: {e}")
            results.append({
                "Input Question": question,
                "Input Answer": answer,
                "Relevant Question to Duke university (yes/no)": "Error",
                "Clarity of answer (1-5)": "Error",
                "General Comments": f"Error: {str(e)}"
            })

        if idx == 49:
            break

    
    # Write results to CSV
    with open('evaluation_results.csv', 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = [
            "Input Question", 
            "Input Answer", 
            "Relevant Question to Duke university (yes/no)", 
            "Clarity of answer (1-5)", 
            "General Comments"
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for result in results:
            writer.writerow(result)
    
    print(f"Evaluation complete! Results written to evaluation_results.csv")

if __name__ == "__main__":
    main()