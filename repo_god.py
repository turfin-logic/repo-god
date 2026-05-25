import os
import sys
import fnmatch
from google import genai
from dotenv import load_dotenv

load_dotenv()

# Strict filters to avoid security risks
IGNORE_DIRS = {'.git', 'node_modules', 'venv', '__pycache__', 'dist', 'build', '.idea', '.vscode'}
IGNORE_FILES = {'.env', '*.log', '*.sqlite', '*.db', '*.pyc', '*.pdf', '*.png', '*.jpg'}

def should_ignore(path, is_dir=False):
    basename = os.path.basename(path)
    if is_dir:
        return basename in IGNORE_DIRS
    for pattern in IGNORE_FILES:
        if fnmatch.fnmatch(basename, pattern):
            return True
    return False

def build_repo_context(root_dir):
    tree_str = "Project Structure:\n"
    code_content = "\n\nFiles Content:\n"
    
    for dirpath, dirnames, filenames in os.walk(root_dir):
        # Mutate dirnames in-place to skip ignored directories
        dirnames[:] = [d for d in dirnames if not should_ignore(os.path.join(dirpath, d), is_dir=True)]
        
        rel_dir = os.path.relpath(dirpath, root_dir)
        if rel_dir == '.':
            rel_dir = ''
        
        for f in filenames:
            if should_ignore(f):
                continue
            
            filepath = os.path.join(dirpath, f)
            rel_file = os.path.join(rel_dir, f)
            tree_str += f"- {rel_file}\n"
            
            try:
                with open(filepath, 'r', encoding='utf-8') as file:
                    content = file.read()
                    code_content += f"\n--- BEGIN {rel_file} ---\n"
                    code_content += content
                    code_content += f"\n--- END {rel_file} ---\n"
            except Exception as e:
                code_content += f"\n--- SKIPPED {rel_file} (Binary or Unreadable) ---\n"

    return tree_str + code_content

def main():
    if len(sys.argv) < 3:
        print("Usage: python repo_god.py <path_to_directory> \"<your prompt>\"")
        sys.exit(1)
        
    target_dir = sys.argv[1]
    prompt = sys.argv[2]
    
    if not os.path.isdir(target_dir):
        print(f"Error: Directory '{target_dir}' not found.")
        sys.exit(1)
        
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("Error: GEMINI_API_KEY not found in environment variables.")
        sys.exit(1)
        
    print("Scraping repository context (ignoring .env and binaries)...")
    repo_context = build_repo_context(target_dir)
    
    # We use 1M Token model for huge context (hypothetical future-proof model)
    # Falling back to 2.5-pro which handles up to 2M tokens
    client = genai.Client(api_key=api_key)
    
    full_prompt = (
        "You are Repo-God, an expert software architect analyzing an entire codebase.\n"
        f"USER REQUEST: {prompt}\n\n"
        f"CODEBASE CONTEXT:\n{repo_context}"
    )
    
    print("\nSending massive payload to Gemini API. This may consume huge quota...")
    try:
        response = client.models.generate_content(
            model="gemini-2.5-pro",
            contents=full_prompt
        )
        print("\n--- REPO-GOD ANALYSIS ---\n")
        print(response.text)
    except Exception as e:
        print(f"\nAPI Error: {e}")

if __name__ == "__main__":
    main()
