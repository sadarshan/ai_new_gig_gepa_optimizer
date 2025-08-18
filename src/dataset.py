import json
import os
from typing import List, Dict, Any
from dataclasses import dataclass

from .tools import get_available_tools


@dataclass
class ChatDataInstance:
    id: str
    history: List[Dict[str, str]]  # List of conversation turns
    expected_tool_call: Dict[str, Any]  # Tool call with name and filled variables


class SourcingDatasetLoader:
    def __init__(self, data_dir: str):
        self.data_dir = data_dir
    
    def load_dataset(self, split: str) -> List[ChatDataInstance]:
        split_dir = os.path.join(self.data_dir, split)
        instances = []
        
        for filename in os.listdir(split_dir):
            if filename.endswith('.jsonl'):
                filepath = os.path.join(split_dir, filename)
                instances.extend(self._load_jsonl(filepath))
        
        return instances
    
    def _load_jsonl(self, filepath: str) -> List[ChatDataInstance]:
        instances = []
        with open(filepath, 'r') as f:
            for line in f:
                line = line.strip()
                if line:
                    data = json.loads(line)
                    instances.append(ChatDataInstance(
                        id=data['id'],
                        history=data['history'],
                        expected_tool_call=data['expected_tool_call']
                    ))
        return instances
    
    def get_tool_definitions(self) -> List[Dict[str, Any]]:
        return get_available_tools()