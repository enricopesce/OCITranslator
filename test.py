import requests
import argparse
from rich.console import Console
from rich.panel import Panel
import time
from datetime import datetime
import json

class TranslationTester:
    def __init__(self, base_url: str, verbose: bool = False):
        self.base_url = base_url.rstrip('/')
        self.verbose = verbose
        self.languages = [
            'ar', 'zh', 'en', 'fr', 'de', 
            'it', 'ja', 'ko', 'pt', 'es'
        ]
        self.language_names = {
            'ar': 'Arabic',
            'zh': 'Chinese',
            'en': 'English',
            'fr': 'French',
            'de': 'German',
            'it': 'Italian',
            'ja': 'Japanese',
            'ko': 'Korean',
            'pt': 'Portuguese',
            'es': 'Spanish'
        }
        self.sample_texts = {
            'en': [
                "Hello, how are you today?",
                "The weather is beautiful",
                "I love to travel"
            ],
            'es': [
                "¿Cómo estás hoy?",
                "El tiempo está hermoso",
                "Me encanta viajar"
            ],
            'fr': [
                "Comment allez-vous aujourd'hui?",
                "Le temps est magnifique",
                "J'aime voyager"
            ],
            'de': [
                "Wie geht es dir heute?",
                "Das Wetter ist schön",
                "Ich reise gerne"
            ],
            'it': [
                "Come stai oggi?",
                "Il tempo è bellissimo",
                "Amo viaggiare"
            ],
            'pt': [
                "Como você está hoje?",
                "O tempo está bonito",
                "Eu amo viajar"
            ],
            'zh': [
                "今天你好吗？",
                "天气很好",
                "我爱旅行"
            ],
            'ja': [
                "今日はお元気ですか？",
                "天気が良いですね",
                "旅行が大好きです"
            ],
            'ko': [
                "오늘 어떠신가요?",
                "날씨가 아름답습니다",
                "나는 여행을 좋아합니다"
            ],
            'ar': [
                "كيف حالك اليوم؟",
                "الطقس جميل",
                "أحب السفر"
            ]
        }
        self.console = Console()
        self.total_time = 0
        self.total_chars = 0
        self.total_translations = 0
        self.errors = 0

    def print_verbose(self, request_data: dict, response_data: dict = None, error: str = None):
        """Print verbose API request and response information."""
        if not self.verbose:
            return

        self.console.print("\n[bold yellow]API Request Details:[/bold yellow]")
        self.console.print(f"[cyan]Endpoint:[/cyan] {self.base_url}/translate")
        self.console.print("[cyan]Request Payload:[/cyan]")
        self.console.print(json.dumps(request_data, indent=2, ensure_ascii=False))

        if error:
            self.console.print(f"\n[bold red]Error:[/bold red] {error}")
        elif response_data:
            self.console.print("\n[bold green]API Response:[/bold green]")
            self.console.print(json.dumps(response_data, indent=2, ensure_ascii=False))
        
        self.console.print("\n" + "-" * 40)
        
    def translate(self, text: str, source_language: str, target_language: str) -> tuple:
        """Make a translation request to the API and measure time."""
        endpoint = f"{self.base_url}/translate"
        payload = {
            "text": text,
            "source_language": source_language,
            "target_language": target_language
        }
        
        start_time = time.time()
        try:
            response = requests.post(endpoint, json=payload)
            response.raise_for_status()
            end_time = time.time()
            response_data = response.json()
            
            # Print verbose information if enabled
            self.print_verbose(payload, response_data)
            
            return response_data, end_time - start_time, False
        except requests.exceptions.RequestException as e:
            self.errors += 1
            # Print verbose error information if enabled
            self.print_verbose(payload, error=str(e))
            return None, time.time() - start_time, True

    def print_translation_result(self, source_lang: str, target_lang: str, 
                               original: str, translation: str, time_taken: float, 
                               chars: int, is_error: bool):
        """Print individual translation result."""
        if is_error:
            self.console.print(f"\n[red]ERROR[/red] translating from "
                             f"[yellow]{self.language_names[source_lang]}[/yellow] to "
                             f"[cyan]{self.language_names[target_lang]}[/cyan]")
            return

        self.console.print(
            f"\n[bold blue]Translation #{self.total_translations + 1}[/bold blue]"
            f"\n[yellow]From[/yellow]: {self.language_names[source_lang]}"
            f"\n[cyan]To[/cyan]: {self.language_names[target_lang]}"
            f"\n[green]Original[/green]: {original}"
            f"\n[magenta]Translated[/magenta]: {translation}"
            f"\n[blue]Time[/blue]: {time_taken:.3f}s"
            f"\n[red]Characters[/red]: {chars}"
            f"\n{'-' * 80}"
        )

    def test_single_translation(self, text: str, source_lang: str, target_lang: str):
        """Test a single translation with specified languages."""
        self.console.print(Panel(
            f"Starting single translation test\n"
            f"API URL: [cyan]{self.base_url}[/cyan]\n"
            f"From: [yellow]{self.language_names[source_lang]}[/yellow]\n"
            f"To: [cyan]{self.language_names[target_lang]}[/cyan]\n"
            f"Text: [green]{text}[/green]\n"
            f"Timestamp: [cyan]{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}[/cyan]", 
            title="Translation Testing", 
            border_style="blue"))

        result, translation_time, is_error = self.translate(
            text, source_lang, target_lang
        )
        
        if not is_error:
            translated_text = result['translated_text']
            total_chars_current = len(text) + len(translated_text)
            self.total_chars += total_chars_current
            self.total_time += translation_time
            self.total_translations += 1
            
            self.print_translation_result(
                source_lang, target_lang, text, 
                translated_text, translation_time, 
                total_chars_current, is_error
            )

    def test_sample_translations(self):
        """Test translations using sample texts."""
        self.console.print(Panel(
            f"Starting sample translations\n"
            f"API URL: [cyan]{self.base_url}[/cyan]\n"
            f"Timestamp: [cyan]{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}[/cyan]", 
            title="Translation Testing", 
            border_style="blue"))

        for source_lang, texts in self.sample_texts.items():
            for test_text in texts:
                for target_lang in self.languages:
                    if target_lang != source_lang:
                        result, translation_time, is_error = self.translate(
                            test_text, source_lang, target_lang
                        )
                        
                        if not is_error:
                            translated_text = result['translated_text']
                            total_chars_current = len(test_text) + len(translated_text)
                            self.total_chars += total_chars_current
                            self.total_time += translation_time
                            self.total_translations += 1
                            
                            self.print_translation_result(
                                source_lang, target_lang, test_text, 
                                translated_text, translation_time, 
                                total_chars_current, is_error
                            )

    def print_summary(self):
        """Print summary of all translations."""
        self.console.print("\n" + "=" * 80)
        self.console.print("[bold blue]Translation Summary[/bold blue]")
        self.console.print(f"[green]Total translations[/green]: {self.total_translations}")
        self.console.print(f"[red]Failed translations[/red]: {self.errors}")
        self.console.print(f"[yellow]Total time[/yellow]: {self.total_time:.2f}s")
        if self.total_translations > 0:
            self.console.print(f"[magenta]Average time per translation[/magenta]: {self.total_time/self.total_translations:.3f}s")
            self.console.print(f"[cyan]Total characters processed[/cyan]: {self.total_chars}")
            self.console.print(f"[blue]Average characters per translation[/blue]: {self.total_chars/self.total_translations:.1f}")
        self.console.print("=" * 80)

