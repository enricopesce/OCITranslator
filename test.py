import requests
from typing import List
from rich.console import Console
from rich.table import Table
import time
import argparse
from datetime import datetime

LANGUAGES = {
    "Arabic": {
        "iso_code": "ar",
        "sample_texts": [
            "التكنولوجيا تتطور بسرعة كبيرة",  # Technology evolves rapidly
            "أحب برمجة الكمبيوتر",  # I love computer programming
            "العلم نور والجهل ظلام"  # Knowledge is light and ignorance is darkness
        ]
    },
    "Chinese": {
        "iso_code": "zh",
        "sample_texts": [
            "科技发展日新月异",  # Technology develops rapidly
            "我喜欢编程",  # I love programming
            "知识就是力量"  # Knowledge is power
        ]
    },
    "English": {
        "iso_code": "en",
        "sample_texts": [
            "Technology evolves rapidly",
            "I love computer programming",
            "Knowledge is power"
        ]
    },
    "French": {
        "iso_code": "fr",
        "sample_texts": [
            "La technologie évolue rapidement",
            "J'aime la programmation informatique",
            "Le savoir est le pouvoir"
        ]
    },
    "German": {
        "iso_code": "de",
        "sample_texts": [
            "Technologie entwickelt sich schnell",
            "Ich liebe Computerprogrammierung",
            "Wissen ist Macht"
        ]
    },
    "Italian": {
        "iso_code": "it",
        "sample_texts": [
            "La tecnologia si evolve rapidamente",
            "Amo la programmazione del computer",
            "La conoscenza è potere"
        ]
    },
    "Japanese": {
        "iso_code": "ja",
        "sample_texts": [
            "技術は急速に進化する",
            "コンピュータープログラミングが大好きです",
            "知識は力なり"
        ]
    },
    "Korean": {
        "iso_code": "ko",
        "sample_texts": [
            "기술은 빠르게 발전합니다",
            "컴퓨터 프로그래밍을 좋아합니다",
            "지식이 힘이다"
        ]
    },
    "Portuguese": {
        "iso_code": "pt",
        "sample_texts": [
            "A tecnologia evolui rapidamente",
            "Eu amo programação de computadores",
            "Conhecimento é poder"
        ]
    },
    "Spanish": {
        "iso_code": "es",
        "sample_texts": [
            "La tecnología evoluciona rápidamente",
            "Me encanta la programación de computadoras",
            "El conocimiento es poder"
        ]
    }
}

def list_available_languages():
    """List all available languages with their details."""
    console = Console()
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Language")
    table.add_column("ISO Code")
    table.add_column("Sample Texts Count")

    for lang, info in sorted(LANGUAGES.items()):
        table.add_row(
            lang,
            info["iso_code"],
            str(len(info["sample_texts"]))
        )

    console.print("\n=== Available Languages ===")
    console.print(table)

def validate_languages(languages: List[str]) -> List[str]:
    """Validate the provided languages and return valid ones."""
    valid_languages = []
    invalid_languages = []
    
    for lang in languages:
        if lang in LANGUAGES:
            valid_languages.append(lang)
        else:
            invalid_languages.append(lang)
    
    if invalid_languages:
        console = Console()
        console.print(f"\n[yellow]Warning: The following languages are not supported: {', '.join(invalid_languages)}[/yellow]")
        console.print("Use --list-languages to see available languages.")
    
    return valid_languages

def log_result(console: Console, result: dict, stats: dict):
    """Log translation result in real-time with timestamp and update character counts."""
    timestamp = datetime.now().strftime("%H:%M:%S")
    
    if result.get("status") == "success":
        translated_text = result['translated_text']
        # Check if translation starts with ERROR
        if translated_text.startswith("ERROR"):
            stats["failed"] += 1
            stats["successful"] -= 1  # Correct the successful count since we're treating this as an error
            console.print(f"[{timestamp}] [red]✗[/red] {result['source_lang']} ({result['source_iso']}) → {result['target_lang']} ({result['target_iso']})")
            console.print(f"   Source: {result['original_text']}")
            console.print(f"   Error: {translated_text}\n")
        else:
            # Update character counts for successful translations only
            input_chars = len(result['original_text'])
            output_chars = len(translated_text)
            stats["total_input_chars"] += input_chars
            stats["total_output_chars"] += output_chars
            
            console.print(f"[{timestamp}] [green]✓[/green] {result['source_lang']} ({result['source_iso']}) → {result['target_lang']} ({result['target_iso']})")
            console.print(f"   Source: {result['original_text']}")
            console.print(f"   Translation: {translated_text}")
            console.print(f"   Characters: {input_chars} → {output_chars}\n")
    else:
        console.print(f"[{timestamp}] [red]✗[/red] {result['source_lang']} ({result['source_iso']}) → {result['target_lang']} ({result['target_iso']})")
        console.print(f"   Source: {result['original_text']}")
        console.print(f"   Error: {result.get('error', 'Unknown error')}\n")

