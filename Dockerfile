FROM ubuntu:22.04

RUN apt-get update && apt-get install -y \
    python3 \
    curl \
    zstd \
    && rm -rf /var/lib/apt/lists/*

RUN curl -fsSL https://ollama.com/install.sh | sh

RUN ollama serve & sleep 5 && ollama pull qwen2.5:3b
WORKDIR /app
COPY src/ /app/src/
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh
CMD ["/app/entrypoint.sh"]