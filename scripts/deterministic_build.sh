#!/bin/bash
# QFS V13 Deterministic Build Script

echo "Building QFS V13 in deterministic environment..."

# Create build directory
mkdir -p build

# Copy source files
cp -r src build/
cp -r tests build/
cp requirements.txt build/
cp requirements-dev.txt build/

# Create deterministic build hash
find build/ -type f -exec sha256sum {} \; | sort -k2 > build/BUILD_MANIFEST.txt
sha256sum build/BUILD_MANIFEST.txt > build/BUILD_HASH.txt

echo "Deterministic build completed!"
echo "Build hash: $(cat build/BUILD_HASH.txt)"