def test_translation_service(base_url: str = "http://localhost:8000", source_languages: List[str] = None):
    console = Console()
    
    # Validate source languages
    if source_languages:
        source_languages = validate_languages(source_languages)
    else:
        source_languages = sorted(LANGUAGES.keys())

    if not source_languages:
        console.print("[red]Error: No valid source languages specified for testing.[/red]")
        return

    # Get all available languages as targets
    target_languages = sorted(LANGUAGES.keys())

    # Print test configuration
    console.print("\n=== Translation Service Test Configuration ===")
    console.print(f"Base URL: {base_url}")
    console.print(f"Source Language(s): {', '.join(source_languages)}")
    console.print(f"Target Languages: All available languages")
    console.print("=" * 50 + "\n")

    # Initialize statistics
    stats = {
        "total": 0,
        "successful": 0,
        "failed": 0,
        "total_input_chars": 0,
        "total_output_chars": 0,
        "start_time": datetime.now()
    }

    # Test translations
    for source_language in source_languages:
        console.print(f"\n[bold cyan]=== Testing translations from {source_language} ===[/bold cyan]\n")
        
        # Get sample texts for the source language
        for text in LANGUAGES[source_language]["sample_texts"]:
            # Test translation to all other languages
            for target_language in [lang for lang in target_languages if lang != source_language]:
                try:
                    stats["total"] += 1
                    source_iso = LANGUAGES[source_language]["iso_code"]
                    target_iso = LANGUAGES[target_language]["iso_code"]
                    
                    # Prepare request
                    payload = {
                        "text": text,
                        "target_language": target_iso
                    }
                    
                    # Make request
                    response = requests.post(
                        f"{base_url}/translate",
                        json=payload,
                        timeout=10
                    )
                    
                    # Process result
                    if response.status_code == 200:
                        result = response.json()
                        stats["successful"] += 1  # This might be decremented in log_result if ERROR is found
                        log_result(console, {
                            "status": "success",
                            "source_lang": source_language,
                            "target_lang": target_language,
                            "source_iso": source_iso,
                            "target_iso": target_iso,
                            "original_text": text,
                            "translated_text": result["translated_text"]
                        }, stats)
                    else:
                        stats["failed"] += 1
                        log_result(console, {
                            "status": "error",
                            "source_lang": source_language,
                            "target_lang": target_language,
                            "source_iso": source_iso,
                            "target_iso": target_iso,
                            "original_text": text,
                            "error": f"HTTP {response.status_code}"
                        }, stats)
                    
                    time.sleep(0.5)  # Small delay to prevent rate limiting
                        
                except Exception as e:
                    stats["failed"] += 1
                    log_result(console, {
                        "status": "error",
                        "source_lang": source_language,
                        "target_lang": target_language,
                        "source_iso": source_iso,
                        "target_iso": target_iso,
                        "original_text": text,
                        "error": str(e)
                    }, stats)
    
    # Print final statistics
    duration = datetime.now() - stats["start_time"]
    console.print("\n=== Test Statistics ===")
    console.print(f"Total translations attempted: {stats['total']}")
    console.print(f"Successful translations: [green]{stats['successful']}[/green]")
    console.print(f"Failed translations: [red]{stats['failed']}[/red]")
    success_rate = (stats['successful'] / stats['total'] * 100) if stats['total'] > 0 else 0
    console.print(f"Success rate: {success_rate:.1f}%")
    console.print("\n=== Character Statistics ===")
    console.print(f"Total input characters: {stats['total_input_chars']}")
    console.print(f"Total output characters: {stats['total_output_chars']}")
    console.print(f"Total characters: {stats['total_output_chars']+stats['total_input_chars']}")
    avg_input = stats['total_input_chars'] / stats['total'] if stats['total'] > 0 else 0
    avg_output = stats['total_output_chars'] / stats['successful'] if stats['successful'] > 0 else 0
    console.print(f"Average characters per request: {avg_input:.1f} → {avg_output:.1f}")
    console.print(f"\nTotal test duration: {duration}")

def main():
    parser = argparse.ArgumentParser(
        description='Test the translation service with specific language options.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  List available languages:
    python test_translation.py --list-languages
    
  Test specific source language(s):
    python test_translation.py --source-languages Spanish French
    
  Test with custom server:
    python test_translation.py --source-languages Spanish --base-url http://your-server:8000
    """
    )
    
    parser.add_argument(
        '--list-languages',
        action='store_true',
        help='List all available languages and exit'
    )
    parser.add_argument(
        '--source-languages',
        nargs='+',
        help='Specify source languages to test (e.g., "Spanish French")'
    )
    parser.add_argument(
        '--base-url', 
        type=str, 
        default="http://localhost:8000",
        help='Base URL of the translation service (default: http://localhost:8000)'
    )
    
    args = parser.parse_args()

    if args.list_languages:
        list_available_languages()
        return

    try:
        test_translation_service(
            base_url=args.base_url,
            source_languages=args.source_languages
        )
    except KeyboardInterrupt:
        print("\nTest interrupted by user. Exiting...")
    except Exception as e:
        print(f"\nAn error occurred: {str(e)}")

if __name__ == "__main__":
    main()