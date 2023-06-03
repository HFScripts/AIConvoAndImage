import openai
import os
import re
import argparse
import random
import json
import requests
import time
import pprint
import base64
import tkinter as tk
import sys
import threading
import pygame
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import datetime
import pygetwindow as gw


def display_menu(your_name, chatGPT_name, personality, race, character_class, hair_color, eye_color, breast_size, skin_color, outfit_type):
    print("-" * 80)
    print(f"Hello {your_name}, you are speaking with {chatGPT_name}, a {personality.name} {race.name} {character_class.name} with {hair_color.name} hair, {eye_color.name} eyes, {breast_size.name} breasts, {skin_color.name} skin, wearing {outfit_type.name} outfit.")
    print("-" * 80)

def clear_screen():
    """Clears the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')

def read_api_key(file_path):
    with open(file_path, 'r') as file:
        return file.read().strip()

def get_gpt_response(messages, max_retries=5):
    retry_count = 0
    while retry_count <= max_retries:
        try:
            total_tokens = sum(len(message['content'].split()) for message in messages)
            if total_tokens > 4000:
                while total_tokens > 4000:
                    messages[-1]['content'] = messages[-1]['content'][:-1]
                    total_tokens -= 1

            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=messages,
                max_tokens=3000,
                n=1,
                stop=None,
                temperature=0.5,
            )
            return response.choices[0].message['content']
        except openai.error.RateLimitError:
            retry_count += 1
            if retry_count <= max_retries:
                print(f"Rate limit error, retrying ({retry_count}/{max_retries})...")
                continue
            else:
                raise

def create_message(role, content):
    return {"role": role, "content": content}

def generate_questions(chatGPT_name, personality, race, character_class, user_content, your_name, conversation, previous_message):
    return [
        create_message("system", f"You are my {chatGPT_name}, you are here to role play and entertain me.\nYour Character Name: {chatGPT_name}\nYour character traits:\nPersonality: {personality.name}\nRace: {race.name}\nClass: {character_class.name}\n\n"),
        create_message("user", f"IMPORTANT! 1. Reply in character at all times\n 2. My name is: {your_name}\n\nOur message history for context:\n```\n{conversation}\n```\n Your last message to me: \n```{previous_message}```\n\nMy reply: {user_content}")
    ]

def get_user_choice(options):
    while True:
        print("ChatGPT will be a:")
        for i, opt in enumerate(options, 1):
            print(f"{i}. {opt}")
        choice = input()
        if choice.isdigit() and int(choice) in range(1, len(options) + 1):
            return options[int(choice) - 1]
        else:
            print("Invalid choice. Please enter a valid option number.")

def get_user_input(your_name):
    try:
        user_content = input(f"{your_name}: ")
    except TimeoutError:
        user_content = "Ask me questions..."
    return user_content

def generate_stable_response(messages):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
        max_tokens=2000,
        n=1,
        stop=None,
        temperature=0.5,
    )
    return response.choices[0].message['content'].strip()


# Start the chat
def start_chat():
    previous_message = "We haven no previous messages yet, we just met"
    display_menu(your_name, chatGPT_name, personality, race, character_class, hair_color, eye_color, breast_size, skin_color, outfit_type)
    conversation = "We have NO conversation history. Wait for more information"

    user_content = ""
    character_response = get_gpt_response(
        generate_questions(chatGPT_name, personality, race, character_class, user_content, your_name, conversation, previous_message)
    )

    print_conversation(chatGPT_name, character_response) 
    handle_token_limit(chatGPT_name, personality, race, character_class, user_content, your_name, conversation, previous_message)

# Print the conversation in the desired format
def print_conversation(chatGPT_name, character_response):
    print("")
    print(f"{chatGPT_name}\033[0m: {character_response}")
    print("")

# Handle the token limit while maintaining the conversation
def handle_token_limit(chatGPT_name, personality, race, character_class, user_content, your_name, conversation, previous_message):
    max_tokens = 3000
    total_tokens = 0
    message_history = []
    conversation = []

    while total_tokens < max_tokens:
        user_content = get_user_input(your_name)

        previous_message = get_gpt_response(
            generate_questions(chatGPT_name, personality, race, character_class, user_content, your_name, conversation, previous_message)
        )

        total_tokens = update_message_history_and_tokens(previous_message, user_content, message_history, total_tokens, max_tokens)

        conversation = " ".join(message_history)

        print_conversation_with_highlights(previous_message)

        generate_stable_diffusion_prompts(previous_message, example_prompt_list)

# Update the message history and the token count
def update_message_history_and_tokens(previous_message, user_content, message_history, total_tokens, max_tokens):
    previous_tokens = len(previous_message.split())
    total_tokens += previous_tokens

    message_history.append(previous_message)
    message_history.append(user_content)

    while total_tokens > max_tokens:
        total_tokens = manage_excess_tokens(message_history, total_tokens, max_tokens)
    return total_tokens

# Handle the situation when total tokens exceed the maximum tokens
def manage_excess_tokens(message_history, total_tokens, max_tokens):
    first_message_tokens = len(message_history[0].split())
    if first_message_tokens <= (total_tokens - max_tokens):
        total_tokens -= first_message_tokens
        message_history.pop(0)
    else:
        chars_to_remove = total_tokens - max_tokens
        message_history[0] = message_history[0][chars_to_remove:]
        total_tokens = max_tokens
    return total_tokens

# Print the conversation with name highlights
def print_conversation_with_highlights(previous_message):
    
    if your_name in previous_message:
        highlighted_name = f"{your_name}\033[0m"
        previous_message = previous_message.replace(your_name, highlighted_name)

    modified_message = previous_message.replace(f"{chatGPT_name}:", "")
    print_conversation(chatGPT_name, modified_message)

# Generate the stable diffusion prompts
def generate_stable_diffusion_prompts(previous_message, example_prompt_list):
    GPT_prompt = f"\n```{example_prompt_list}``` \n\n\nbased on the example stable diffusion prompts, create EXACTLY 1 different stable diffusion prompt for the text below following the same format:\n Context to generate prompt: ```'{previous_message}'```"
    messages = []
    how_many_prompts = 1
    messages.append({"role": "user", "content": GPT_prompt})
    generate_and_print_stable_diffusion_responses(messages, previous_message)

# Generate and print the stable diffusion responses
def generate_and_print_stable_diffusion_responses(messages, previous_message):
    stable_diffusion_command = generate_stable_response(messages)
    responses = split_and_clean_responses(stable_diffusion_command)

    for i, response in enumerate(responses, 1):
        print_diffusion_prompt(response, previous_message)

# Split and clean the stable diffusion responses
def split_and_clean_responses(stable_diffusion_command):
    responses = stable_diffusion_command.split('\n')
    responses = [response.split('. ', 1)[-1].strip() for response in responses if response.strip()]
    return responses

# Print the diffusion prompt
def print_diffusion_prompt(response, previous_message):
    response_with_variables = response.format(
        chatGPT_name=chatGPT_name,
        personality=personality.name,
        race=race.name,
        character_class=character_class.name,
        hair_color=hair_color.name,
        eye_color=eye_color.name,
        breast_size=breast_size.name,
        skin_color=skin_color.name,
        outfit_type=outfit_type.name,
        scene=scene.name
    )
    response_without_prefix = remove_prompt_prefixes(response_with_variables)
    
    if response_without_prefix.count(',') >= 4:
        config = parseArguments(response_without_prefix)
        runQuery(config)

# Remove '* prompt:' prefixes from the response
def remove_prompt_prefixes(response_with_variables):
    response_with_variables = re.sub(r'.*prompt ?: ', '', response_with_variables, flags=re.IGNORECASE)
    return response_with_variables.strip("'")

# Read the API key from key.txt
openai.api_key = read_api_key('../key.txt')

class Character:
    def __init__(self, attribute_list, name):
        self.attribute_list = attribute_list
        self.name = name

# Prompt user for attribute selections
def select_attribute(attribute):
    clear_screen()
    print(f"ChatGPT will be a {attribute.name}:")
    for i, attr in enumerate(attribute.attribute_list, start=1):
        print(f"{i}. {attr}")
    choice = int(input())
    attribute.name = attribute.attribute_list[choice - 1]

# Global variable to store the current image file name
current_image = None
image_update_in_progress = False

def runQuery(config):
    url = config["url"]
    del config["url"]

    if config["outfile"] == "":
        outfile = "result." + config["output_format"]
    else:
        outfile = config["outfile"]
    del config["outfile"]

    payload = json.dumps(config, indent=3)

    req = requests.post(url + "/render", data=payload)
    stream = json.loads(req.text)["stream"]
    decoder = json.JSONDecoder()

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    new_outfile = f"result_{timestamp}.{config['output_format']}"

    while True:
        time.sleep(1)
        req = requests.get(url + stream)
        if req.text != "":
            data = decoder.raw_decode(req.text)[0]
            if "step" in data:
                t = (data["total_steps"] - data["step"]) * data["step_time"]
            if "status" in data:
                if data["status"] == "succeeded":
                    header, encoded = data["output"][0]["data"].split(",", 1)
                    data = base64.b64decode(encoded)
                    try:
                        with open(new_outfile, "wb") as f:
                            f.write(data)
                    except PermissionError:
                        print("Permission denied. Unable to write to the file:", new_outfile)
                    except IOError as e:
                        print("An error occurred while writing to the file:", e)
                    break

def parseArguments(response_without_prefix):
    rnd = random.randrange(4000000000)

    config = {
        "prompt": response_without_prefix,
        "negative_prompt": "",
        "height": "512",
        "width": "512",
        "guidance_scale": "7.5",
        "steps": 25,
        "num_outputs": 1,
        "output_format": "png",
        "render_device": "0",
        "sampler_name": "euler_a",
        "seed": rnd,
        "session_id": "txt2img",
        "turbo": "true",
        "use_full_precision": "false",
        "use_stable_diffusion_model": "revAnimated_v122",
        "use_vae_model": "",
        "save_to_disk_path": "",
        "url": "http://192.168.1.30:9090",
        "outfile": ""  # Add the 'outfile' key with a default value
    }

    return config

personality = Character(["Flirty", "Strict", "Teacher", "Bully", "Happy", "Angry", "Sad", "Calm"], 'personality')
select_attribute(personality)

race = Character(["Human", "Elf", "Dwarf", "Orc"], 'race')
select_attribute(race)

character_class = Character(["Warrior", "Mage", "Thief", "Cleric"], 'character class')
select_attribute(character_class)

hair_color = Character(["Black", "Brown", "Blonde", "Red", "Gray"], 'hair color')
select_attribute(hair_color)

breast_size = Character(["Small", "Medium", "Large"], 'breast size')
select_attribute(breast_size)

eye_color = Character(["Blue", "Green", "Brown", "Hazel"], 'eye color')
select_attribute(eye_color)

outfit_type = Character(["Fantasy red panties and bra", "Fantasy steel armor and gold trim", "Fantasy black robe", "Nude"], 'outfit type')
select_attribute(outfit_type)

skin_color = Character(["Fair", "Tan", "Dark", "Pale"], 'skin color')
select_attribute(skin_color)

scene = Character(["tavern", "alley", "empty room", "castle"], 'scene location')
select_attribute(scene)

# Check attributes and print the appropriate statement
if (
    personality.name != "personality"
    and race.name != "race"
    and character_class.name != "character class"
    and hair_color.name != "hair color"
    and breast_size.name != "breast size"
    and eye_color.name != "eye color"
    and outfit_type.name != "outfit type"
    and skin_color.name != "skin color"
    and scene.name != "scene location"
):
    clear_screen()
    print(
        f"ChatGPT is a {personality.name} {race.name} {character_class.name} with {hair_color.name} hair, {eye_color.name} eyes, {breast_size.name} breasts, {skin_color.name} skin, and wearing {outfit_type.name} outfit."
        f"Starting scene: {scene.name}"
    )

# ChatGPT roleplay name
chatGPT_name = input('What shall ChatGPT be called: ')
clear_screen()

# Your name
your_name = input(f"What shall {chatGPT_name} refer to you as: ")
clear_screen()

previous_message = "This is our first message"

example_prompt_list = [
    "example Prompt: {chatGPT_name}, {personality}, {race}, {character_class}, {hair_color} hair, {eye_color} eyes, {breast_size} breasts, {skin_color} skin, wearing {outfit_type} outfit, {scene}, happy, Studio Quality, 6k , toa, toaair, 1boy, glowing, axe, mecha, science_fiction, solo, weapon, jungle, green_background, nature, outdoors, solo, tree, weapon, mask, dynamic lighting, detailed shading, digital texture painting",
    "example Prompt: {chatGPT_name}, {personality}, {race}, {character_class}, {hair_color} hair, {eye_color} eyes, {breast_size} breasts, {skin_color} skin, wearing {outfit_type} outfit, {scene}, sad, Masterpiece, Studio Quality, 6k , toa, toaair, 1boy, glowing, axe, mecha, science_fiction, solo, weapon, jungle , green_background, nature, outdoors, solo, tree, weapon, mask, dynamic lighting, detailed shading, digital texture painting",
    "example Prompt: {chatGPT_name}, {personality}, {race}, {character_class}, {hair_color} hair, {eye_color} eyes, {breast_size} breasts, {skin_color} skin, wearing {outfit_type} outfit, {scene}, upset, portrait, fine details. Anime. realistic shaded lighting by Ilya Kuvshinov Giuseppe Dangelico Pino and Michael Garmash and Rob Rey, IAMAG premiere, WLOP matte print, cute freckles, masterpiece",
    "example Prompt: {chatGPT_name}, {personality}, {race}, {character_class}, {hair_color} hair, {eye_color} eyes, {breast_size} breasts, {skin_color} skin, wearing {outfit_type} outfit, {scene}, fearful, young Disney socialite, small neckless, cute-fine-face, anime. illustration, realistic shaded perfect face, fine details, realistic shaded lighting by ilya kuvshinov giuseppe dangelico pino and michael garmash and rob rey, iamag premiere, wlop matte print, 4k resolution, a masterpiece",
    "example Prompt: {chatGPT_name}, {personality}, {race}, {character_class}, {hair_color} hair, {eye_color} eyes, {breast_size} breasts, {skin_color} skin, wearing {outfit_type} outfit, {scene}, scared, unreal engine, cozy indoor lighting, artstation, detailed, digital painting,cinematic,character design by mark ryden and pixar and hayao miyazaki, unreal 5, daz, hyperrealistic, octane render",
    "example Prompt: {chatGPT_name}, {personality}, {race}, {character_class}, {hair_color} hair, {eye_color} eyes, {breast_size} breasts, {skin_color} skin, wearing {outfit_type} outfit, {scene}, aggressive, cute girl, crop-top, black glasses, stretching, with background by greg rutkowski makoto shinkai kyoto animation key art feminine mid shot",
    "example Prompt: {chatGPT_name}, {personality}, {race}, {character_class}, {hair_color} hair, {eye_color} eyes, {breast_size} breasts, {skin_color} skin, wearing {outfit_type} outfit, {scene}, angry, the street of a medieval fantasy town, at dawn, dark, 4k, highly detailed",
]

start_chat()
