#!/bin/bash
set -euo pipefail
TARGET="/Users/mohamedali/Library/CloudStorage/OneDrive-LeedsBeckettUniversity/Work/GITHUB REPO/INQETRA"
SOURCE="$(cd "$(dirname "$0")/.." && pwd)"
mkdir -p "$TARGET"
rsync -av --exclude '.DS_Store' "$SOURCE/" "$TARGET/"
echo "INQETRA build pack copied to: $TARGET"
