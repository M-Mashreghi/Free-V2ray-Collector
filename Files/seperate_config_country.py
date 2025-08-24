import os


# def seperate_by_country():
#     output_folder = os.path.abspath(os.path.join(os.getcwd(), '..'))
#     # Delete existing output files
#     input_file_path = os.path.join(output_folder, f'All_shuffled_config.txt')
    
    
#     # Read lines and save non-null lines to a list
#     with open(input_file_path, 'r', encoding='utf-8', errors='ignore') as file:
#         lines = [line.strip() for line in file if line.strip()]
    
#     # Group lines based on the last two uppercase letters
#     grouped_lines = {}
#     for line in lines:
#         last_two_letters = line[-2:]
#         if last_two_letters.isalpha() and last_two_letters.isupper():
#             if last_two_letters not in grouped_lines:
#                 grouped_lines[last_two_letters] = []
#             grouped_lines[last_two_letters].append(line)
    
#     # Create a folder if it doesn't exist
#     output_folder = 'Config_by_country'
#     os.makedirs(output_folder, exist_ok=True)
    
#     # Save each group in a separate text file
#     for two_letters, group in grouped_lines.items():
#         output_file_path = os.path.join(output_folder, f'server_{two_letters}.txt')
#         with open(output_file_path, 'w', encoding='utf-8') as output_file:
#             output_file.write('\n'.join(group))
    
#     print(f"Groups saved in '{output_folder}' folder.")
    


def seperate_by_country():
    # Read from CURRENT folder (where save_config.save_data_shuffle writes)
    input_file_path = os.path.join(os.getcwd(), "All_shuffled_config.txt")

    # Read lines and save non-null lines to a list
    with open(input_file_path, 'r', encoding='utf-8', errors='ignore') as file:
        lines = [line.strip() for line in file if line.strip()]

    # Group lines based on the last two uppercase letters
    grouped_lines = {}
    for line in lines:
        last_two_letters = line[-2:]
        if last_two_letters.isalpha() and last_two_letters.isupper():
            grouped_lines.setdefault(last_two_letters, []).append(line)

    # Create output folder
    output_folder = 'Config_by_country'
    os.makedirs(output_folder, exist_ok=True)

    # Save each group in a separate text file
    for two_letters, group in grouped_lines.items():
        output_file_path = os.path.join(output_folder, f'server_{two_letters}.txt')
        with open(output_file_path, 'w', encoding='utf-8') as output_file:
            output_file.write('\n'.join(group))

    print(f"Groups saved in '{output_folder}' folder.")