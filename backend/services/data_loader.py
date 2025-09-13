import json
import os
from typing import List, Dict, Any

def load_sample_tickets() -> List[Dict[str, Any]]:
    root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, "sample_tickets.json"))
    backend_path = os.path.join(os.path.dirname(__file__), "..", "sample_tickets.json")
    
    for sample_path in [root_path, backend_path]:
        if os.path.exists(sample_path):
            try:
                with open(sample_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, list) and data:
                        return data
            except Exception as e:
                print(f"Failed loading {sample_path}: {str(e)}")
    
    return []

def save_tickets(tickets: List[Dict[str, Any]], filepath: str) -> bool:
    try:
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(tickets, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Failed to save tickets to {filepath}: {str(e)}")
        return False