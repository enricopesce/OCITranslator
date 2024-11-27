# Translation Service

A FastAPI-based translation service that uses Oracle Cloud Infrastructure (OCI) Generative AI to perform text translations.

## Features

- RESTful API endpoint for text translation
- Powered by Cohere's Command R+ model through OCI
- Support for multiple target languages
- Error handling for invalid inputs or translation failures
- Auto-reload capability for development

## Prerequisites

- Python 3.7+
- Oracle Cloud Infrastructure (OCI) account
- OCI API credentials configured
- Required Python packages (see Installation section)

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd translation-service
```

2. Install the required packages:
```bash
pip install fastapi uvicorn pydantic langchain-core langchain-community
```

3. Configure your OCI credentials according to the OCI documentation.

## Configuration

The service requires the following OCI configuration:
- Model ID: `cohere.command-r-plus-08-2024`
- Service Endpoint: `https://inference.generativeai.us-chicago-1.oci.oraclecloud.com`
- Compartment ID: Your OCI compartment ID

## Usage

1. Start the server:
```bash
python main.py
```

2. The service will be available at `http://localhost:8000`

3. API Endpoints:

### POST /translate

Translates text to the specified target language.

Request body:
```json
{
    "text": "Hello, world!",
    "target_language": "Spanish"
}
```

Response:
```json
{
    "translated_text": "¡Hola, mundo!",
    "target_language": "Spanish"
}
```

## API Documentation

Once the service is running, you can access the interactive API documentation at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Development

The service includes auto-reload functionality for development:
- Changes to Python files will automatically trigger a server restart
- The server watches the current directory for changes
- Auto-reload can be disabled by setting `reload=False` in `main.py`

## Error Handling

The service includes comprehensive error handling:
- Invalid requests return appropriate HTTP status codes
- Translation errors are returned with descriptive messages
- System errors return 500 status code with error details

## Limitations

- Translations depend on the capabilities of the Cohere Command R+ model
- Some language pairs might not be supported
- Error messages are always returned in English

## License

[Add your license information here]

## Contributing

[Add contribution guidelines here]