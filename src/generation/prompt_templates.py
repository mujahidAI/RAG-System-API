"""Prompt templates for the RAG generation pipeline.

This module contains all prompt templates used for:
- Answer generation with context
- HyDE hypothetical answer generation
- Multi-query expansion
- Evaluation prompts
"""

from langchain_core.prompts import PromptTemplate


ANSWER_GENERATION_TEMPLATE = """You are a helpful AI assistant. Use the following context to answer the user question.

Guidelines:
1. Answer only based on the provided context
2. If the context does not contain enough information to answer the question, say "I dont have enough information to answer this question based on the provided context."
3. Cite the sources when possible using the format [Source: filename]
4. Be concise and accurate in your response

Context:
{context}

Question: {question}

Answer:"""

QUESTION_ANSWERING_PROMPT = PromptTemplate.from_template(ANSWER_GENERATION_TEMPLATE)


CONTEXT_ONLY_TEMPLATE = """Based only on the following context, answer the question:

Context:
{context}

Question: {question}

Provide your answer:"""

CONTEXT_PROMPT = PromptTemplate.from_template(CONTEXT_ONLY_TEMPLATE)


HYDE_TEMPLATE = """Given a user question about a knowledge base, generate a hypothetical 
answer that would be found in the knowledge base. 

Question: {question}

Hypothetical Answer:"""

HYDE_PROMPT = PromptTemplate.from_template(HYDE_TEMPLATE)


MULTI_QUERY_TEMPLATE = """Generate {count} different versions of the following user question 
to retrieve relevant documents from a knowledge base.

Provide these questions separated by newlines.

Original question: {question}

Questions:"""

MULTI_QUERY_PROMPT = PromptTemplate.from_template(MULTI_QUERY_TEMPLATE)


CITATION_TEMPLATE = """Using the following context, answer the question and cite your sources:

Context:
{context}

Question: {question}

Answer (with citations):"""

CITATION_PROMPT = PromptTemplate.from_template(CITATION_TEMPLATE)


def get_answer_prompt() -> PromptTemplate:
    return QUESTION_ANSWERING_PROMPT


def get_citation_prompt() -> PromptTemplate:
    return CITATION_PROMPT


def get_hyde_prompt() -> PromptTemplate:
    return HYDE_PROMPT


def get_multi_query_prompt() -> PromptTemplate:
    return MULTI_QUERY_PROMPT


def format_context(documents, max_docs: int = 5) -> str:
    context_parts = []
    for i, doc in enumerate(documents[:max_docs]):
        source = doc.metadata.get("source_file", "unknown")
        content = doc.page_content
        context_parts.append(f"[Document {i+1} from {source}]\n{content}\n")
    return "\n---\n".join(context_parts)


def format_sources(documents):
    sources = []
    for doc in documents:
        sources.append(
            {
                "content": (
                    doc.page_content[:200] + "..."
                    if len(doc.page_content) > 200
                    else doc.page_content
                ),
                "source": doc.metadata.get("source_file", "unknown"),
                "chunk_index": doc.metadata.get("chunk_index", 0),
            }
        )
    return sources
