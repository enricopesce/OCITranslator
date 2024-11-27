# main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.chat_models.oci_generative_ai import ChatOCIGenAI
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

app = FastAPI(title="OCI Translator")

# Initialize the LLM with environment variables
llm = ChatOCIGenAI(
    model_id=os.getenv('OCI_MODEL_ID'),
    service_endpoint=os.getenv('OCI_SERVICE_ENDPOINT'),
    compartment_id=os.getenv('OCI_COMPARTMENT_ID')
)

# Rest of your code remains the same...
# Create the prompt template
prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """You are a professional translator who translates input messages to {output_language} language.
 You must reply only with the translation; nothing else.
 If it is not a literal translation exists, please provide an alternative with the best meaning.
 If it is not possible to offer any translation, please return a message starting with 
 ERROR and explain the problem intro [], example 'ERROR: [The input message does not contain any words or sentences to translate.]'
 the error message must be in English""",
        ),
        ("human", "{input}"),
    ]
)

# Create the chain
chain = prompt | llm

# Define request model
class TranslationRequest(BaseModel):
    text: str
    target_language: str

# Define response model
class TranslationResponse(BaseModel):
    translated_text: str
    target_language: str

@app.post("/translate", response_model=TranslationResponse)
async def translate_text(request: TranslationRequest):
    try:
        # Call the translation chain
        message = chain.invoke(
            {
                "output_language": request.target_language,
                "input": request.text,
            }
        )
        
        # Return the translation
        return TranslationResponse(
            translated_text=message.content,
            target_language=request.target_language
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )