"""
Tests for src/rag.py
====================
All tests use a temporary ChromaDB directory (via tmp_path) and mock PdfReader
so no real PDFs or file-system side effects are left behind.
"""

from unittest.mock import MagicMock, patch

import pytest

import src.rag as rag_module


@pytest.fixture(autouse=True)
def isolated_db(tmp_path, monkeypatch):
    monkeypatch.setattr(rag_module, "_DB_PATH", str(tmp_path / "test_chroma"))
    monkeypatch.setattr(rag_module, "_client", None)
    monkeypatch.setattr(rag_module, "_collection", None)
    yield
    rag_module._client = None
    rag_module._collection = None


def _mock_pdf(pages: list[str]):
    """Returns a context manager that patches PdfReader with the given page texts."""
    mock_pages = []
    for text in pages:
        p = MagicMock()
        p.extract_text.return_value = text
        mock_pages.append(p)

    patcher = patch("src.rag.PdfReader")
    mock_reader_cls = patcher.start()
    mock_reader_cls.return_value.pages = mock_pages
    return patcher


class TestChunkText:
    def test_text_shorter_than_chunk_size_returns_single_chunk(self):
        text = "Hello world. " * 10  # well under 600 chars
        chunks = rag_module._chunk_text(text)
        assert len(chunks) == 1
        assert text.strip() in chunks[0]

    def test_long_text_produces_multiple_chunks(self):
        text = "A" * 1500  # > _CHUNK_SIZE (600)
        chunks = rag_module._chunk_text(text)
        assert len(chunks) > 1

    def test_no_chunk_exceeds_chunk_size(self):
        text = "B" * 3000
        chunks = rag_module._chunk_text(text)
        assert all(len(c) <= rag_module._CHUNK_SIZE for c in chunks)

    def test_overlap_keeps_adjacent_chunks_connected(self):
        # Consecutive chunks should overlap by _CHUNK_OVERLAP characters.
        # Chunk 1 starts at step = _CHUNK_SIZE - _CHUNK_OVERLAP, which is
        # still inside chunk 0 — so chunk 0 must be longer than step.
        text = "X" * 1400
        chunks = rag_module._chunk_text(text)
        step = rag_module._CHUNK_SIZE - rag_module._CHUNK_OVERLAP
        assert len(chunks) >= 2
        assert len(chunks[0]) > step

    def test_fragments_below_minimum_length_are_discarded(self):
        tiny = "x" * (rag_module._MIN_CHUNK_LEN - 1)
        assert rag_module._chunk_text(tiny) == []

    def test_empty_string_returns_empty_list(self):
        assert rag_module._chunk_text("") == []


class TestIndexPdf:
    def test_returns_positive_chunk_count(self):
        page_text = "The quick brown fox. " * 40
        patcher = _mock_pdf([page_text])
        try:
            count = rag_module.index_pdf(b"fake", "doc.pdf")
        finally:
            patcher.stop()
        assert count > 0

    def test_document_count_is_zero_before_any_indexing(self):
        assert rag_module.document_count() == 0

    def test_document_count_increases_after_indexing(self):
        page_text = "Sample paragraph for indexing. " * 30
        patcher = _mock_pdf([page_text])
        try:
            rag_module.index_pdf(b"fake", "sample.pdf")
        finally:
            patcher.stop()
        assert rag_module.document_count() > 0

    def test_multi_page_pdf_indexes_all_pages(self):
        page_texts = ["Page one content. " * 30, "Page two content. " * 30]
        patcher = _mock_pdf(page_texts)
        try:
            count = rag_module.index_pdf(b"fake", "multi.pdf")
        finally:
            patcher.stop()
        assert count > 0
        assert rag_module.document_count() == count

    def test_re_uploading_same_file_is_idempotent(self):
        """Chunk IDs are deterministic — re-indexing must not duplicate data."""
        page_text = "Idempotency test. " * 30
        patcher = _mock_pdf([page_text])
        try:
            first = rag_module.index_pdf(b"fake", "same.pdf")
            second = rag_module.index_pdf(b"fake", "same.pdf")
        finally:
            patcher.stop()
        assert rag_module.document_count() == first == second

    def test_page_with_no_extractable_text_is_skipped(self):
        patcher = _mock_pdf([""])  # extract_text returns empty string
        try:
            count = rag_module.index_pdf(b"fake", "blank.pdf")
        finally:
            patcher.stop()
        assert count == 0
        assert rag_module.document_count() == 0


class TestRetrieveContext:
    def test_returns_empty_string_when_no_docs_indexed(self):
        assert rag_module.retrieve_context("anything") == ""

    def test_returns_non_empty_string_after_indexing(self):
        page_text = "PydanticAI is a typed AI agent framework built on Pydantic. " * 15
        patcher = _mock_pdf([page_text])
        try:
            rag_module.index_pdf(b"fake", "pydantic.pdf")
        finally:
            patcher.stop()
        result = rag_module.retrieve_context("What is PydanticAI?")
        assert isinstance(result, str) and len(result) > 0

    def test_result_includes_source_filename(self):
        page_text = "ChromaDB stores vector embeddings locally. " * 15
        patcher = _mock_pdf([page_text])
        try:
            rag_module.index_pdf(b"fake", "chroma_guide.pdf")
        finally:
            patcher.stop()
        result = rag_module.retrieve_context("vector database")
        assert "chroma_guide.pdf" in result

    def test_result_includes_page_number(self):
        page_text = "Ollama runs large language models on your laptop. " * 15
        patcher = _mock_pdf([page_text])
        try:
            rag_module.index_pdf(b"fake", "ollama.pdf")
        finally:
            patcher.stop()
        result = rag_module.retrieve_context("local models")
        # Metadata format is "filename — p.N"
        assert "p.1" in result


class TestClearIndex:
    def test_clear_resets_count_to_zero(self):
        page_text = "Temporary content to be cleared. " * 20
        patcher = _mock_pdf([page_text])
        try:
            rag_module.index_pdf(b"fake", "temp.pdf")
        finally:
            patcher.stop()
        assert rag_module.document_count() > 0
        rag_module.clear_index()
        assert rag_module.document_count() == 0

    def test_clear_on_empty_store_does_not_raise(self):
        # Must be a no-op, not a KeyError or collection error
        rag_module.clear_index()
        assert rag_module.document_count() == 0

    def test_retrieve_returns_empty_after_clear(self):
        page_text = "Content that will be deleted. " * 20
        patcher = _mock_pdf([page_text])
        try:
            rag_module.index_pdf(b"fake", "todelete.pdf")
        finally:
            patcher.stop()
        rag_module.clear_index()
        assert rag_module.retrieve_context("deleted content") == ""
