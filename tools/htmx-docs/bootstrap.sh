#!/usr/bin/env bash
# Bootstraps the HTMX Documentation Site on Unix/Linux/macOS edge targets

set -e

echo -e "\033[1;36m=======================================================\033[0m"
echo -e "\033[1;36m  CAMELOT WORLD_TREE: HTMX DOCS BOOTSTRAP SEQUENCE     \033[0m"
echo -e "\033[1;36m=======================================================\033[0m"
echo ""

# 1. Check Dependencies
echo -e "\033[1;35m[*] Verifying Go toolchain...\033[0m"
if ! command -v go &> /dev/null; then
    echo -e "\033[1;31mFATAL: Go is not installed. Please install Go 1.21+.\033[0m"
    exit 1
fi
go version

# 2. Sync Modules
echo -e "\033[1;35m[*] Synchronizing Go modules...\033[0m"
go mod tidy

# 3. Verify Asset Directories
echo -e "\033[1;35m[*] Verifying go:embed virtual filesystem assets...\033[0m"
for dir in docs static templates; do
    if [ ! -d "$dir" ]; then
        echo -e "\033[1;33m    [-] Missing directory: $dir. Forging...\033[0m"
        mkdir -p "$dir"
    else
        echo -e "\033[1;32m    [+] Directory attached: $dir/\033[0m"
    fi
done

# 4. Run Validation Suite
echo -e "\033[1;35m[*] Executing Gideon Verdict Validation Suite (N110)...\033[0m"
go test ./...
echo -e "\033[1;32m    [+] Validation Matrix Passed.\033[0m"

# 5. Build Bare-Metal Server
echo -e "\033[1;35m[*] Forging bare-metal executable (server)...\033[0m"
go build -o server ./cmd/server
echo -e "\033[1;32m    [+] Executable compiled successfully.\033[0m"
echo ""

# 6. Launch
echo -e "\033[1;36m=======================================================\033[0m"
echo -e "\033[1;36m  BOOTSTRAP COMPLETE. LAUNCHING NEURAL LINK...         \033[0m"
echo -e "\033[1;36m=======================================================\033[0m"
./server
