import requests
import streamlit as st

# Set the FastAPI server URL
server_url = "http://127.0.0.1:8001"

# Fetch available models from the backend
def get_available_models():
    response = requests.get(f"{server_url}/available_models/")
    if response.status_code == 200:
        return response.json()["available_models"]
    else:
        st.error("Failed to fetch available models")
        return []

# Fetch available languages from the backend
def get_available_languages():
    response = requests.get(f"{server_url}/available_languages/")
    if response.status_code == 200:
        return response.json()["available_languages"]
    else:
        st.error("Failed to fetch available languages")
        return []

# Update the model in the backend
def update_model(new_model):
    json_body = {"new_model": new_model}
    response = requests.post(f"{server_url}/update_model/", json=json_body)
    if response.status_code == 200:
        st.success(response.json()["message"])
    else:
        st.error("Failed to update the model")

# Update the language and get the translated text
def update_language_and_get_translation(new_language, input_text):
    json_body = {"new_language": new_language, "input_text": input_text}
    response = requests.post(f"{server_url}/update_language_txt/", json=json_body)
    if response.status_code == 200:
        return response.json()["translated_text"]
    else:
        st.error("Failed to get the translation")
        return ""

# Set page configuration
st.set_page_config(
    page_title="LLM Translation App",
    page_icon="🌍",
    layout="wide",
)

# Streamlit app
st.title("LLM Translation Application 🤖")
# st.image("header_2.png", width=400)
st.subheader("Harness the power of Language Models for seamless translation  🌅")

#
st.markdown(
    """
    This application allows you to translate text using different language models. 
    Select the model and language you want to use, enter the text, and get the translated output instantly.
    """
)

# Sidebar configuration
st.sidebar.header("Configuration 🛠️")
st.sidebar.write("Use the options below to configure your translation:")

# Fetch and display available models
available_models = get_available_models()
selected_model = st.sidebar.selectbox("Select a model for translation", available_models)

# Fetch and display available languages
available_languages = get_available_languages()
selected_language = st.sidebar.selectbox("Select a language for translation", available_languages)

# Input text for translation
input_text = st.text_area("Enter the text you want to translate")

if st.button("Translate  🔄"):
    if selected_model and selected_language and input_text:
        # Update the model
        update_model(selected_model)

        # Get the translation
        translated_text = update_language_and_get_translation(selected_language, input_text)
        st.write("**Translated Text:**")
        st.write(translated_text)
    else:
        st.error("Please select a model, language, and enter text for translation.")