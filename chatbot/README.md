# Flight Chatbot Knowledge Base

This folder contains the RAG (Retrieval-Augmented Generation) knowledge base system for the flights chatbot assistant.

## Overview

The knowledge base provides contextual information to enhance chatbot responses with relevant airline policies, procedures, and product documentation.

## Structure

```
chatbot/
├── RAG.ipynb              # Jupyter notebook to generate knowledge base files
├── knowledge_base/        # Generated knowledge base files
│   ├── airline_faqs.json  # FAQ entries in JSON format
│   └── product_docs.yaml  # Product documentation in YAML format
└── README.md             # This file
```

## Usage

### 1. Generate Knowledge Base Files

Run the Jupyter notebook to create the knowledge base files:

```bash
cd chatbot
jupyter notebook RAG.ipynb
```

Execute all cells in the notebook to generate:
- `knowledge_base/airline_faqs.json` - Airline FAQ entries
- `knowledge_base/product_docs.yaml` - Product documentation

### 2. Integration

The generated files are automatically loaded by the main API in `api/src/utils/chatbot_tools.py` through the `load_knowledge_base_documents()` function.

## Knowledge Base Content

- **FAQs**: Baggage policies, check-in procedures, booking changes, prohibited items, chatbot capabilities
- **Product Docs**: API documentation, booking management, authentication, system features

## Requirements

- Python 3.8+
- Jupyter Notebook
- PyYAML
- LangChain (for vector store integration)

## RAG Implementation

The system implements Retrieval-Augmented Generation by:
1. Loading documents from JSON/YAML files
2. Creating vector embeddings for semantic search
3. Retrieving relevant context based on user queries
4. Augmenting LLM prompts with retrieved information