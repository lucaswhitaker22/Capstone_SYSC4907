#!/bin/bash

output_file="combined_html.txt"

# Remove the output file if it already exists
rm -f "$output_file"

# Find all .html files and process them
find . -type f -name "*.html" | while read -r file; do
    echo "Processing: $file"
    echo "--- File: $file ---" >> "$output_file"
    cat "$file" >> "$output_file"
    echo -e "\n\n" >> "$output_file"
done

echo "All .html files have been concatenated into $output_file"


#!/bin/bash

output_file="combined_py.txt"

# Remove the output file if it already exists
rm -f "$output_file"

# Find all .html files and process them
find . -type f -name "*.py" | while read -r file; do
    echo "Processing: $file"
    echo "--- File: $file ---" >> "$output_file"
    cat "$file" >> "$output_file"
    echo -e "\n\n" >> "$output_file"
done

echo "All .py files have been concatenated into $output_file"