import streamlit as st
from openai import OpenAI
from PIL import Image
import requests
import warnings
from io import BytesIO
warnings.filterwarnings("ignore", category=UserWarning, module='PIL')
def setup_dalle(apikey):
    """
    Sets up the OpenAI API for DALL-E image generation.
    
    Parameters:
    api_key (str): Your OpenAI API key.
    """
    openai_client = OpenAI(api_key=apikey)
    
    print("DALL-E setup complete.")
    return openai_client

def get_first_sentence(text):
    # Split the text by period
    sentences = text.split('.')
    # Return the first sentence with a period at the end
    return sentences[0] + '.'

def create_dalle_image(api_client,prompt):
    """
    Generates an image from a given prompt using DALL-E.
    
    Parameters:
    prompt (str): The prompt to generate the image from.
    
    Returns:
    str: URL of the generated image.
    """
    #clean up the prompt
    prompt = prompt.replace("\n", " ").replace("\r", " ")
    for prefix in ["A.", "B.", "C.", "D.", "E.", "F.", "A)", "B)", "C)", "D)", "E)", "F)"]:
        prompt = prompt.replace(prefix, "")
    prompt = "I NEED to test how the tool works with extremely simple prompts. DO NOT add any detail, just use it AS-IS:" + prompt
        
    try:
    # Code that uses the Streamlit component
        response = api_client.images.generate(
            model="dall-e-3",
            prompt=prompt,   
            n=1,    
            quality="standard"    
            )  
    except Exception as e:
        # Handle the exception
        print("An error occurred:", e)
        st.error("Error: An error has occured.")
        return None
   
    image_url = response.data[0].url
    response = requests.get(image_url)
    img = Image.open(BytesIO(response.content))
    return img
