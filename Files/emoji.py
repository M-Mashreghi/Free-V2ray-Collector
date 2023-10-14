import json
def find_emoji(country_name):
    # Define the filename for the text file
    filename = "country_emojis.txt"
    
    # Read the JSON data from the text file
    with open(filename, "r") as file:
        json_data = file.read()
    
    # Deserialize the JSON data into a Python dictionary
    country_emojis = json.loads(json_data)
    
    def get_country_emoji(country_name):
        # Get the emoji for the given country name, or return None if not found
        return country_emojis.get(country_name, None)
    
    
    # Get the emoji for the provided country name
    emoji = get_country_emoji(country_name)
    
    if emoji:
        return emoji
    else:
        country_name

