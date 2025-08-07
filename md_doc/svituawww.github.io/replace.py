import json
import os

def replace_in_file(file_path, replacements):
    with open(file_path, 'r') as file:
        content = file.read()
    
    for replacement in replacements:
        content = content.replace(replacement['find'], replacement['replace'])
        
    with open(file_path, 'w') as file:
        file.write(content)

def main():
    with open('config.json', 'r') as f:
        replacements = json.load(f)

    for root, _, files in os.walk('.'):
        for file in files:
            if file.endswith('.html'):
                file_path = os.path.join(root, file)
                replace_in_file(file_path, replacements)

if __name__ == "__main__":
    main()
