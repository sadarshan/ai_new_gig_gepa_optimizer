import os
from dataclasses import dataclass
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


@dataclass
class OptimizationConfig:
    # Data configuration
    data_dir: str = "data"
    train_split: str = "train"
    eval_split: str = "eval"
    
    # Portkey configuration
    portkey_api_key: Optional[str] = None
    portkey_virtual_key: Optional[str] = None
    portkey_config_id: Optional[str] = None
    portkey_provider: str = "openai"
    portkey_model: str = "gpt-4"
    
    # GEPA optimization parameters
    num_iterations: int = 10
    batch_size: int = 8
    components_to_update: list = None
    
    # Output configuration
    output_dir: str = "optimization_results"
    save_intermediate: bool = True
    
    def __post_init__(self):
        if self.components_to_update is None:
            self.components_to_update = ["system_prompt"]
        
        if self.portkey_api_key is None:
            self.portkey_api_key = os.getenv("PORTKEY_API_KEY")
        
        if self.portkey_virtual_key is None:
            self.portkey_virtual_key = os.getenv("PORTKEY_VIRTUAL_KEY")
            
        if self.portkey_config_id is None:
            self.portkey_config_id = os.getenv("PORTKEY_CONFIG_ID")


# Default initial prompt
DEFAULT_INITIAL_PROMPT = """You are a sourcing concierge AI assistant helping buyers find products and services. Your role is to:

1. Understand what the buyer needs
2. Collect necessary details about their requirements  
3. Submit requests to suppliers when you have enough information
4. Provide helpful responses and ask clarifying questions when needed
5. Cancel requests if the buyer changes their mind

Available tools:
- submit_request(): Use when you have enough details to create a sourcing request
- cancel_request(): Use when the buyer wants to cancel an existing request
- reply_to_buyer(): Use to ask questions, provide information, or give updates

Always be helpful, professional, and thorough in gathering requirements before submitting requests."""