def main():
    parser = argparse.ArgumentParser(description='Test translation API for all language combinations')
    parser.add_argument('--url', default='http://localhost:8000', 
                       help='Base URL of the translation API (default: http://localhost:8000)')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Enable verbose output showing API requests and responses')
    
    # Create a group for text-related arguments
    text_group = parser.add_argument_group('text translation arguments')
    text_group.add_argument('--text', help='Input text to translate')
    text_group.add_argument('--from', dest='from_lang',
                           help='Source language code (required if --text is used)',
                           choices=['ar', 'zh', 'en', 'fr', 'de', 'it', 'ja', 'ko', 'pt', 'es'])
    text_group.add_argument('--to', dest='to_lang',
                           help='Target language code (required if --text is used)',
                           choices=['ar', 'zh', 'en', 'fr', 'de', 'it', 'ja', 'ko', 'pt', 'es'])
    
    args = parser.parse_args()
    
    # Validate arguments
    if args.text and (not args.from_lang or not args.to_lang):
        parser.error("When using --text, both --from and --to language codes are required")
    
    if (args.from_lang or args.to_lang) and not args.text:
        parser.error("--from and --to can only be used when --text is provided")
    
    tester = TranslationTester(args.url, verbose=args.verbose)
    
    if args.text:
        # Single translation mode
        tester.test_single_translation(args.text, args.from_lang, args.to_lang)
    else:
        # Sample translations mode
        tester.test_sample_translations()
    
    tester.print_summary()

if __name__ == "__main__":
    main()