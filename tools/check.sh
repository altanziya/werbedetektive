#!/bin/sh
# Vor jedem Push: Service Worker und Seitenskript müssen gültiges JavaScript sein.
# Ein Syntaxfehler in sw.js lässt Geräte unbemerkt auf dem alten Stand hängen.
set -e
cd "$(dirname "$0")/.."
node --check sw.js
tmp=$(mktemp -t wd-check).js
python3 -c "import re,sys;print(re.search(r'<script>(.*)</script>',open('index.html').read(),re.S).group(1))" > "$tmp"
node --check "$tmp" && rm -f "$tmp"
echo "check ok"
