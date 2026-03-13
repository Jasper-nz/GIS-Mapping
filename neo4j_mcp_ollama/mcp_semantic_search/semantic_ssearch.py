"""
Ollama Web Search - A sophisticated web search assistant
Powered by Ollama and SearxNG for intelligent information retrieval
"""

import re
import ollama
import requests
import json
import time
import sys
import os
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from urllib.parse import urlparse
import argparse
import urllib.parse

# Configuration
def load_config():
    """Load configuration from file with fallback to defaults"""
    default_config = {
        'model': 'llama3',
        'searxng_instances': [
            'https://html.duckduckgo.com/html/',
            'https://google.com/search',
        ],
        'max_results': 8,
        'timeout': 10,
        'max_retries': 3,
        'history_file': 'search_history.json',
        'enable_colors': True,
        'streaming_delay': 0.02
    }
    
    try:
        if os.path.exists('config.json'):
            with open('config.json', 'r') as f:
                user_config = json.load(f)
                default_config.update(user_config)
    except Exception as e:
        print(f"Warning: Could not load config.json, using defaults: {e}")
    
    return default_config

# Load the Global config from config.json
CONFIG = load_config()

class ExtractEngine:

    regex_description = ""
    regex_url = ""
    regex_title = ""
    regex_page = ""

    GOOGLE = 'google'
    BING = 'bing'
    DUCKDUCKGO = 'duckduckgo'

    description = ""
    url = ""
    title = ""

    def __init__(self):
        pass

    def get_engine_name(self, engine: str) -> str:
        engine_map = {
            self.GOOGLE: "Google",
            self.BING: "Bing",
            self.DUCKDUCKGO: "DuckDuckGo",
        }
        return engine_map.get(engine.lower(), "Unknown")
    
    def extract_title_url_description(self, data: str) -> Tuple[str, str, str]:
        
        raise Exception("Not implemented yet")
    

class DuckDuckGoExtractEngine(ExtractEngine):
    def __init__(self):
        super().__init__()

        self.regex_description = re.compile(r'<a class="result__snippet" href=".*?">(.*?)</a>', re.IGNORECASE)
        self.regex_url = re.compile(r'<a rel="nofollow" class="result__a" href="//duckduckgo.com/l/\?uddg=(.*?)">.*?...</a>', re.IGNORECASE)
        self.regex_title = re.compile(r'<a rel="nofollow" class="result__a" href="//duckduckgo.com/l/\?uddg=.*?">(.*?)...</a>', re.IGNORECASE)
        self.regex_page = re.compile(r'<[^>]+>')

    def extract_title_url_description(self, data: str) -> Tuple[str, str, str]:

        descriptions = self.regex_description.findall(data)
        urls = self.regex_url.findall(data)
        titles = self.regex_title.findall(data)
        for i in range(len(descriptions)):
                desc = descriptions[i]
                title = titles[i]
                url = urllib.parse.unquote(urls[i])
                if len(contents) >0:
                    contents += ", "
                contents += f"{{ \"title\": \"{title}\", \"url\": \"{url}\", \"description\": \"{desc}\" }}"
            
        return json.loads(f"{{\"results\": [{contents}]}}") 

class BingExtractEngine(ExtractEngine):
    def __init__(self):
        super().__init__()

    def extract_title_url_description(self, data: str) -> Tuple[str, str, str]:
        # Implement Bing extraction logic here
        return "", "", ""

class GoogleExtractEngine(ExtractEngine):
    def __init__(self):
        super().__init__()

    def extract_title_url_description(self, data: str) -> Tuple[str, str, str]:
        # Implement Google extraction logic here
        return "", "", ""  


