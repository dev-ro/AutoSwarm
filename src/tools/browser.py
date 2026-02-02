
from agno.tools import Toolkit
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

class BrowserTools(Toolkit):
    def __init__(self):
        super().__init__(name="browser_tools")
        self.register(self.search_web)
        self.register(self.read_page)

    def search_web(self, query: str) -> str:
        """
        Searches the web for the given query using a headless browser (DuckDuckGo).
        Returns the top results as a summary string.
        """
        print(f"  [BrowserTool] Searching for: {query}")
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            try:
                # navigating to duckduckgo
                page.goto(f"https://duckduckgo.com/?q={query}&t=h_&ia=web")
                page.wait_for_selector(".result__body", timeout=5000)
                
                # extracting results (titles and snippets)
                results = []
                elements = page.query_selector_all(".result__body")
                for i, el in enumerate(elements[:5]): # Top 5 results
                    title_el = el.query_selector(".result__title")
                    snippet_el = el.query_selector(".result__snippet")
                    
                    if title_el and snippet_el:
                        title = title_el.inner_text()
                        snippet = snippet_el.inner_text()
                        link = el.query_selector("a.result__a").get_attribute("href")
                        results.append(f"{i+1}. {title}\n   Snippet: {snippet}\n   Link: {link}\n")
                
                if not results:
                    return "No results found or page structure changed."
                
                return "\n".join(results)
            except Exception as e:
                return f"Error searching web: {e}"
            finally:
                browser.close()

    def read_page(self, url: str) -> str:
        """
        Visted a URL and extracts the main text content.
        Useful for reading articles or documentation found via search.
        """
        print(f"  [BrowserTool] Reading page: {url}")
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            try:
                page.goto(url, timeout=10000)
                # Just get the body text
                content = page.content()
                soup = BeautifulSoup(content, 'html.parser')
                
                # Remove scripts and styles
                for script in soup(["script", "style"]):
                    script.decompose()
                
                text = soup.get_text()
                
                # Basic cleaning - IMPROVED
                # Filter out short lines (likely navigation items) and massive blocks of whitespace
                lines = (line.strip() for line in text.splitlines())
                # Keep lines that look like actual content (more than 30 chars or ends with punctuation)
                meaningful_lines = [line for line in lines if len(line) > 30 or line.endswith(('.', '!', '?'))]
                text = '\n'.join(meaningful_lines)
                
                # Smart Truncation
                if len(text) > 8000:
                    text = f"--- Page Summary (Truncated) ---\n{text[:8000]}\n...(more content)..."
                    
                return text
            except Exception as e:
                return f"Error reading page: {e}"
            finally:
                browser.close()
