# mitmproxy-llm-adapter

A mitmproxy-based adapter that redirects OpenAI API calls to local LLM services with model name translation

## Installation

### Install mitmproxy
```bash
# Using pip
pip install mitmproxy

# Using conda
conda install -c conda-forge mitmproxy

# Using brew (macOS)
brew install mitmproxy
```

### Install Ollama (for local LLM backend)
```bash
# macOS
brew install ollama

# Linux
curl -fsSL https://ollama.com/install.sh | sh

# Windows
# Download from https://ollama.com/download
```

### Start Ollama service
```bash
# Start Ollama (runs on http://127.0.0.1:11434 by default)
ollama serve
```

## Quick Start

### 1. Domain Redirection
Redirect OpenAI domain `api.openai.com` to `127.0.0.1`

### 2. Start mitmproxy Adapter
```bash
sudo mitmdump \
  -s openai_adapter_log.py \
  -p 443 \
  --mode reverse:http://127.0.0.1:11434 \
  --set http2=false \
  --set stream_large_bodies=0
```

### 3. Create Model Aliases (Recommended)
Use Ollama copy command to create model aliases - fastest and safest method:

```bash
# Copy existing models to create aliases
ollama cp llama3.1:latest my-llama3.1
ollama cp qwen3-coder:latest my-qwen3-coder

# Verify model list
ollama list
```

After copying, use the new model names in your API calls.

## Features

- **Model Mapping**: Translate OpenAI model names to local LLM models
- **Streaming Support**: Full support for streaming and non-streaming requests
- **Domain Redirection**: Transparently forward OpenAI API calls to local services
- **Request Aggregation**: Properly handle chunked request bodies

## Configuration

### Model Mapping
Configure model mappings in `openai_adapter_log.py`:
```python
MODEL_MAP = {
    "gpt-4.1-mini": "llama3.1:latest",    # maps to my-llama3.1
    "gpt-4o-mini": "qwen3-coder:latest"  # maps to my-qwen3-coder
}
```

### Environment Variables
```bash
export OPENAI_API_KEY="your-api-key"
```

## Use Cases

- Local development and testing
- Enterprise intranet deployment
- Model migration transition
- API compatibility testing

## Notes

- Requires admin privileges to run mitmproxy
- Ensure Ollama service runs on port 11434
- Recommended to use model copying instead of modifying original models
- Adjust model mappings as needed
