import requests
import json
import shutil
import os
import time

def add_card(deck_name, front, back, card_model_name="Basic"):
    # AnkiConnect API URL
    url = "http://localhost:8765"
    
    # Data for the AnkiConnect request
    data = {
        "action": "addNote",
        "version": 6,
        "params": {
            "note": {
                "deckName": deck_name,
                "modelName": card_model_name,
                "fields": {
                    "Front": front,
                    "Back": back
                },
                "tags": []
            }
        }
    }
    
    # Make the request to AnkiConnect
    response = requests.post(url, data=json.dumps(data))
    
    if response.status_code == 200:
        # Check for errors in adding the card
        res = response.json()
        if not res.get('error'):
            print("Card added successfully.")
        else:
            print("Error adding card:", res['error'])
    else:
        print("Failed to connect to AnkiConnect.")

# Example usage
#deck_name = "MyDeck"
#front_content = "What is the capital of France?"
#back_content = "Paris"
#add_card(deck_name, front_content, back_content)

def add_card_with_images(deck_name, front_image_file, back_image_file, card_model_name="Basic"):
    # Format the front and back contents to include images
    front_content = f'<img src="{front_image_file}">'
    back_content = f'<img src="{back_image_file}">'

    # AnkiConnect API URL
    url = "http://localhost:8765"
    
    # Data for the AnkiConnect request
    data = {
        "action": "addNote",
        "version": 6,
        "params": {
            "note": {
                "deckName": deck_name,
                "modelName": card_model_name,
                "fields": {
                    "Front": front_content,
                    "Back": back_content
                },
                "tags": []
            }
        }
    }
    
    # Make the request to AnkiConnect
    response = requests.post(url, data=json.dumps(data))
    
    if response.status_code == 200:
        # Check for errors in adding the card
        res = response.json()
        if not res.get('error'):
            print("Card added successfully.")
        else:
            print("Error adding card:", res['error'])
    else:
        print("Failed to connect to AnkiConnect.")



def generate_unique_filename(base_path, original_name):
    # Split the original name into name and extension
    name, extension = os.path.splitext(original_name)
    
    # Generate a potential new name by appending a timestamp
    unique_name = f"{name}_{int(time.time())}{extension}"
    
    # Check if this file already exists in the folder
    if not os.path.exists(os.path.join(base_path, unique_name)):
        return unique_name
    else:
        # If the generated name exists (very unlikely), recurse until a unique name is found
        return generate_unique_filename(base_path, unique_name)

def copy_image_to_anki_media(source_image_path, anki_media_folder_path = "/home/len1218/.local/share/Anki2/User 1/collection.media"):
    # Ensure the Anki media folder exists
    if not os.path.exists(anki_media_folder_path):
        print(f"Anki media folder does not exist: {anki_media_folder_path}")
        return

    # Copy the image to the Anki media folder
    try:
        shutil.copy(source_image_path, anki_media_folder_path)
        print(f"Successfully copied {source_image_path} to {anki_media_folder_path}")
    except Exception as e:
        print(f"Failed to copy image: {e}")

deck_name = "MyDeck"
anki_media_folder_path = "/home/len1218/.local/share/Anki2/User 1/collection.media"

# Example usage
#original_image_name = "image.jpg"
#unique_image_name = generate_unique_filename(anki_media_folder, original_image_name)

#print(f"Unique image name: {unique_image_name}")


#front_image_file = "front.jpg"  
#back_image_file = "back.jpg"    
#copy_image_to_anki_media(front_image_file)
#copy_image_to_anki_media(back_image_file)
def add_image_card_wrapper(front, back):
    front_name = generate_unique_filename(anki_media_folder_path,"Front.png")
    front_image_file = anki_media_folder_path + "/" +  front_name
    back_name =  generate_unique_filename(anki_media_folder_path,"Back.png")
    back_image_file = anki_media_folder_path + "/"+ back_name
    front.save(front_image_file)
    back.save(back_image_file)
    add_card_with_images(deck_name, front_name, back_name)

