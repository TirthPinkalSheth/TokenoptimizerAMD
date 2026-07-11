#!/bin/bash
ollama serve &
sleep 5
echo "Warming up model..."
curl -s http://localhost:11434/api/generate -d '{"model": "qwen2.5:3b", "prompt": "Hi", "stream": false}' > /dev/null
echo "Model warmed up, starting agent..."
python3 /app/src/main.py