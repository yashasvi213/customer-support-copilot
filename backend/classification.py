import getpass
import os
from typing import List

if not os.environ.get("OPENAI_API_KEY"):
  os.environ["OPENAI_API_KEY"] = getpass.getpass("Enter API key for OpenAI: ")

from langchain.chat_models import init_chat_model

llm = init_chat_model("gpt-4o-mini", model_provider="openai")

from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

tag_list = [
    "How-to", "Product", "Connector", "Lineage", "API/SDK", "SSO",
    "Glossary", "Best practices", "Sensitive data", "Bug", "Permissions"
]

tagging_prompt = ChatPromptTemplate.from_template(
    """
Extract the desired information from the following passage.

Only extract the properties mentioned in the 'Classification' function.

Passage:
{input}
"""
)


class Classification(BaseModel):
    label: List[str] = Field(
        description=f"The topic tags of the ticket. Only choose from: {tag_list}"
    )
    sentiment: str = Field(description="The sentiment of the ticket, e.g., 'Frustrated'")
    priority: str = Field(description="The priority level, e.g., 'P0'")

# Structured LLM
structured_llm = llm.with_structured_output(Classification)


inp = "Hi team, we're trying to set up our primary Snowflake production database as a new source in Atlan, but the connection keeps failing. We've tried using our standard service account, but it's not working. Our entire BI team is blocked on this integration for a major upcoming project, so it's quite urgent. Could you please provide a definitive list of the exact permissions and credentials needed on the Snowflake side to get this working? Thanks."
prompt = tagging_prompt.invoke({"input": inp})
response = structured_llm.invoke(prompt)

print(response.model_dump())

#Evaluation Code
# Metrics - accuracy, precision, recall, F1-score can be calculated based on labeled data
# import json
# from tqdm import tqdm
# from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
# from sklearn.preprocessing import MultiLabelBinarizer

# LABELED_FILE = os.path.join(os.path.dirname(__file__), "labeled_tickets.json")

# with open(LABELED_FILE, "r") as f:
#     tickets = json.load(f)

# true_labels = {"label": [], "sentiment": [], "priority": []}
# pred_labels = {"label": [], "sentiment": [], "priority": []}

# for ticket in tqdm(tickets, desc="Evaluating tickets"):
#     text = f"{ticket.get('subject', '')}\n{ticket.get('body', '')}"
#     prompt = tagging_prompt.invoke({"input": text})
#     try:
#         response = structured_llm.invoke(prompt)
#         pred = response.model_dump()
#     except Exception as e:
#         print(f"Skipping ticket {ticket.get('id', '')} due to error: {e}")
#         continue

#     # Handle multi-label for 'label'
#     true_val = ticket.get("label", [])
#     pred_val = pred.get("label", [])
#     if isinstance(true_val, str):
#         true_val = [true_val]
#     if isinstance(pred_val, str):
#         pred_val = [pred_val]
#     true_labels["label"].append(true_val)
#     pred_labels["label"].append(pred_val)

#     # Handle single-label for 'sentiment' and 'priority'
#     for field in ["sentiment", "priority"]:
#         true_labels[field].append(ticket.get(field, ""))
#         pred_labels[field].append(pred.get(field, ""))

# def print_metrics(y_true, y_pred, field_name):
#     if field_name == "label":
#         # Multi-label classification metrics
#         mlb = MultiLabelBinarizer()
#         all_labels = set()
#         for labels in y_true + y_pred:
#             if isinstance(labels, list):
#                 all_labels.update(labels)
#             else:
#                 all_labels.add(labels)
        
#         mlb.fit([list(all_labels)])
#         y_true_bin = mlb.transform(y_true)
#         y_pred_bin = mlb.transform(y_pred)
        
#         accuracy = accuracy_score(y_true_bin, y_pred_bin)
#         precision = precision_score(y_true_bin, y_pred_bin, average="weighted", zero_division=0)
#         recall = recall_score(y_true_bin, y_pred_bin, average="weighted", zero_division=0)
#         f1 = f1_score(y_true_bin, y_pred_bin, average="weighted", zero_division=0)
#     else:
#         # Single-label classification metrics
#         accuracy = accuracy_score(y_true, y_pred)
#         precision = precision_score(y_true, y_pred, average="weighted", zero_division=0)
#         recall = recall_score(y_true, y_pred, average="weighted", zero_division=0)
#         f1 = f1_score(y_true, y_pred, average="weighted", zero_division=0)

#     print(f"Metrics for {field_name}:")
#     print(f"  Accuracy:  {accuracy:.4f}")
#     print(f"  Precision: {precision:.4f}")
#     print(f"  Recall:    {recall:.4f}")
#     print(f"  F1-score:  {f1:.4f}")

# for field in ["label", "sentiment", "priority"]:
#     print()
#     print_metrics(true_labels[field], pred_labels[field], field)
