# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a mitmproxy-based LLM API adapter that intercepts and modifies OpenAI API traffic. It consists of two main components:

1. **openai_adapter.py** - Basic adapter for API key injection and model list modification
2. **openai_adapter_log.py** - Advanced adapter with model mapping and streaming support

## Key Components

### openai_adapter.py
- **Purpose**: Injects OPENAI_API_KEY from environment variable and modifies /v1/models responses
- **Key functions**:
  - `request()`: Adds authorization header for api.openai.com requests
  - `response()`: Rewrites /v1/models responses with fixed model list
- **Environment variable**: `OPENAI_API_KEY` - API key to inject

### openai_adapter_log.py
- **Purpose**: Maps OpenAI model names to alternative LLM models with full streaming support
- **Key features**:
  - `MODEL_MAP`: Dictionary mapping OpenAI models to target models
  - `BodyRewriter` class handles request modification
  - Supports both streaming and non-streaming requests
  - Uses mitmproxy's event system for chunk aggregation
- **Model mappings**:
  - "gpt-4.1-mini" → "llama3.1:latest"
  - "gpt-4o-mini" → "qwen3-coder:latest"

## Usage

### Running mitmproxy with adapters
```bash
# Basic adapter
mitmproxy -s openai_adapter.py

# Advanced adapter with model mapping
mitmproxy -s openai_adapter_log.py

# With specific port
mitmproxy -s openai_adapter_log.py -p 8080
```

### Environment Setup
```bash
export OPENAI_API_KEY="your-api-key-here"
mitmproxy -s openai_adapter.py
```

### Browser/Client Configuration
Configure your browser or application to use mitmproxy as a proxy:
- Host: localhost (or where mitmproxy runs)
- Port: 8080 (default) or specified port

## Development Notes

- No build system or package manager required (pure Python mitmproxy addons)
- No linting/testing setup (simple script-based architecture)
- Both files are independent mitmproxy addons - use one or the other, not both simultaneously
- Logging uses mitmproxy's ctx.log system
- Streaming support handles chunked HTTP requests properly