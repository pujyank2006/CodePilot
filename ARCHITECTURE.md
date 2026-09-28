
# CodePilot Architecture

## Overview

CodePilot is a full-stack AI coding assistant.
The React frontend communicates with a FastAPI
backend, which manages application logic and
interacts with LLMs and development tools.

## Components

### Frontend
- React + Vite
- Chat interface
- Repository and code views

### Backend
- FastAPI routes
- Pydantic schemas
- Application services
- Configuration management

### LLM Layer
- Provider integration
- Prompt management
- Structured outputs
- Tool calling

### Future Components
- Repository ingestion and retrieval
- AST and Tree-sitter analysis
- Agent execution loop
- MCP integration
- Git and test-runner tools

## Initial Request Flow

1. User interacts with React.
2. React sends an HTTP request to FastAPI.
3. FastAPI validates the request.
4. Application logic processes it.
5. FastAPI returns a JSON response.
6. React displays the result.