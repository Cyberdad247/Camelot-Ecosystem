import os

REPLACEMENT_MAP = {
    "chimera-os": "Camelot-OS"
}

IGNORE_DIRS = {
    ".git", ".hg", ".svn", "venv", "node_modules", "target", "__pycache__", ".vscode", ".idea", "dist", "build"
}

IGNORE_EXTENSIONS = {
    ".exe", ".dll", ".so", ".dylib", ".rlib", ".rmeta", ".obj", ".o", ".a", ".lib", ".pyc", ".pyd", ".png", ".jpg", ".jpeg", ".gif", ".ico", ".webp", ".svg", ".zip", ".tar", ".gz", ".7z", ".rar", ".pdf", ".docx", ".xlsx", ".pptx", ".mp3", ".mp4", ".wav", ".avi", ".mov", ".mkv", ".db", ".sqlite", ".sqlite3"
}

def is_text_file(filepath):
    # Simple heuristic: try reading first 1024 bytes as utf-8
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            f.read(1024)
        return True
    except UnicodeDecodeError:
        return False

def process_file(filepath):
    try:
        if not is_text_file(filepath):
            return False

        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        new_content = content
        for old, new in REPLACEMENT_MAP.items():
            new_content = new_content.replace(old, new)

        if new_content != content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"Updated: {filepath}")
            return True
    except Exception as e:
        print(f"Error processing {filepath}: {e}")
    return False

def main():
    root_dir = os.getcwd()
    count = 0
    for dirpath, dirnames, filenames in os.walk(root_dir):
        # Modify dirnames in-place to skip ignored directories
        dirnames[:] = [d for d in dirnames if d not in IGNORE_DIRS]

        for filename in filenames:
            ext = os.path.splitext(filename)[1].lower()
            if ext in IGNORE_EXTENSIONS:
                continue

            filepath = os.path.join(dirpath, filename)
            # Skip the script itself
            if filepath == os.path.abspath(__file__):
                continue
            
            if process_file(filepath):
                count += 1
    
    print(f"Total files updated: {count}")

if __name__ == "__main__":
    main()
