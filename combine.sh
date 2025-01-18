#!/bin/bash

# Create backend.txt - recursively search all subdirectories
find backend/app -type f -name "*.py" ! -path "*/__pycache__/*" -exec echo "=== {} ===" \; -exec cat {} \; -exec echo -e "\n\n" \; > backend.txt

# Create frontend.txt - recursively search all subdirectories
find frontend/app/src -type f -name "*.jsx" -exec echo "=== {} ===" \; -exec cat {} \; -exec echo -e "\n\n" \; > frontend.txt
