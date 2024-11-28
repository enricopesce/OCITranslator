from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.chat_models.oci_generative_ai import ChatOCIGenAI
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

app = FastAPI(title="OCI Translator")

# Language code mapping
LANGUAGE_CODES = {
    "ar": "Arabic",
    "zh": "Chinese",
    "en": "English",
    "fr": "French",
    "de": "German",
    "it": "Italian",
    "ja": "Japanese",
    "ko": "Korean",
    "pt": "Portuguese",
    "es": "Spanish"
}

# Reverse mapping for validation
LANGUAGE_NAMES = {v.lower(): k for k, v in LANGUAGE_CODES.items()}

# Initialize the LLM with environment variables
llm = ChatOCIGenAI(
    model_id=os.getenv('OCI_MODEL_ID'),
    service_endpoint=os.getenv('OCI_SERVICE_ENDPOINT'),
    compartment_id=os.getenv('OCI_COMPARTMENT_ID'),
    model_kwargs={"temperature": 0.0, "max_tokens": 1024}
)

# Create the prompt template
prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """You are a professional {input_language} to {output_language} translator. Rules:

1. Provide translation only, no explanations
2. For idioms/cultural phrases use the cultural equivalent

3. If translation impossible, respond:
ERROR: [reason in English]
""",
        ),
        ("human", "{input}"),
    ]
)

# Create the chain
chain = prompt | llm

# Define request model with validation
class TranslationRequest(BaseModel):
    text: str
    source_language: str
    target_language: str

    def get_language_name(self, code_or_name: str) -> str:
        """Convert language code or name to full language name."""
        if code_or_name.lower() in [name.lower() for name in LANGUAGE_CODES.values()]:
            return code_or_name.capitalize()
        elif code_or_name.lower() in LANGUAGE_NAMES:
            return LANGUAGE_CODES[code_or_name.lower()].capitalize()
        elif code_or_name in LANGUAGE_CODES:
            return LANGUAGE_CODES[code_or_name].capitalize()
        else:
            raise ValueError(f"Unsupported language: {code_or_name}")

# Define response model
class TranslationResponse(BaseModel):
    translated_text: str
    source_language: str
    target_language: str

@app.post("/translate", response_model=TranslationResponse)
async def translate_text(request: TranslationRequest):
    try:
        # Convert language codes/names to full names
        try:
            source_lang = request.get_language_name(request.source_language)
            target_lang = request.get_language_name(request.target_language)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

        # Call the translation chain
        message = await chain.ainvoke(
            {
                "input_language": source_lang,
                "output_language": target_lang,
                "input": request.text,
            }
        )
        
        # Check if the response starts with "ERROR:"
        if message.content.startswith("ERROR:"):
            # Extract the error message from within the square brackets
            error_start = message.content.find("[")
            error_end = message.content.find("]")
            if error_start != -1 and error_end != -1:
                error_message = message.content[error_start + 1:error_end]
            else:
                error_message = message.content[6:].strip()  # Remove "ERROR:" prefix
            
            raise HTTPException(
                status_code=400,
                detail={
                    "message": error_message,
                    "source_language": source_lang,
                    "target_language": target_lang
                }
            )
        
        # Return the translation if no error
        return TranslationResponse(
            translated_text=message.content,
            source_language=source_lang,
            target_language=target_lang
        )
    except HTTPException:
        raise  # Re-raise HTTP exceptions as they are already formatted
    except Exception as e:
        # Handle any other unexpected errors
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )