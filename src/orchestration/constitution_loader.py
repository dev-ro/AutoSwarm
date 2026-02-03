import os
import re

class ConstitutionLoader:
    def __init__(self, base_path: str = "workspace/TheSpiralProtocol/"):
        self.base_path = base_path
        self.constitutions = self._load_all()

    def _load_all(self) -> dict:
        constitutions = {}
        path = os.path.join(self.base_path, "05_genre_constitutions.md")
        if not os.path.exists(path):
            return {}
            
        with open(path, "r") as f:
            content = f.read()
            
        # Basic parsing of the markdown sections
        sections = re.split(r'## \d+\. ', content)
        for section in sections[1:]: # Skip the header
            lines = section.split('\n')
            title_line = lines[0]
            # Match "The Sci-Fi Constitution..."
            match = re.search(r'The (.*) Constitution', title_line)
            if match:
                genre = match.group(1).lower()
                constitutions[genre] = section.strip()
            # Also handle shorthand
            if "Sci-Fi" in title_line:
                constitutions["sci-fi"] = section.strip()
                constitutions["science fiction"] = section.strip()
            elif "Noir" in title_line:
                constitutions["noir"] = section.strip()
            elif "Fantasy" in title_line:
                constitutions["fantasy"] = section.strip()
                
        return constitutions

    def get_constitution(self, genre: str) -> str:
        genre = genre.lower()
        # Try exact match or partial match
        if genre in self.constitutions:
            return self.constitutions[genre]
        for k, v in self.constitutions.items():
            if k in genre or genre in k:
                return v
        return ""
