import sys
import ruamel.yaml

for file in sys.argv[1:]:
    with open(file, 'r') as f:
        print(f"Loading {file}")
