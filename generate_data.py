#!/usr/bin/env python3

import sys
import os

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.data_generator import main

if __name__ == "__main__":
    main()