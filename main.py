import os
from dotenv import load_dotenv
import google.generativeai as genai
from PIL import Image
import json
import re

# Setup
load_dotenv()
api_key = os.getenv("API_KEY")
genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-1.5-flash')

# Start remembering
chat = model.start_chat(history=[])

# Query for input
user_suggestion = input("What do you like: ")


# List of file paths for upload
file_paths = ["data/jacket.jpg", "data/jersey.jpg", 
              "data/joggingpants.jpg", "data/polo.jpg", 
              "data/shorts.jpg", "data/slacks.jpg"]

file_ids = {}

# Upload files and store their IDs
for file_path in file_paths:
    with open(file_path, "rb") as image_file:
        image_data = image_file.read()
    
    uploaded_file = genai.upload_file(file_path)
    file_name = os.path.basename(file_path)
    file_id = f"image_id/{file_name}"

    # Send message with the uploaded file
    response = chat.send_message({
        "parts": [
            {"text": f"image id = {file_id}:"},
            {"mime_type": "image/jpeg", "data": image_data}
        ]
    })

response = chat.send_message(f"""
                            Based on the images, 
                            {user_suggestion}.
                            I am implying on an outfit.
                            this is the strict format of your output:
                            First, start the conversation with a very brief introduction about the outfit I want 
                            (follow the format intro: introduction_words [there is only one intro]).
                            Second, tell me the outfit number 
                            (follow the format outfit: num).
                            Third, tell me their corresponding image id and specify what is the ware used
                            (follow the format 'ware: name [newline] id: ware_id').
                            Fourth, move on to the second ware if there's any, then specify the ware used, 
                            loop until no ware is left.
                            Fifth, explain the overall reasoning why you chose that ware for the outfit
                            (follow the format reasoning: your_reasoning).
                            Lastly, conclude the conversation with encouragement of my outfit target
                            (follow the format end: ending_words [there is only one end])""")


def parse_ai_response(ai_response):
    parsed_data = {
        "introduction": "",
        "outfits": [],
        "end": ""
    }

    # Define regex patterns for each section
    intro_pattern = r"intro: (.*?)\n"
    outfit_pattern = r"outfit: (\d+)\n((?:ware: (.*?)\nid: (.*?)\n)+)reasoning: (.*?)\n"
    end_pattern = r"end: (.*?)$"

    # Find introduction
    intro_match = re.search(intro_pattern, ai_response, re.DOTALL)
    if intro_match:
        parsed_data["introduction"] = intro_match.group(1).strip()

    # Find outfits
    outfit_matches = re.finditer(outfit_pattern, ai_response, re.DOTALL)
    for match in outfit_matches:
        outfit_number = match.group(1)
        reasoning = match.group(5).strip()

        outfits_data = []
        ware_id_pairs = re.findall(r"ware: (.*?)\nid: (.*?)\n", match.group(2))

        for ware_name, image_id in ware_id_pairs:
            outfit_data = {
                "outfit_number": outfit_number,
                "ware": ware_name.strip(),
                "id": image_id.strip(),
                "reasoning": reasoning
            }
            outfits_data.append(outfit_data)

        parsed_data["outfits"].extend(outfits_data)

    # Find end
    end_match = re.search(end_pattern, ai_response, re.DOTALL)
    if end_match:
        parsed_data["end"] = end_match.group(1).strip()

    return parsed_data

def save_json_to_file(data, filename):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)


parsed_json = parse_ai_response(response.text)

print(json.dumps(parsed_json, indent=4))

save_json_to_file(parsed_json, 'parsed_output.json')

print(response.text)



