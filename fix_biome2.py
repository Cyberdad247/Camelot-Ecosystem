import subprocess
import sys

def parse_failures(output):
    files_to_fix = set()
    for line in output.split('\n'):
        if line.startswith('./') and 'format' in line:
            files_to_fix.add(line.split(' ')[0][2:])
    return list(files_to_fix)

result = subprocess.run(["npx", "biome", "check", "."], capture_output=True, text=True)
files = parse_failures(result.stdout + result.stderr)

print(f"Found {len(files)} files to format.")
chunk_size = 50
for i in range(0, len(files), chunk_size):
    chunk = files[i:i+chunk_size]
    print(f"Formatting chunk {i//chunk_size + 1}...")
    subprocess.run(["npx", "biome", "format", "--write"] + chunk)
