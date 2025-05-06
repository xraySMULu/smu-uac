import uuid
import os
import streamlit as st
from PIL import Image
from time import sleep
from streamlit_extras.app_logo import add_logo
from streamlit.components.v1 import html
from streamlit.delta_generator import DeltaGenerator
from langchain.chains.summarize import load_summarize_chain
from langchain.schema import Document
from langchain_openai import ChatOpenAI
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains.llm import LLMChain
from langchain_core.prompts import ChatPromptTemplate
import time
from llm_init import *  # Custom module for initializing the language model
from img_gen import *  # Custom module for image generation
from util import *  # Custom module for utility functions

#global variables
my_story_string = ''
scrubbed_resp = ''
# Function to authenticate API key and update session states
def auth():    
    os.environ['OPENAI_API_KEY'] = st.session_state.openai_api_key  # Set OpenAI API key
    st.session_state.genreBox_state = False  # Disable genre input box
    st.session_state.apiBox_state = True    # Enable API input box


# Configure the Streamlit page (title, icon, layout, and menu)
st.set_page_config(
    page_title='Mystic AI',  # Set page title
    page_icon=Image.open('resources/website/icons/mai.ico'),  # Set page icon
    layout='wide',  # Use wide layout
    menu_items={
        'About': "Mystic AI is a dynamic story creator built with LangChain, OpenAI and DALL-E 3"  # About section
    },
    initial_sidebar_state='expanded'  # Expand sidebar by default
)

# Set the main title of the app
st.title(f"Mystic AI")  # Display app title

# Initialize session state variables if not already set
if "llm" not in st.session_state:
    st.session_state.llm = None
if 'cols' not in st.session_state:  # Stores story sections
    st.session_state['cols'] = []
if 'keep_graphics' not in st.session_state:  # Toggle for keeping graphics
    st.session_state['keep_graphics'] = False
if 'data_dict' not in st.session_state:  # Stores story data
    st.session_state['data_dict'] = {}
if 'genreBox_state' not in st.session_state:  # Controls genre input box visibility
    st.session_state['genreBox_state'] = True
if 'apiBox_state' not in st.session_state:  # Controls API input box visibility
    st.session_state['apiBox_state'] = False
if 'openai_api_key' not in st.session_state:  # Stores OpenAI API key
    st.session_state['openai_api_key'] = ''
if 'genre_input' not in st.session_state:  # Stores user input for story genre
    st.session_state['genre_input'] = 'Use a random theme'

# Configuring the Sidebar
with st.sidebar:
    st.image('resources/website/icons/mysai.png')  # Display sidebar logo

    st.markdown('''
    Mystic AI is a dynamic story creator built with LangChain, OpenAI and DALL-E.
    ''')  # Sidebar description
    
    with st.expander('Instructions'):  # Expandable instructions section
        st.markdown('''
        - To begin Mystic AI, please enter your own OpenAI API key.
        - After entering the API keys, please enter the genre/theme of your desired story, and watch the magic unfold.
        ''')  # Instructions for using the app
    
    # Sidebar Form, wherein the user enters their API Keys. 
    with st.form(key='API Keys'):
        openai_key = st.text_input(
            label='Your OpenAI API Key', 
            key='openai_api_key',
            type='password',
            disabled=st.session_state.apiBox_state,
            help='You can create your own OpenAI API key by going to https://platform.openai.com/account/api-keys (Sign up required)'
        )       
        
        btn = st.form_submit_button(label='Begin Mystic AI!', on_click=auth)

    
    st.info('**Note:** You can close the sidebar when you enter the API keys')

# Displaying the API Key warnings
if not openai_key.startswith('sk-'): 
    st.warning('Please enter your OpenAI API Key to start Mystic AI', icon='⚠')