class WebSearchAssistant:
    def __init__(self):
        self.search_history = self.load_history()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })
        
    def print_banner(self):
        """Display a beautiful welcome banner"""
        banner = f"""
✨ Features:
• 🧠 AI-powered query optimization
• 🌐 Multiple search engine fallbacks  
• 📄 Smart content extraction
• 💾 Search history tracking
• 🎨 Beautiful terminal interface

"""
        print(banner)

    def model_response(self, model: str, message: str, max_retries: int = 3) -> Optional[str]:
        """Get response from Ollama model with error handling"""
        for attempt in range(max_retries):
            try:
                response = ollama.chat(model=model, messages=[{
                    'role': 'user',
                    'content': message,
                }])
                return response['message']['content']
            except Exception as e:
                print(f"⚠️  Attempt {attempt + 1} failed: {str(e)}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                else:
                    print(f"❌ Failed to get model response after {max_retries} attempts")
                    return None

    def streaming_model_response(self, model: str, message: str) -> str:
        """Stream model response with typing effect"""
        response = ""
        try:
            print(f"🤖 Assistant:", end=" ")
            for chunk in ollama.chat(model=model, messages=[{
                'role': 'user',
                'content': message,
            }], stream=True):
                content = chunk['message']['content']
                print(content, end='', flush=True)
                response += content
                time.sleep(CONFIG.get('streaming_delay', 0.02))  # Slight delay for better reading experience
            print()  # New line after streaming
            return response
        except Exception as e:
            print(f"\n❌ Error during streaming: {str(e)}")
            return ""

    def retrieve_page_information(self, url: str) -> Optional[str]:
        """Retrieve and clean webpage content using Jina Reader API"""
        try:
            print(f"📄 Extracting content from webpage...")
            
            # Clean URL
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
                
            base_url = "https://r.jina.ai/"
            response = self.session.get(
                base_url + url, 
                timeout=CONFIG['timeout'],
                headers={'Accept': 'text/plain'}
            )
            response.raise_for_status()
            
            content = response.text.strip()
            if len(content) > 10000:  # Limit content size
                content = content[:10000] + "\n... (content truncated)"
                
            return content
            
        except Exception as e:
            print(f"❌ Failed to retrieve page content: {str(e)}")
            return None

    def browser_retriev_content_page(self, url: str, data: str) ->Optional[List[Dict]]:
        """Retrieve webpage content using a headless browser (Selenium)"""

        
        try:
            print(f"📄 Extracting content from webpage using headless browser...")
            
            regex_description = re.compile(r'<a class="result__snippet" href=".*?">(.*?)</a>', re.IGNORECASE)
            regex_url = re.compile(r'<a rel="nofollow" class="result__a" href="//duckduckgo.com/l/\?uddg=(.*?)">.*?...</a>', re.IGNORECASE)
            regex_title = re.compile(r'<a rel="nofollow" class="result__a" href="//duckduckgo.com/l/\?uddg=.*?">(.*?)...</a>', re.IGNORECASE)
            regex_page = re.compile(r'<[^>]+>')
   
            contents = ""
            descriptions = regex_description.findall(data)
            urls = regex_url.findall(data)
            titles = regex_title.findall(data)

            for i in range(len(descriptions)):
                desc = descriptions[i]
                title = titles[i]
                url = urllib.parse.unquote(urls[i])
                if len(contents) >0:
                    contents += ", "
                contents += f"{{ \"title\": \"{title}\", \"url\": \"{url}\", \"description\": \"{desc}\" }}"
            
            return json.loads(f"{{\"results\": [{contents}]}}")
            
        except Exception as e:
            print(f"❌ Failed to retrieve page content with browser: {str(e)}")
            return None
        

    def browse_web(self, query: str) -> Optional[List[Dict]]:
        """Search the web using multiple SearxNG instances with fallback"""
        
        print(f"🔍 Searching the web for: {query}")
        
        for instance in CONFIG['searxng_instances']:
            try:
                query = requests.utils.quote(query)
                search_url = f"{instance}?q={query}&format=json&categories=general"

                print(f"🌐 Trying search instance: {instance} and url -> {search_url} ")
                
                response = self.session.get(search_url, timeout=CONFIG['timeout'])
                response.raise_for_status()
                #print(f"✅ Search instance responded successfully- {response.raise_for_status()} ")
                #print(f"🌐 response text: {response.text}")
                data = self.browser_retriev_content_page( url=search_url, data=response.text)
                #print(data)
                results = data.get('results', [])
                
                if results:
                    print(f"✅ Found {len(results)} results")
                    return results[:CONFIG['max_results']]
                    
            except Exception as e:
                print(f"⚠️  Search instance failed, trying next...")
                continue
                
        print(f"❌ All search instances failed")
        return None

    def save_search_to_history(self, query: str, question: str, result: Dict):
        """Save search to history"""
        entry = {
            'timestamp': datetime.now().isoformat(),
            'question': question,
            'query': query,
            'result': result
        }
        
        self.search_history.append(entry)
        
        # Keep only last 50 searches
        if len(self.search_history) > 50:
            self.search_history = self.search_history[-50:]
            
        try:
            with open(CONFIG['history_file'], 'w') as f:
                json.dump(self.search_history, f, indent=2)
        except Exception as e:
            print(f"⚠️  Could not save history: {e}")

    def load_history(self) -> List[Dict]:
        """Load search history"""
        try:
            if os.path.exists(CONFIG['history_file']):
                with open(CONFIG['history_file'], 'r') as f:
                    return json.load(f)
        except Exception:
            pass
        return []

    def show_history(self):
        """Display recent search history"""
        if not self.search_history:
            print(f"📝 No search history found")
            return
            
        print(f"\n📚 Recent Search History:")
        print("═" * 60)
        
        for i, entry in enumerate(self.search_history[-10:], 1):  # Show last 10
            timestamp = datetime.fromisoformat(entry['timestamp']).strftime('%m/%d %H:%M')
            print(f"{i:2d}. [{timestamp}] {entry['question'][:50]}...")

    def generate_search_query(self, question: str) -> Optional[str]:
        """Generate optimized search query from user question"""
        prompt = """You are an expert at creating precise web search queries. Convert the user's question into an optimal search query that will find the most relevant results.

Guidelines:
- Use specific keywords and terms
- Remove unnecessary words like "what", "how", "can you"
- Include important context
- Keep it concise but comprehensive
- Avoid overly broad terms
- keep it under 10 words
- Do not include quotation marks or special characters
- Do not include any explanation, only provide the search query

Examples:
Question: "What is the capital of France?"
Query: capital France

Question: "How do I install Docker on Ubuntu?"
Query: install Docker Ubuntu tutorial

Question: "What are the latest developments in AI?"
Query: latest AI developments 2024

User's question: """ + question

        print(f"🧠 Optimizing search query...")
        return self.model_response(CONFIG['model'], prompt)

    def select_best_result(self, question: str, query: str, results: List[Dict]) -> Optional[Tuple[str, str]]:
        """Let AI select the most relevant search result"""
        results_text = "\n".join([
            f"{i+1}. {result.get('title', 'No title')} - {result.get('url', 'No URL')}\n   {result.get('content', 'No description')[:200]}..."
            for i, result in enumerate(results)
        ])
        
        prompt = f"""You are an expert at evaluating search results. Based on the original question, select the MOST RELEVANT result.

Original Question: {question}
Search Query: {query}

Search Results:
{results_text}

Respond with ONLY the title and URL in this exact format:
Title: [exact title from results]
URL: [exact URL from results]
"holder_name": [the company name from results],
"address": [the company address from results],
"phone": [the company phone number from results],
"email": [the company email from results],
"website": [the company website from results],
"nzbn": [NZBN number from the result if "N/A" not found any things]
"""

        print(f"🎯 AI is selecting the best result...")
        response = self.model_response(CONFIG['model'], prompt)
        
        if not response:
            return None
            
        try:
            lines = [line.strip() for line in response.strip().split('\n') if line.strip()]
            title = next((line.split(':', 1)[1].strip() for line in lines if line.startswith('Title:')), None)
            url = next((line.split(':', 1)[1].strip() for line in lines if line.startswith('URL:')), None)
            
            if title and url:
                return title, url
        except Exception as e:
            print(f"⚠️  Error parsing result selection: {e}")
            
        # Fallback to first result
        if results:
            return results[0].get('title', 'Unknown'), results[0].get('url', '')
        return None

    def generate_final_answer(self, question: str, query: str, title: str, content: str) -> str:
        """Generate comprehensive answer based on retrieved content"""
        prompt = f"""You are a knowledgeable assistant providing accurate information based on web content.

Original Question: {question}
Search Query: {query}
Source: {title}

Retrieved Content:
{content}

Instructions:
- Provide a comprehensive but concise answer to the user's question
- Use information from the retrieved content
- Cite specific details when relevant
- If the content doesn't fully answer the question, mention what information is available
- Format your response clearly with bullet points or sections when appropriate
- Be helpful and informative

Return results strictly in the following JSON format:
{{
"holder_name": [the company name from results],
"address": [the company address from results],
"phone": [the company phone number from results],
"email": [the company email from results],
"website": [the company website from results],
"nzbn": [NZBN number from the result if "N/A" not found any things]
}}

"""

        print(f"\n{'='*60}")
        result = self.streaming_model_response(CONFIG['model'], prompt)
        print(f"{'='*60}")
        return result

    def interactive_search(self):
        """Main interactive search function"""
        while True:
            try:
                print(f"\n💭 What would you like to know?")
                print(f"(Type 'history' to see recent searches, 'config' to see settings, 'quit' to exit)")
                
                question = input(f"❓ Your question: ").strip()
                
                if not question:
                    continue
                    
                if question.lower() in ['quit', 'exit', 'q']:
                    print(f"👋 Thank you for using Ollama Web Search!")
                    break
                    
                if question.lower() == 'history':
                    self.show_history()
                    continue
                    
                if question.lower() == 'config':
                    self.show_config()
                    continue
                
                if question.lower() == 'config':
                    self.show_config()
                    continue
                
                # Generate optimized search query
                search_query = self.generate_search_query(question)
                if not search_query:
                    print(f"❌ Failed to generate search query")
                    continue
                
                print(f"🔍 Search Query: {search_query}")
                
                # Search the web
                results = self.browse_web(search_query)
                if not results:
                    print(f"❌ No search results found")
                    continue
                
                # Select best result
                result = self.select_best_result(question, search_query, results)
                if not result:
                    print(f"❌ Could not select a result")
                    continue
                    
                title, url = result
                print(f"\n📌 Selected: {title}")
                print(f"🔗 URL: {url}")
                
                # Retrieve page content
                content = self.retrieve_page_information(url)
                if not content:
                    print(f"❌ Could not retrieve page content")
                    continue
                
                # Save to history
                self.save_search_to_history(search_query, question, {
                    'title': title, 
                    'url': url
                })
                
                # Generate final answer
                self.generate_final_answer(question, search_query, title, content)
                
            except KeyboardInterrupt:
                print(f"\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Unexpected error: {str(e)}")

    def show_config(self):
        """Display current configuration settings"""
        print(f"\n⚙️  Current Configuration:")
        print("═" * 50)
        print(f"Model: {CONFIG['model']}")
        print(f"Max Results: {CONFIG['max_results']}")
        print(f"Timeout: {CONFIG['timeout']}s")
        print(f"Search Engines: {len(CONFIG['searxng_instances'])} instances")
        print(f"History File: {CONFIG['history_file']}")
        print(f"Colors Enabled: {CONFIG['enable_colors']}")
        print("═" * 50)


def main():
    """Main function with command line argument support"""
    parser = argparse.ArgumentParser(description='Ollama Web Search Assistant')
    parser.add_argument('--model', default=CONFIG['model'], help=f'Ollama model to use (default: {CONFIG["model"]})')
    parser.add_argument('--query', help='Direct query instead of interactive mode (e.g., --query "What is Python?")')
    parser.add_argument('--history', action='store_true', help='Show search history and exit')
    parser.add_argument('--config', action='store_true', help='Show current configuration and exit')
    
    args = parser.parse_args()
    
    # Update config with command line arguments if explicitly provided
    if args.model != CONFIG['model']:  # Only update if user explicitly provided a different model
        CONFIG['model'] = args.model
    
    assistant = WebSearchAssistant()
    
    if args.history:
        assistant.show_history()
        return
        
    if args.config:
        assistant.show_config()
        return
    
    assistant.print_banner()
    
    # Check if Ollama is available
    try:
        ollama.list()
        print(f"✅ Ollama connection successful")
        print(f"🤖 Using model: {CONFIG['model']}")
    except Exception as e:
        print(f"❌ Cannot connect to Ollama: {e}")
        print(f"💡 Make sure Ollama is running: ollama serve")
        return
    
    if args.query:
        # Single query mode
        print(f"🔍 Single query mode: {args.query}")
        try:
            # Generate optimized search query
            search_query = assistant.generate_search_query(args.query)
            if not search_query:
                print(f"❌ Failed to generate search query")
                return
            
            print(f"🔍 Search Query: {search_query}")
            
            # Search the web
            results = assistant.browse_web(search_query)
            if not results:
                print(f"❌ No search results found")
                return
            
            # Select best result
            result = assistant.select_best_result(args.query, search_query, results)
            if not result:
                print(f"❌ Could not select a result")
                return
                
            title, url = result
            print(f"\n📌 Selected: {title}")
            print(f"🔗 URL: {url}")
            
            # Retrieve page content
            content = assistant.retrieve_page_information(url)
            if not content:
                print(f"❌ Could not retrieve page content")
                return
            
            # Save to history
            assistant.save_search_to_history(search_query, args.query, {
                'title': title, 
                'url': url
            })
            
            # Generate final answer
            assistant.generate_final_answer(args.query, search_query, title, content)
            
        except Exception as e:
            print(f"❌ Error in single query mode: {str(e)}")
    else:
        # Interactive mode
        assistant.interactive_search()

if __name__ == "__main__":
    main()
