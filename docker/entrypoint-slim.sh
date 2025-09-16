#!/bin/bash
echo "🧠 MetaMark Slim: Using external Ollama at $OLLAMA_URL"
python3 cli.py --verbose "$@"
