#!/usr/bin/env python3

import os
import sys
from portkey_ai import Portkey
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from config.config import OptimizationConfig, DEFAULT_INITIAL_PROMPT
from src.optimize import optimize_sourcing_prompt


def main():
    # Load configuration
    config = OptimizationConfig()
    
    # Initialize Portkey client
    if not config.portkey_api_key:
        print("Error: Please set PORTKEY_API_KEY in .env file or environment variable")
        return
    
    
    light_client = Portkey(api_key=config.portkey_api_key, config=config.portkey_config_id_light_model)
    heavy_client = Portkey(api_key=config.portkey_api_key, config=config.portkey_config_id_heavy_model)
    
    print("Starting GEPA optimization for sourcing concierge prompt...")
    print(f"Data directory: {config.data_dir}")
    print(f"Output directory: {config.output_dir}")
    print(f"Iterations: {config.num_iterations}")
    print(f"Batch size: {config.batch_size}")
    # print(f"Provider: {config.portkey_provider}")
    # print(f"Model: {config.portkey_model}")
    print()
    
    # Run optimization
    try:
        result = optimize_sourcing_prompt(
            data_dir=config.data_dir,
            light_client=light_client,
            heavy_client=heavy_client,
            initial_prompt=DEFAULT_INITIAL_PROMPT,
            num_iterations=config.num_iterations,
            batch_size=config.batch_size,
            output_dir=config.output_dir
        )
        
        print("Optimization completed successfully!")
        print(f"Results saved to: {config.output_dir}")
        
        if hasattr(result, 'best_candidate'):
            print("\nBest prompt found:")
            print("=" * 50)
            print(result.best_candidate.get('system_prompt', 'No optimized prompt found'))
            print("=" * 50)
            
    except Exception as e:
        print(f"Error during optimization: {str(e)}")
        raise


if __name__ == "__main__":
    main()