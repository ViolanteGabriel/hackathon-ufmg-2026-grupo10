# EanterOS — Política de Acordos Inteligente

> **Hackathon UFMG 2026 · Grupo 10** — Sistema de apoio à decisão jurídica desenvolvido para o Banco UFMG. Automatiza a análise de processos de não-reconhecimento de empréstimo e recomenda acordo ou defesa com fundamentação e valoração.

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=white)](https://python.org)
[![React](https://img.shields.io/badge/React-19-61DAFB?logo=react&logoColor=black)](https://react.dev)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16+pgvector-4169E1?logo=postgresql&logoColor=white)](https://github.com/pgvector/pgvector)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker&logoColor=white)](https://docs.docker.com/compose/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**[Video da apresentacao](https://youtu.be/to8Uv4QSDXI)** | **[Slides](docs/presentation.html)** | **[Relatorio](docs/relatorio_hackathon.pdf)**

---

## O Problema

O Banco UFMG recebe **~15.000 novos processos por mes** em que clientes alegam nao reconhecer a contratacao de emprestimos. Para cada processo, um advogado externo precisa decidir: **propor acordo** ou **ir a defesa**. Sem ferramenta, essa decisao e:

- Subjetiva e inconsistente entre advogados
- Impossivel de monitorar em escala
- Sem rastreabilidade de aderencia ou efetividade financeira

---

## A Solucao

O **EanterOS** e um sistema de apoio a decisao que:

1. **Ingere documentos** do processo (Autos + Subsidios) via upload guiado com OCR automatico
2. **Executa um pipeline de IA hibrido** — Rede Neural (RN1) + RAG sobre sentencas historicas + GPT-4o-mini
3. **Recomenda ACORDO ou DEFESA** com valor sugerido, intervalo de negociacao, nivel de confianca e citacoes textuais dos documentos
4. **Registra a decisao do advogado** (HITL) para monitoramento de aderencia e efetividade financeira

---

## Quick Start

**Prerequisitos:** Docker 24+ e Docker Compose v2. Node.js e Python nao sao necessarios no host.

```bash
# 1. Clone o repositorio
git clone https://github.com/ViolanteGabriel/hackathon-ufmg-2026-grupo10.git
cd hackathon-ufmg-2026-grupo10

# 2. Configure e suba tudo com o script automatico
bash setup.sh
# O script solicita sua OPENAI_API_KEY interativamente
```

Ao final, acesse:

| Servico | URL |
|---------|-----|
| **Frontend** | http://localhost:5173 |
| **API (Swagger)** | http://localhost:8000/docs |
| **Health check** | http://localhost:8000/health |

> Para instrucoes detalhadas (setup manual, variaveis de ambiente, troubleshooting), veja [SETUP.md](SETUP.md).

---

## Credenciais de Demo

| Perfil | E-mail | Senha |
|--------|--------|-------|
| Advogado | `advogado@banco.com` | `advogado123` |
| Banco (gestor) | `banco@banco.com` | `banco123` |

---

## Como Funciona

### Pipeline de IA (Upload -> Recomendacao em ~15-30s)

```
Advogado faz upload de PDFs (Autos + Subsidios)
          |
          v
  [Estagio 0] Ingestion
  pdfplumber + Tesseract OCR (fallback para PDFs escaneados)
          |
          v
  [Estagio 1] Extracao de Metadados
  GPT-4o-mini extrai: UF, valor_da_causa, sub_assunto
          |
          v
  [Estagio 2] RAG por Processo
  pgvector kNN busca sentencas historicas similares (60k registros)
          |
          v
  [Estagio 3] Classificador RN1
  Rede Neural PyTorch (treinada em 60k sentencas) -> probabilidade de derrota
          |
          v
  [Estagio 4] Analista GPT
  GPT-4o-mini (Structured Outputs) -> ACORDO/DEFESA + confianca + fatores
          |
          v
  [Estagio 5] Valoracao
  GPT calcula valor_sugerido, intervalo_min/max e economia_esperada
          |
          v
  [Estagio 6] HITL
  Advogado aceita / ajusta (justificativa obrigatoria) / recusa
          |
          v
  Metricas de aderencia e efetividade (painel do banco)
```

### Política de Decisao (`policy.yaml`)

Os limiares sao configurados sem redeploy:

| Parametro | Valor padrao |
|-----------|-------------|
| Confianca verde (recomendacao automatica) | >= 0.85 |
| Confianca amarela (revisar) | 0.60 – 0.85 |
| Piso do acordo | R$ 1.500 |
| Teto do acordo | R$ 50.000 |
| Penalidade: sem contrato | -20% |
| Penalidade: sem comprovante BACEN | -15% |

---

## Requisitos do Hackathon Atendidos

| Requisito | Implementacao |
|-----------|--------------|
| **Regra de decisao** | RN1 (PyTorch, 60k sentencas) + RAG (pgvector) + GPT-4o-mini Structured Outputs |
| **Sugestao de valor** | Valuator GPT: `valor_sugerido`, `intervalo_min/max`, `economia_esperada` via `policy.yaml` |
| **Acesso a recomendacao** | Decision Lab (React): decisao, confianca, valor, fatores pro/contra, trechos citados |
| **Monitoramento de aderencia** | Toda decisao HITL e gravada com timestamp e justificativa obrigatoria em ajustes |
| **Monitoramento de efetividade** | Dashboard executivo: taxa de acordos, economia acumulada, drift de confianca, alertas |

---

## Fluxo de Uso

### Perfil: Advogado

1. Login em http://localhost:5173 com `advogado@banco.com`
2. **Central de Evidencias** (`/upload`): upload sequencial dos documentos — permite "Pular" documentos ausentes
3. Clicar em **Upload and Analyze** — o pipeline roda automaticamente
4. **Decision Lab** (`/dashboard/:id`): visualiza recomendacao com valor sugerido, confianca e trechos dos documentos
5. Clicar em **ACEITAR**, **AJUSTAR** (com justificativa) ou **RECUSAR**

### Perfil: Banco (Gestor)

1. Login com `banco@banco.com`
2. **Monitoramento** (`/monitoring`): aderencia por advogado, economia acumulada, feed de recomendacoes recentes e casos de alto risco

---

## Estrutura do Projeto

```
hackathon-ufmg-2026-grupo10/
├── src/
│   ├── back/                     # API FastAPI (Python 3.11+)
│   │   ├── app/
│   │   │   ├── core/             # JWT, logging, exceptions
│   │   │   ├── db/models/        # processo, documento, analise_ia,
│   │   │   │                     # proposta_acordo, decisao_advogado,
│   │   │   │                     # sentenca_historica (pgvector)
│   │   │   ├── routers/          # auth, processes, analysis, metrics
│   │   │   ├── schemas/          # contratos Pydantic (request/response)
│   │   │   └── services/
│   │   │       ├── ai/           # pipeline, extractor, classifier (RN1),
│   │   │       │                 # llm_classifier, valuator, retriever (RAG)
│   │   │       └── ingestion/    # pdf (pdfplumber + OCR), xlsx
│   │   ├── alembic/              # migracoes de banco de dados
│   │   ├── policy.yaml           # parametros da politica de acordos
│   │   └── pyproject.toml
│   ├── front/                    # React 19 + TypeScript + Vite
│   │   └── src/
│   │       ├── screens/          # Login, Home, Upload, ProcessList,
│   │       │                     # Dashboard (Decision Lab), Monitoring
│   │       ├── modules/          # tema (dark/light), componentes UI
│   │       └── api/              # TanStack Query hooks + axios client
│   └── models/RN1/               # Rede neural PyTorch + dados de treino
├── models/
│   └── litigation_model.pth      # pesos treinados da RN1
├── data/
│   └── examples/                 # processos de exemplo para demo
├── docs/
│   ├── presentation.html         # slides da apresentacao (navegue com <- ->)
│   ├── relatorio_hackathon.pdf   # relatorio escrito
│   ├── policy.md                 # documentacao da politica de acordos
│   └── adr/                      # Architecture Decision Records
├── docker-compose.yml
├── setup.sh                      # script de setup automatizado
├── .env.example                  # template de variaveis de ambiente
└── SETUP.md                      # guia completo de instalacao
```

---

## Stack Tecnologica

| Camada | Tecnologia |
|--------|-----------|
| **Frontend** | React 19, TypeScript 5.8, Vite 6, TanStack Query v5, React Router v7, Zod v4 |
| **Backend** | FastAPI 0.115, SQLAlchemy 2.0, Alembic, Pydantic v2, Python 3.11 |
| **IA Generativa** | OpenAI GPT-4o-mini (Structured Outputs) + `text-embedding-3-small` |
| **ML** | PyTorch (RN1 — 60k sentencas judiciais), scikit-learn |
| **Banco de dados** | PostgreSQL 16 + pgvector (busca vetorial para RAG) |
| **OCR** | Tesseract `por` + pdfplumber |
| **Auth** | JWT (python-jose + passlib/bcrypt) |
| **Infra** | Docker Compose (3 servicos: db, back, front) |

---

## Documentos Suportados

| Codigo | Categoria | Descricao |
|--------|-----------|-----------|
| `PETICAO_INICIAL` | Autos | Peticao inicial do processo |
| `PROCURACAO` | Autos | Procuracao do advogado do autor |
| `CONTRATO` | Subsidio | Contrato de emprestimo firmado |
| `EXTRATO` | Subsidio | Extrato bancario da conta do autor |
| `COMPROVANTE_CREDITO` | Subsidio | Comprovante regulatorio BACEN |
| `DOSSIE` | Subsidio | Dossie de autenticidade de assinaturas |
| `DEMONSTRATIVO_DIVIDA` | Subsidio | Evolucao mensal da divida |
| `LAUDO_REFERENCIADO` | Subsidio | Laudo interno da operacao de credito |

---

## Apresentacao

- **Video:** [youtu.be/to8Uv4QSDXI](https://youtu.be/to8Uv4QSDXI)
- **Slides:** abra `docs/presentation.html` no browser e navegue com as setas do teclado

---

## Equipe — Grupo 10

Eduardo Muniz · Gabriel Rabelo · Gabriel Violante · Ian Paleta · Rafael Sollino

---

## Licenca

Distribuido sob a licenca MIT. Veja [LICENSE](LICENSE) para detalhes.