# Defining the functions for the actual screen
def get_story_and_image(user_resp):
    global scrubbed_resp
    scrubbed_resp = ''
    # Initialize the language model and DALL-E client
    llm_model = initialize_model()
        
    openai_client = setup_dalle(st.session_state.openai_api_key)
    
    # Timer for the story generation
    gpt_start_time = time.perf_counter()  # Start the timer     
    # Generate a response from the language model
    bot_response = llm_model.predict(input=user_resp)
    print(bot_response)
    response_list = bot_response.split("\n")
    
    # Optimization: Using Time module to return the time taken to generate the response, i was able to get a baseline result. After modifications, reponse time improved 34%
    gpt_end_time = time.perf_counter()  # end the timer
    gpt_elasped_time = gpt_end_time - gpt_start_time  # Calculate elapsed time    
    # Display the response time in the console
    print(f"GPT Response time: {gpt_elasped_time:2f} seconds")

    # Filter out empty lines and separators from the response
    responses = list(filter(lambda x: x != '' and x != '-- -- --', response_list))
    
    # Timer for the DALL-E image generation
    dalle_start_time = time.perf_counter()  # Start the timer      
    # Generate an image using DALL-E if the response contains an image prompt
    if len(response_list) != 1:
        img_prompt = response_list[-1]
        dalle_img = create_dalle_image(openai_client, img_prompt)        
    else:
        dalle_img = None
    
    dalle_end_time = time.perf_counter()  # end the timer
    dalle_elasped_time = dalle_end_time - dalle_start_time  # Calculate elapsed time     
    print(f"DALLE Response Time: {dalle_elasped_time:2f} seconds")

    # Remove unwanted lines related to image generation from the response
    responses = list(filter(lambda x: 'DALL-E' not in x and 'Image prompt' not in x, responses))
    
    # Parse the response into story, label, and options
    opts = []
    story = ''
    label = ''
    
    for response in responses:
        response = response.strip()  
        
        try:
            if response.startswith(('What', 'Which', 'Choose')):
                label = f'**{response}**'
            elif response[1:2] in {'.', ')'} or response[1:6] == ' --' or response.startswith('Option'):
                opts.append(response)
            else:
                #clean up the response
                scrubbed_resp = response
                scrubbed_resp = scrubbed_resp.replace("\n", " ").replace("\r", " ")
                for prefix in ["Prompt:", "Visual Prompt:", "Image Prompt:", "A.", "B.", "C.", "D.", "E.", "F.", "A)", "B)", "C)", "D)", "E)", "F)"]:
                    scrubbed_resp = scrubbed_resp.replace(prefix, "")               
                story += f'{scrubbed_resp}\n'
        except IndexError:
            print(f"IndexError: The response '{response}' is too short to check the specified index.")
            st.switch_page('app.py')  # Navigate to an error page if the response is too short
    
    # Return the parsed story, label, options, and generated image
    if not story:
        story = 'This fantasy story is about embarking on an epic quest. The hero must make crucial decisions that will shape their destiny and the fate of the realm.'  # Default story if none is provided
    
    if not label:
        label = f'**What would you like to do next?**'  # Default label if none is provided    

    # Check if the number of options exceeds 6
    if len(opts) > 6:        
        opts = trim_lst(opts)  # Validate the options list
    elif len(opts) < 6:  # If less than 6 options
        # Ensure the options list contains all required values
        opts = ensure_lst_values(opts)

    return {
        'Story': story,
        'Radio Label': label,
        'Options': opts,
        'Image': dalle_img
    }

@st.cache_data(show_spinner='Generating your story...')
# Function to handle user input, generate story content, and update session state
def get_output(_pos: DeltaGenerator, el_id='', genre=''):
    st.session_state.keep_graphics = True
    
    if el_id:        
        st.session_state['genreBox_state'] = True
        st.session_state[f'expanded_{el_id}'] = False
        st.session_state[f'radio_{el_id}_disabled'] = True
        st.session_state[f'submit_{el_id}_disabled'] = True

        user_choice = st.session_state[f'radio_{el_id}']
    
    if genre:         
        st.session_state['genreBox_state'] = False
        user_choice = genre
    
    with _pos:    
        data = get_story_and_image(user_choice)
        add_new_data(data['Story'], data['Radio Label'], data['Options'], data['Image'])
    
