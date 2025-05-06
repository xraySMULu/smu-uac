import streamlit as st
from openai import OpenAI
from PIL import Image
from io import BytesIO
import random

#fucntion to cleanup the list
def trim_lst(lst):
    
    # Initialize an empty list to store the ordered options
    opts_rtn = []
    opts_ordered_1 = []
    opts_ordered_2 = []
       
    # Iterate through the responses and keep only the first 6 values corresponding to A) to F)
    for op in lst:
        if op.startswith(('A)', 'B)', 'C)', 'D)', 'E)', 'F)')):
            opts_ordered_1.append(op)
        if len(opts_ordered_1) == 6:
            break
        elif op.startswith(('A.', 'B.', 'C.', 'D.', 'E.', 'F.')):
            opts_ordered_2.append(op)
        if len(opts_ordered_2) == 6:
            break    
    # Sort the options based on the desired order
    opts_rtn = sort_lst(opts_ordered_1, opts_ordered_2)

    return opts_rtn
# function to ensure the list has all values
def ensure_lst_values(lst):
    required_values = ['A', 'B', 'C', 'D', 'E', 'F']
    #default_value = "Think about what you want to do next."

     #used for the default label
    # If no label is provided by AI, use a random fantasy prompt
    fantasy_prompts = [
    "Discover the hidden forest of secrets.",
    "Seek the ancient artifact of power.",
    "Unravel the mystery of the lost city.",
    "Find the enchanted river of dreams.",
    "Explore the haunted castle on the hill.",
    "Journey to the land of forgotten magic.",
    "Unearth the buried treasure of legends.",
    "Follow the path of the wandering stars.",
    "Unlock the door to the shadow realm.",
    "Venture into the cave of whispers.",
    "Cross the bridge to the unknown lands.",
    "Search for the mythical beast of lore.",
    "Navigate the labyrinth of endless night.",
    "Ascend the mountain of eternal light.",
    "Enter the portal to otherworldly realms."
    ]    

    # Create a set of the first characters in the list
    existing_values = {item[0] for item in lst}

    # Check for missing values and add them with the default value
    for value in required_values:
        random.shuffle(fantasy_prompts)  # Shuffle the list of fantasy prompts
        # Select a random prompt from the shuffled list
        default_value = f"{fantasy_prompts[0]}"
        if value not in existing_values:
            lst.append(f"{value}) {default_value}")
    
    # Sort the list based on the desired order
    lst = sort_lst_by_char1(lst)
    # Return the updated list
    return lst
# function to sort the list by the first character
def sort_lst_by_char1(lst):
    lst_rtn = []
    # Define the desired order
    desired_order = ['A', 'B', 'C', 'D', 'E', 'F']
    
    # Filter and sort the ops based on the desired order
    opts1 = sorted(
        [op for op in lst if op[:1] in desired_order],
        key=lambda x: desired_order.index(x[:1])
    )

    if len(opts1) == 6:
        lst_rtn = opts1
    
    return lst_rtn
# function to sort and select best lst
def sort_lst(lst1,lst2):
    lst_rtn = []
    # Define the desired order
    desired_order_1 = ['A)', 'B)', 'C)', 'D)', 'E)', 'F)']
    desired_order_2 = ['A.', 'B.', 'C.', 'D.', 'E.', 'F.']

    # Filter and sort the ops based on the desired order
    opts1 = sorted(
        [op for op in lst1 if op[:2] in desired_order_1],
        key=lambda x: desired_order_1.index(x[:2])
    )       
    opts2 = sorted(
        [op for op in lst2 if op[:2] in desired_order_2],
        key=lambda x: desired_order_2.index(x[:2])
    )

    if len(opts1) == 6:
        lst_rtn = opts1
    elif len(opts2) == 6:   
        lst_rtn = opts2
    return lst_rtn