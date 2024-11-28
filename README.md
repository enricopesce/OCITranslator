# OCI Translator

## Introduction

The OCI Translator demonstrates the power of using [Oracle Cloud Infrastructure's Generative AI services](https://www.oracle.com/artificial-intelligence/generative-ai/generative-ai-service/) to build practical language applications. 

This project showcases how Generative AI services can translate text with a modern LLM that understands context and nuances and how to integrate it into a modern web application.

### Why OCI Generative AI?

Oracle Cloud Infrastructure (OCI) Generative AI offers several compelling advantages for translation services:

- **Enterprise-Ready**: Built on OCI's robust infrastructure, ensuring high availability and scalability
- **Cost-Effective**: Pay-as-you-go pricing model with competitive rates for API calls
- **Security-First**: Enterprise-grade security with built-in governance and compliance features
- **High Performance**: Low-latency responses suitable for real-time translation needs
- **Multilingual Support**: Comprehensive support for major world languages with high accuracy
- **Context Awareness**: Advanced language models that understand context and nuances
- **Integration Friendly**: Easy integration with existing cloud infrastructure and applications

# Supported Languages

| Language   | ISO Code |
| ---------- | -------- |
| Arabic     | ar       |
| Chinese    | zh       |
| English    | en       |
| French     | fr       |
| German     | de       |
| Italian    | it       |
| Japanese   | ja       |
| Korean     | ko       |
| Portuguese | pt       |
| Spanish    | es       |

## Prerequisites

- Python 3.8 or higher
- Oracle Cloud Infrastructure account with access to Generative AI service
- OCI credentials configured

## Installation

1. Clone the repository:

```bash
git clone https://github.com/enricopesce/OCITranslator
cd oci-translator
```

2. Install required packages:

```bash
pip install -r requirements.txt
```

## Configuration

1. Create a `.env` file in the project root with your OCI credentials (env.example provided):

```env
OCI_MODEL_ID=your_model_id
OCI_SERVICE_ENDPOINT=your_service_endpoint
OCI_COMPARTMENT_ID=your_compartment_id
```

## Usage

1. Start the server:

```bash
python main.py
```

2. The API will be available at `http://localhost:8000`


### API Endpoint

#### POST /translate

Translates text between supported languages.

Request body:

```json
{
  "text": "Hello world",
  "source_language": "en",
  "target_language": "es"
}
```

Response:

```json
{
  "translated_text": "Hola mundo",
  "source_language": "en",
  "target_language": "es"
}
```

### Example Usage with cURL

```bash
curl -X POST "http://localhost:8000/translate" \
     -H "Content-Type: application/json" \
     -d '{
           "text": "Hello world",
           "source_language": "en",
           "target_language": "es"
         }'
```

## Error Handling

The API returns appropriate HTTP status codes and error messages:

- 400: Bad Request (invalid language code/name or impossible translation)
- 500: Internal Server Error (unexpected errors)

Error response format:

```json
{
  "detail": {
    "message": "Error description",
    "source_language": "Source language",
    "target_language": "Target language"
  }
}
```

## Testing by script

### Basic Usage

```bash
# Run with default settings (localhost:8000)
python test.py

# Run with custom API URL
python test.py --url http://your-api-url
```

### Sample Testing Mode

Running without parameters will execute tests using predefined sample texts in all supported languages:

```bash
python test.py
```

### Single Translation Mode

For testing a specific text with defined source and target languages:

```bash
python test.py --text "Your text here" --from en --to es
```

Parameters:

- `--text`: The text you want to translate
- `--from`: Source language code
- `--to`: Target language code

Example:

```bash
# Translate from English to Spanish
python test.py --text "Hello world" --from en --to es

# Translate from French to German
python test.py --text "Bonjour le monde" --from fr --to de
```

## Output

```bash
python test.py --text "ciao" --from it --to zh
╭──────────────────────────────────────────────── Translation Testing ─────────────────────────────────────────────────╮
│ Starting single translation test                                                                                     │
│ API URL: http://localhost:8000                                                                                       │
│ From: Italian                                                                                                        │
│ To: Chinese                                                                                                          │
│ Text: ciao                                                                                                           │
│ Timestamp: 2024-11-28 11:13:08                                                                                       │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯

Translation #2
From: Italian
To: Chinese
Original: ciao
Translated: 再见
Cultural: 再见
Time: 0.315s
Characters: 19
--------------------------------------------------------------------------------

================================================================================
Translation Summary
Total translations: 1
Failed translations: 0
Total time: 0.31s
Average time per translation: 0.315s
Total characters processed: 19
Average characters per translation: 19.0
================================================================================
```