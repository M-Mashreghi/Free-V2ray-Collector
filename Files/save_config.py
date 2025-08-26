import os
import logging
logger = logging.getLogger("save_config")
  
def save_data(merged_configs):
    # output_folder = os.path.abspath(os.path.join(os.getcwd(), '..'))
    output_folder = os.getcwd()
    logger.info("Saving %d configs to %s", len(merged_configs), output_folder)

    # Delete existing output files
    filename = os.path.join(output_folder, f'All_Configs_Sub.txt')
    if os.path.exists(filename):
        os.remove(filename)
    for i in range(30):
        filename = os.path.join(output_folder, f'Sub{i}.conf')
        if os.path.exists(filename):
            os.remove(filename)
    


    # Write merged configs to output file
    output_file = os.path.join(output_folder, 'All_Configs_Sub.txt')
    with open(output_file, 'w', encoding='utf-8') as f:
        for config in merged_configs:
            try:
                f.write(config + '\n')
            except UnicodeEncodeError:
                # Handle characters that cannot be encoded
                f.write("<<Unencodable Character>>\n")
    logger.info("Saved All_Configs_Sub.txt successfully")





def save_data_shuffle(shuffled_config , shuffled_list):
    # output_folder = os.path.abspath(os.path.join(os.getcwd(), '..'))
    output_folder = os.getcwd()
    logger.info("Saving %d configs to %s", len(shuffled_config), output_folder)

    output_folder_shuffled = "shuffle"  # Output folder where files will be created

    # Delete existing output files
    filename = os.path.join(output_folder, f'All_shuffled_config.txt')
    if os.path.exists(filename):
        os.remove(filename)
    for i in range(50):
        filename = os.path.join(output_folder_shuffled, f'Sub{i}_shuffled.conf')
        if os.path.exists(filename):
            os.remove(filename)


    # Write merged configs to output file
    output_file = os.path.join(output_folder, 'All_shuffled_config.txt')
    with open(output_file, 'w', encoding='utf-8') as f:
        for config in shuffled_config:
            try:
                f.write(config)
            except UnicodeEncodeError:
                # Handle characters that cannot be encoded
                f.write("<<Unencodable Character>>\n")
            # f.write("\n")


    num_lines = len(shuffled_list)
    max_lines_per_file = 900
    num_files = (num_lines + max_lines_per_file - 1) // max_lines_per_file

    # Create the 'shuffle' folder if it doesn't exist
    os.makedirs(output_folder_shuffled, exist_ok=True)

    for i in range(num_files):
        start_index = i * max_lines_per_file
        end_index = (i + 1) * max_lines_per_file
        filename = os.path.join(output_folder_shuffled, f'Sub{i + 1}_shuffled.conf')
        with open(filename, 'w', encoding='utf-8') as f:
            for line in shuffled_list[start_index:end_index]:
                f.write(line + "\n")
    logger.info("Saved All_Configs_shuffled.txt successfully")
