FROM python:3.11-slim

# 1. Dependências do sistema (raramente mudam - Cache pesado)
RUN apt-get update && apt-get install -y --no-install-recommends \
    tesseract-ocr \
    tesseract-ocr-por \
    libpq-dev \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 2. Upgrade do pip
RUN pip install --upgrade pip setuptools

# 3a. PyTorch CPU-only (instalado antes para usar o índice correto e evitar CUDA ~900MB)
RUN pip install --no-cache-dir \
    torch>=2.1.0 \
    scikit-learn>=1.3.0 \
    numpy>=1.24.0 \
    --extra-index-url https://download.pytorch.org/whl/cpu

# 3b. Instalação de demais dependências (Cacheado se o pyproject.toml não mudar)
COPY pyproject.toml .
RUN mkdir app && touch app/__init__.py && \
    pip install --no-cache-dir .[dev]

# 4. Copia o restante do código (Muda sempre - Rebuild rápido aqui)
COPY . .

# 5. Instalação final para garantir que o pacote local e scripts sejam registrados
RUN pip install --no-cache-dir .[dev] && \
    sed -i 's/\r$//' scripts/init_db.sh && \
    chmod +x scripts/init_db.sh

# 6. Pré-download do modelo de embeddings para cache na imagem (~120MB)
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')"

EXPOSE 8000
ENTRYPOINT ["/bin/bash", "scripts/init_db.sh"]
