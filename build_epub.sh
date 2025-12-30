#!/bin/bash

# Build Wyckoff Notes EPUB
# This script compiles all markdown notes into a single EPUB file

echo "Building Wyckoff_Notes.epub..."

pandoc \
  --resource-path=wyckoff_content \
  --split-level=1 \
  --css=epub.css \
  -o Wyckoff_Notes.epub \
  metadata.yaml \
  $(cat files.txt)

if [ $? -eq 0 ]; then
  echo "✅ EPUB created successfully: Wyckoff_Notes.epub"
  ls -lh Wyckoff_Notes.epub
else
  echo "❌ EPUB build failed"
  exit 1
fi