# Function to generate content for each story section
# This function creates an expander for each part of the story, displaying the story text, options, and image
# It also handles user interactions, such as submitting choices and summarizing the story    
def generate_content(story, lbl_text, opts: list, img, el_id):   
 
    global my_story_string
    my_story_string = ''
    prompt_template = """
    Create a story title. For each section, make a section title and a short paragraph of 1-2 sentences:
    Context:{text}
    """
    prompt = PromptTemplate(template=prompt_template, input_variables=["text"])   

    if f'expanded_{el_id}' not in st.session_state:
        st.session_state[f'expanded_{el_id}'] = True
    if f'radio_{el_id}_disabled' not in st.session_state:
        st.session_state[f'radio_{el_id}_disabled'] = False
    if f'submit_{el_id}_disabled' not in st.session_state:
        st.session_state[f'submit_{el_id}_disabled'] = False
    
    story_pt = list(st.session_state["data_dict"].keys()).index(el_id) + 1
    expander = st.expander(f'Part {story_pt}', expanded=st.session_state[f'expanded_{el_id}'])   
    col1, col2 = expander.columns([0.65, 0.35])
    empty = st.empty()
    if img:
        col2.image(img, width=40, use_container_width=True)
    
    with col1:
        st.write(story)        
        if lbl_text and opts:
            with st.form(key=f'user_choice_{el_id}'): 
                st.radio(lbl_text, opts, disabled=st.session_state[f'radio_{el_id}_disabled'], key=f'radio_{el_id}')                
                st.form_submit_button(
                    label="Let's do this!", 
                    disabled=st.session_state[f'submit_{el_id}_disabled'], 
                    on_click=get_output, args=[empty], kwargs={'el_id': el_id}
                )
            if st.button("Summarize Story", key=f'summarize_{el_id}'):  # Button to summarize the story        
                try:
                    with st.spinner("Fetching and summarizing story..."):                       
                        llm = ChatOpenAI(model="gpt-4o-mini")                                                
                        
                        dd_story ={}
                        dd_story = st.session_state['data_dict']
                        lst_cols=[]
                        lst_cols= st.session_state['cols']    
                        #iterate data dict, passing part id, returning story to build out page summary
                        for cls in lst_cols:
                            story_obj = dd_story[cls]
                            my_story_string += story_obj[0] + '\n'                      
                        
                        text = my_story_string
                        # Create a document object for summarization
                        document = Document(page_content=text)

                        # Chain for summarization using the defined prompt template
                        chain = load_summarize_chain(llm, chain_type="stuff", prompt=prompt)
                        result = chain.invoke({"input_documents": [document]})
                        output_summary = result.get("output_text", "No summary available.")
                        st.success(output_summary)
                except Exception as e:
                    st.exception(f"Exception: {e}")

# Function to add new data to the session state
# This function generates a unique ID for each new story section and appends it to the session state
def add_new_data(*data):   
    el_id = str(uuid.uuid4())
    st.session_state['cols'].append(el_id)
    st.session_state['data_dict'][el_id] = data
    

# Genre Input widgets
with st.container():
    # Create three columns for input, clear button, and begin button
    col_1, col_2, col_3 = st.columns([8, 1, 1], gap='small')
    
    # Text input for entering the story theme/genre
    col_1.text_input(
        label='Enter the theme of your story',
        key='genre_input',
        placeholder='Enter the theme of the story', 
        disabled=st.session_state.genreBox_state
    )
    
    # Clear button to reset the genre input field
    col_2.write('')
    col_2.write('')
    col_2_cols = col_2.columns([0.5, 6, 0.5])
    col_2_cols[1].button(
        ':arrows_counterclockwise: &nbsp; Clear', 
        key='clear_btn',
        on_click=lambda: setattr(st.session_state, "genre_input", ''),
        disabled=st.session_state.genreBox_state
    )
    
    # Begin button to start generating the story
    col_3.write('')
    col_3.write('')
    begin = col_3.button(
        'Begin story →',
        on_click=get_output, args=[st.empty()], kwargs={'genre': st.session_state.genre_input},
        disabled=st.session_state.genreBox_state
    )
    
# Generate content for each story section stored in session state
for col in st.session_state['cols']:
    data = st.session_state['data_dict'][col]
    generate_content(data[0], data[1], data[2], data[3], col)