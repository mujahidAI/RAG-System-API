"""Query transformation using HyDE and multi-query expansion.

This module provides query transformation techniques to improve retrieval:
- HyDE: Generate hypothetical answer for better retrieval
- Multi-query: Generate multiple query variants
"""

from typing import Any, Optional

from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import Runnable

from src.utils.logger import get_logger
from src.utils.config import get_settings

logger = get_logger(__name__)


class QueryTransformer:
    """Query transformer for HyDE and multi-query expansion.

    Provides:
    - HyDE: Hypothetical Document Embedding
    - Multi-query: Generate multiple query variants
    """

    def __init__(
        self,
        llm_chain: Optional[Runnable] = None,
        enable_hyde: bool = False,
        enable_multi_query: bool = False,
        multi_query_count: int = 3,
    ):
        """Initialize the query transformer.

        Args:
            llm_chain: LLM chain for generating hypothetical answers
            enable_hyde: Enable HyDE transformation
            enable_multi_query: Enable multi-query expansion
            multi_query_count: Number of query variants to generate
        """
        settings = get_settings()

        self.llm_chain = llm_chain
        self.enable_hyde = enable_hyde or settings.query_transform.enable_hyde
        self.enable_multi_query = enable_multi_query or settings.query_transform.enable_multi_query
        self.multi_query_count = multi_query_count or settings.query_transform.multi_query_count

        logger.info(
            "QueryTransformer initialized",
            extra={
                "enable_hyde": self.enable_hyde,
                "enable_multi_query": self.enable_multi_query,
                "multi_query_count": self.multi_query_count,
            },
        )

        if self.enable_multi_query and not self.llm_chain:
            logger.warning("Multi-query enabled but no LLM chain provided")

    def transform_hyde(self, query: str) -> str:
        """Transform query using HyDE technique.

        Generates a hypothetical answer that is used for retrieval.

        Args:
            query: Original query

        Returns:
            Transformed query (hypothetical answer)
        """
        if not self.llm_chain:
            logger.warning("HyDE requires LLM chain, returning original query")
            return query

        logger.info("Generating hypothetical answer", extra={"query": query[:50] + "..."})

        hyde_prompt = PromptTemplate.from_template(
            """Given a user question about a knowledge base, generate a hypothetical 
            answer that would be found in the knowledge base. 
            
            Question: {question}
            
            Hypothetical Answer:"""
        )

        hyde_chain = hyde_prompt | self.llm_chain | StrOutputParser()

        try:
            hypothetical_answer = hyde_chain.invoke({"question": query})

            logger.info(
                "HyDE transformation completed",
                extra={"hypothetical_length": len(hypothetical_answer)},
            )

            return hypothetical_answer

        except Exception as e:
            logger.error("HyDE transformation failed", extra={"error": str(e)})
            return query

    def transform_multi_query(self, query: str) -> list[str]:
        """Generate multiple query variants.

        Args:
            query: Original query

        Returns:
            List of query variants including original
        """
        if not self.llm_chain:
            logger.warning("Multi-query requires LLM chain, returning original")
            return [query]

        logger.info(
            "Generating query variants",
            extra={"query": query[:50] + "...", "count": self.multi_query_count},
        )

        multi_query_prompt = PromptTemplate.from_template(
            """Generate {count} different versions of the following user question 
            to retrieve relevant documents from a knowledge base.
            
            Provide these questions separated by newlines.
            
            Original question: {question}
            
            Questions:"""
        )

        multi_query_chain = multi_query_prompt | self.llm_chain | StrOutputParser()

        try:
            result = multi_query_chain.invoke({"question": query, "count": self.multi_query_count})

            query_variants = [line.strip() for line in result.split("\n") if line.strip()]
            query_variants = [query] + query_variants[: self.multi_query_count]

            logger.info(
                "Multi-query transformation completed", extra={"variant_count": len(query_variants)}
            )

            return query_variants

        except Exception as e:
            logger.error("Multi-query transformation failed", extra={"error": str(e)})
            return [query]

    def transform(self, query: str) -> list[str]:
        """Transform query using enabled techniques.

        Args:
            query: Original query

        Returns:
            List of transformed queries
        """
        queries = [query]

        if self.enable_hyde:
            hyde_query = self.transform_hyde(query)
            if hyde_query != query:
                queries.append(hyde_query)

        if self.enable_multi_query:
            multi_queries = self.transform_multi_query(query)
            queries.extend(multi_queries)

        unique_queries = list(dict.fromkeys(queries))

        logger.info(
            "Query transformation completed",
            extra={"original": query[:30], "transformed_count": len(unique_queries)},
        )

        return unique_queries

    def set_llm_chain(self, llm_chain: Runnable) -> None:
        """Set or update the LLM chain.

        Args:
            llm_chain: New LLM chain
        """
        self.llm_chain = llm_chain
        logger.info("LLM chain updated")


class HydeQueryTransformer:
    """Simplified HyDE-only transformer."""

    def __init__(self, llm_chain: Runnable):
        self.transformer = QueryTransformer(llm_chain=llm_chain, enable_hyde=True)

    def transform(self, query: str) -> str:
        return self.transformer.transform_hyde(query)


class MultiQueryTransformer:
    """Simplified multi-query-only transformer."""

    def __init__(self, llm_chain: Runnable, query_count: int = 3):
        self.transformer = QueryTransformer(
            llm_chain=llm_chain,
            enable_multi_query=True,
            multi_query_count=query_count,
        )

    def transform(self, query: str) -> list[str]:
        return self.transformer.transform_multi_query(query)


def get_query_transformer(llm_chain: Optional[Runnable] = None) -> QueryTransformer:
    """Get a configured query transformer.

    Args:
        llm_chain: Optional LLM chain

    Returns:
        Configured QueryTransformer
    """
    return QueryTransformer(llm_chain=llm_chain)
