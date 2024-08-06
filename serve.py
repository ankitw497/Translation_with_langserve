from fastapi import FastAPI, HTTPException, Body
from pydantic import BaseModel
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_groq import ChatGroq
import os
from langserve import add_routes
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()

# Load API key from environment variables
groq_api_key = os.getenv("GROQ_API_KEY")

# List of available model names
model_names = [
    'Llama-3.1-8b-Instant',
    'Mixtral-8x7b-32768',
    'Gemma2-9b-It',
    'Gemma-7b-It'
]

# List of available languages
languages = ['French', 'German', 'Spanish', 'Hindi']

# Initialize the model with a default model
model_name = "Gemma2-9b-It"
model = ChatGroq(model=model_name, groq_api_key=groq_api_key)

# Initialize the selected language with a default language
selected_language = "French"

# Create the prompt template for translation
system_template = "Translate the following into {language}:"
prompt_template = ChatPromptTemplate.from_messages([
    ('system', system_template),
    ('user', '{text}')
])

# Initialize the output parser
parser = StrOutputParser()

# Create the translation chain by combining the prompt template, model, and parser
chain = prompt_template | model | parser

# Initialize the FastAPI app
app = FastAPI(
    title="Langchain Server",
    version="1.0",
    description="A simple API server using Langchain runnable interfaces"
)

@app.get("/available_models/")
async def get_available_models():
    """
    Endpoint to get the list of available models.
    
    Returns:
        dict: A dictionary containing the list of available models.
    """
    return {"available_models": model_names}

@app.get("/available_languages/")
async def get_available_languages():
    """
    Endpoint to get the list of available languages.
    
    Returns:
        dict: A dictionary containing the list of available languages.
    """
    return {"available_languages": languages}

# Define the request body model for updating the model
class UpdateModelRequest(BaseModel):
    new_model: str

# Define the request body model for updating the language
class LanguageTextRequest(BaseModel):
    new_language: str
    input_text:str

@app.post("/update_model/")
async def update_model(request: UpdateModelRequest):
    """
    Endpoint to update the model used for translation.
    
    Args:
        request (UpdateModelRequest): The request body containing the new model name.
    
    Returns:
        dict: A dictionary containing a success message if the model is updated successfully.
    
    Raises:
        HTTPException: If the model name is invalid or there is an error updating the model.
    """
    global model, chain
    if request.new_model not in model_names:
        raise HTTPException(status_code=400, detail="Invalid model name. Available models are: " + ", ".join(model_names))
    try:
        # Update the model with the new model name
        model = ChatGroq(model=request.new_model, groq_api_key=groq_api_key)
        # Update the chain with the new model
        chain = prompt_template | model | parser
        return {"message": f"Model updated to {request.new_model}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating model: {str(e)}")

@app.post("/update_language_txt/")
async def update_language_txt(request: LanguageTextRequest):
    """
    Endpoint to update the language used for translation.
    
    Args:
        request (UpdateLanguageRequest): The request body containing the new language.
    
    Returns:
        dict: A dictionary containing a success message if the language is updated successfully.
    
    Raises:
        HTTPException: If the language is invalid.
    """
    global selected_language, chain
    if request.new_language not in languages:
        raise HTTPException(status_code=400, detail="Invalid language. Available languages are: " + ", ".join(languages))
    try:
        # Update the selected language
        selected_language = request.new_language
        input_text = request.input_text
        # Update the prompt
        prompt_template = ChatPromptTemplate.from_messages([
            ('system', system_template.format(language=selected_language)),
            ('user', '{text}')
        ])
        # Update the chain with the new system prompt template
        chain = prompt_template | model | parser
        translated_txt = chain.invoke(input_text)
        return {"translated_text": f"{translated_txt}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating language: {str(e)}")

# Add chain routes to the FastAPI app
add_routes(
    app,
    chain,
    path="/chain"
)

if __name__ == "__main__":
    import uvicorn
    # Run the FastAPI app with uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8001)
