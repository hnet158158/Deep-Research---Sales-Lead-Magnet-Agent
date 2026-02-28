"""
AI Lead Magnet Generator - Main Entry Point
Gradio приложение для генерации лид-магнитов с использованием Tavily Search и LLM.
"""

import logging
import sys

from src.ui import main

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )

    main()
