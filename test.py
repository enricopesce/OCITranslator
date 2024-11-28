import requests
from itertools import permutations
import argparse
from typing import List, Dict
import sys
from rich.console import Console
from rich.progress import track
from rich.table import Table
from rich.panel import Panel
from rich import box
import time
from rich.live import Live
from datetime import datetime

class TranslationTester:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip('/')
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
            return response.json(), end_time - start_time
        except requests.exceptions.RequestException as e:
            self.console.print(f"[red]Error making request: {str(e)}[/red]")
            sys.exit(1)

    def test_all_combinations(self):
        """Test translation between all language pairs with native sample texts."""
        results = []
        total_tests = sum(len(texts) * (len(self.languages) - 1) 
                         for texts in self.sample_texts.values())
        
        self.console.print(Panel(
            f"Starting translation tests\n"
            f"API URL: [cyan]{self.base_url}[/cyan]\n"
            f"Total translations to perform: [cyan]{total_tests}[/cyan]\n"
            f"Timestamp: [cyan]{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}[/cyan]", 
            title="Translation Testing", 
            border_style="blue"))

        total_time = 0
        total_chars = 0

        with Live(auto_refresh=False) as live:
            for source_lang, texts in self.sample_texts.items():
                live.update(f"[yellow]Processing source language: {self.language_names[source_lang]}[/yellow]")
                live.refresh()
                
                for test_text in texts:
                    for target_lang in self.languages:
                        if target_lang != source_lang:
                            result, translation_time = self.translate(test_text, source_lang, target_lang)
                            translated_text = result['translated_text']
                            
                            total_chars_current = len(test_text) + len(translated_text)
                            total_chars += total_chars_current
                            total_time += translation_time
                            
                            results.append({
                                'source_language': source_lang,
                                'target_language': target_lang,
                                'original_text': test_text,
                                'translated_text': translated_text,
                                'translation_time': translation_time,
                                'total_chars': total_chars_current
                            })
                            
                            live.update(
                                f"[yellow]{self.language_names[source_lang]}[/yellow] → "
                                f"[cyan]{self.language_names[target_lang]}[/cyan]\n"
                                f"Time: [green]{translation_time:.3f}s[/green] | "
                                f"Chars: [blue]{total_chars_current}[/blue]"
                            )
                            live.refresh()
        
        self.console.print(f"\n[bold green]Testing completed![/bold green]")
        self.console.print(f"Total time: [yellow]{total_time:.2f}s[/yellow]")
        self.console.print(f"Total characters: [blue]{total_chars}[/blue]")
        self.console.print(f"Average time per translation: [green]{total_time/len(results):.3f}s[/green]")
        
        return results

    def display_results(self, results: List[Dict]):
        """Display results in a formatted table."""
        table = Table(show_header=True, 
                     header_style="bold magenta",
                     box=box.ROUNDED,
                     title="Translation Results",
                     title_style="bold blue")
        
        table.add_column("From", style="yellow", width=12)
        table.add_column("To", style="cyan", width=12)
        table.add_column("Original Text", style="green", width=30)
        table.add_column("Translated Text", style="blue", width=30)
        table.add_column("Time (s)", style="magenta", width=10)
        table.add_column("Chars", style="red", width=10)
        
        for result in results:
            table.add_row(
                self.language_names[result['source_language']],
                self.language_names[result['target_language']],
                result['original_text'],
                result['translated_text'],
                f"{result['translation_time']:.3f}",
                str(result['total_chars'])
            )
        
        self.console.print(table)

def main():
    parser = argparse.ArgumentParser(description='Test translation API for all language combinations')
    parser.add_argument('--url', default='http://localhost:8000', 
                       help='Base URL of the translation API (default: http://localhost:8000)')
    
    args = parser.parse_args()
    
    tester = TranslationTester(args.url)
    results = tester.test_all_combinations()
    
    # Display results in rich formatted table
    tester.display_results(results)

if __name__ == "__main__":
    main()