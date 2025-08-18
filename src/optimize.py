import os
from typing import Dict, Any

import gepa
from .dataset import SourcingDatasetLoader
from .adapter import SourcingConciergeGEPAAdapter


def optimize_sourcing_prompt(
    data_dir: str,
    model_client: Any,
    initial_prompt: str,
    num_iterations: int = 10,
    batch_size: int = 16,
    output_dir: str = "results"
):
    """
    Optimize the sourcing concierge prompt using GEPA.
    
    Args:
        data_dir: Path to directory containing train/ and eval/ subdirectories with .jsonl files
        model_client: OpenAI or compatible client for making API calls
        initial_prompt: Starting system prompt to optimize
        num_iterations: Number of GEPA optimization iterations
        batch_size: Size of mini-batches for evaluation
        output_dir: Directory to save optimization results
    """
    
    # Load datasets
    data_loader = SourcingDatasetLoader(data_dir)
    train_data = data_loader.load_dataset("train")
    eval_data = data_loader.load_dataset("eval")
    
    print(f"Loaded {len(train_data)} training examples and {len(eval_data)} evaluation examples")
    
    # Create GEPA adapter
    adapter = SourcingConciergeGEPAAdapter(model_client, data_loader)
    
    # Initial candidate with the seed prompt
    initial_candidate = {
        "system_prompt": initial_prompt
    }
    
    # Run GEPA optimization
    result = gepa.optimize(
        adapter=adapter,
        train_data=train_data,
        val_data=eval_data,
        initial_candidate=initial_candidate,
        components_to_update=["system_prompt"],
        num_iterations=num_iterations,
        batch_size=batch_size,
        output_dir=output_dir
    )
    
    return result


def main():
    """
    Example usage of the optimization script.
    """
    # You'll need to provide your model client
    # For example, using OpenAI:
    # from openai import OpenAI
    # model_client = OpenAI(api_key="your-api-key")
    
    initial_prompt = """You are a sourcing concierge AI assistant helping buyers find products and services. Your role is to:

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

    data_dir = "data"
    output_dir = "optimization_results"
    
    # Uncomment and configure when you have your model client ready
    # result = optimize_sourcing_prompt(
    #     data_dir=data_dir,
    #     model_client=model_client,
    #     initial_prompt=initial_prompt,
    #     num_iterations=10,
    #     batch_size=8,
    #     output_dir=output_dir
    # )
    
    print("Optimization setup complete. Configure your model client and uncomment the optimization call.")


if __name__ == "__main__":
    main()