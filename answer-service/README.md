# Answer Service

Conversation and answer generation testing service using Vertex AI conversation capabilities for the Vertex AI Search project.

## Overview

The answer-service module provides conversation testing capabilities for Stream 4 specifications, enabling automated testing of conversation flows and answer quality using Vertex AI's discovery engine.

## Features

- Execute conversation queries with context using Vertex AI
- Generate and validate answers with confidence scoring
- Track conversation sessions with proper session management
- Measure response quality metrics and timing
- Support conversation history and context management

## API

### Core Classes

- `ConversationResult`: Data model for conversation results with metrics
- `AnswerService`: Main service class for conversation management

### Key Methods

- `ask_question()`: Execute conversation queries with context
- `start_conversation()`: Initialize new conversation session
- `end_conversation()`: Terminate conversation session
- `get_conversation_history()`: Retrieve conversation history

## Installation

```bash
# Install dependencies
make setup

# Run tests
make test

# Build package
make build
```

## Development

```bash
# Format code
make format

# Lint code
make lint

# Type check
make typecheck

# Run all quality checks
make quality
```

## Testing

The module follows TDD principles with comprehensive test coverage:

- Unit tests for core functionality
- Integration tests for Vertex AI services
- Acceptance tests for API contract validation
- 80%+ test coverage requirement

## Configuration

Configure your Google Cloud project and credentials before use:

```bash
export GOOGLE_CLOUD_PROJECT="your-project-id"
export GOOGLE_APPLICATION_CREDENTIALS="path/to/credentials.json"
```
