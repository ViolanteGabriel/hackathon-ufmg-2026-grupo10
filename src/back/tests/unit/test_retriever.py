"""Unit tests para `app.services.ai.retriever`.

Cobertura:
  - Chunking em janelas com overlap
  - Fallback "naive" (keyword overlap) quando sentence-transformers indisponível
  - Fallback "naive" quando a chamada de embedding falha
  - `lookup_historical_win_rate` com e sem registros
  - `InProcessRetriever.search` devolve top-k com doc_type preservado
"""
from __future__ import annotations

from dataclasses import dataclass
from unittest.mock import patch

import pytest

from app.services.ai.retriever import (
    Chunk,
    InProcessRetriever,
    _cosine,
    _window_chunks,
    lookup_historical_win_rate,
)


@dataclass
class _FakeDoc:
    doc_type: str
    original_filename: str
    raw_text: str


# ---------------------------------------------------------------------------
# Chunking
# ---------------------------------------------------------------------------

def test_window_chunks_cria_overlap_quando_texto_longo():
    """Texto com 1000 palavras gera >1 chunks com overlap esperado."""
    text = " ".join(f"palavra{i}" for i in range(1000))
    chunks = list(_window_chunks(text))
    assert len(chunks) >= 2, "texto longo deve gerar múltiplos chunks"
    first_words = chunks[0].split()[-20:]
    second_chunk_prefix = chunks[1].split()[:50]
    assert any(w in second_chunk_prefix for w in first_words)


def test_window_chunks_texto_vazio_retorna_nada():
    assert list(_window_chunks("")) == []
    assert list(_window_chunks("   ")) == []


# ---------------------------------------------------------------------------
# Retriever (naive fallback — sentence-transformers indisponível)
# ---------------------------------------------------------------------------

@patch("app.services.ai.retriever._get_embedder", return_value=None)
def test_retriever_sem_embedder_usa_naive(_mock):
    docs = [
        _FakeDoc(
            doc_type="PETICAO_INICIAL",
            original_filename="peticao.pdf",
            raw_text=(
                "A parte autora alega ter sido vítima de golpe por terceiros. "
                "Nunca contratou o empréstimo em questão e não reconhece "
                "a assinatura presente no contrato apresentado."
            ),
        ),
        _FakeDoc(
            doc_type="CONTRATO",
            original_filename="contrato.pdf",
            raw_text=(
                "Contrato de empréstimo pessoal celebrado em 10/05/2024 "
                "no valor de R$ 8.000,00 com taxa de juros de 2,99% ao mês."
            ),
        ),
    ]
    retriever = InProcessRetriever.from_documents(docs)
    assert retriever.method == "naive"
    assert len(retriever.chunks) >= 2

    # Busca por "assinatura golpe" deve priorizar o chunk da petição
    results = retriever.search("assinatura golpe fraude", k=2)
    assert len(results) >= 1
    assert results[0].chunk.doc_type == "PETICAO_INICIAL"


@patch("app.services.ai.retriever._get_embedder", return_value=None)
def test_retriever_sem_documentos_retorna_vazio(_mock):
    retriever = InProcessRetriever.from_documents([])
    assert retriever.chunks == []
    assert retriever.search("qualquer coisa") == []


@patch("app.services.ai.retriever._get_embedder", return_value=None)
def test_retriever_ignora_docs_sem_raw_text(_mock):
    docs = [
        _FakeDoc(doc_type="OUTRO", original_filename="vazio.pdf", raw_text=""),
        _FakeDoc(
            doc_type="PETICAO_INICIAL",
            original_filename="p.pdf",
            raw_text="parte autora alega fraude com documentação suficiente",
        ),
    ]
    retriever = InProcessRetriever.from_documents(docs)
    assert all(c.doc_type == "PETICAO_INICIAL" for c in retriever.chunks)


# ---------------------------------------------------------------------------
# Fallback quando embedding falha durante encode
# ---------------------------------------------------------------------------

@patch("app.services.ai.retriever._get_embedder")
def test_retriever_embedding_falho_cai_para_naive(mock_get_embedder):
    mock_embedder = mock_get_embedder.return_value
    mock_embedder.encode.side_effect = RuntimeError("sem rede")

    docs = [
        _FakeDoc(
            doc_type="PETICAO_INICIAL",
            original_filename="p.pdf",
            raw_text="Alegação de golpe e fraude por terceiro desconhecido.",
        )
    ]
    retriever = InProcessRetriever.from_documents(docs)
    assert retriever.method == "naive"
    # Mesmo após falha, search ainda funciona via keyword overlap
    results = retriever.search("golpe fraude", k=1)
    assert len(results) == 1


# ---------------------------------------------------------------------------
# Similaridade cosseno
# ---------------------------------------------------------------------------

def test_cosine_vetores_iguais_retorna_1():
    v = [1.0, 2.0, 3.0]
    assert _cosine(v, v) == pytest.approx(1.0)


def test_cosine_vetores_ortogonais_retorna_0():
    assert _cosine([1.0, 0.0], [0.0, 1.0]) == pytest.approx(0.0)


def test_cosine_vetor_vazio_retorna_0():
    assert _cosine([], [1.0, 2.0]) == 0.0
    assert _cosine([1.0, 2.0], [0.0, 0.0]) == 0.0


# ---------------------------------------------------------------------------
# Chunk.preview
# ---------------------------------------------------------------------------

def test_chunk_preview_trunca_com_reticencias():
    c = Chunk(
        doc_type="PETICAO_INICIAL",
        doc_filename="p.pdf",
        chunk_index=0,
        text="a" * 500,
    )
    preview = c.preview(max_chars=100)
    assert len(preview) == 100
    assert preview.endswith("…")


def test_chunk_preview_nao_trunca_texto_curto():
    c = Chunk(
        doc_type="OUTRO",
        doc_filename="o.pdf",
        chunk_index=0,
        text="texto curto",
    )
    assert c.preview() == "texto curto"


# ---------------------------------------------------------------------------
# lookup_historical_win_rate (fallback seguro)
# ---------------------------------------------------------------------------

def test_lookup_historical_sem_tabela_retorna_default(db):
    """Sem SentencaHistorica criada (SQLite test env), deve devolver default sem crashar."""
    prob, n = lookup_historical_win_rate(db, uf="MG", sub_assunto="golpe")
    assert prob == 0.30
    assert n == 0
