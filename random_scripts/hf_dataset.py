import pandas as pd

df = pd.read_json("hf://datasets/cindy990915/duke-chat-rag/updated_qa_pairs_0411 (2).json")
df.to_csv("data/eval_QA_data.csv", index=False)
