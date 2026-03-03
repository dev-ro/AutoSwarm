
import os
import importlib
import pkgutil
import agno

package = agno
path = package.__path__[0]
found = []

for root, dirs, files in os.walk(path):
    for file in files:
        if file.endswith(".py"):
            filepath = os.path.join(root, file)
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                if "Gemini" in content or "LanceDb" in content or "AgentKnowledge" in content or "Knowledge" in content:
                    rel_path = os.path.relpath(filepath, path)
                    found.append(f"{rel_path}: Matches found")

for f in found:
    print(f)
