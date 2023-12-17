import os

output_folder = os.path.abspath(os.path.join(os.getcwd(), '..'))
# Delete existing output files
input_file_path = os.path.join(output_folder, f'All_shuffled_config.txt')

output_file_path = 'us_server.txt'
# Read lines containing 'us' (case-insensitive) from the input file

# Check if the output file exists and delete it if it does
if os.path.exists(output_file_path):
    os.remove(output_file_path)

# Read lines containing 'US' in uppercase from the input file
with open(input_file_path, 'r', encoding='utf-8', errors='ignore') as input_file:
    lines_with_us = [line.strip() for line in input_file if 'US' in line]

# Write the filtered lines to the output file
with open(output_file_path, 'w', encoding='utf-8') as output_file:
    output_file.write('\n'.join(lines_with_us))

print(f"Filtered lines saved to {output_file_path}")