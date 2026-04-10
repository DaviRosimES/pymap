# 🗺️ pymap

![CI/CD](https://github.com/DaviRosim/pymap/actions/workflows/ci.yml/badge.svg)
![Coverage](https://img.shields.io/badge/coverage-≥80%25-brightgreen)
![Python](https://img.shields.io/badge/python-3.11%2B-blue)

> HashMap puro em Python — implementação do zero com encadeamento separado e rehashing automático.

Projeto desenvolvido como atividade prática da disciplina **C14 – Engenharia de Software** no Instituto Nacional de Telecomunicações (Inatel), focando em pipeline completo de CI/CD com testes automatizados.

---

## ✨ Funcionalidades

| Método | Descrição |
|---|---|
| `put(key, value)` | Insere ou atualiza um par |
| `get(key, default)` | Recupera um valor (ou default) |
| `remove(key)` | Remove e retorna o valor |
| `contains(key)` | Verifica existência |
| `clear()` | Remove todos os pares |
| `keys() / values() / items()` | Listagem |
| `size() / is_empty()` | Estado do mapa |
| `__setitem__ / __getitem__ / __delitem__` | Sintaxe de dicionário Python |
| `__iter__ / __len__ / __contains__` | Protocolos Python |

**Detalhes internos:**
- Resolução de colisões: **encadeamento separado** (listas por bucket)
- Capacidade padrão: **16 buckets**
- Threshold de rehashing: **0.75**

---

## 📁 Estrutura do Projeto

```
pymap/
├── src/
│   └── pymap/
│       ├── __init__.py
│       └── hashmap.py          # Implementação principal
├── tests/
│   ├── conftest.py
│   ├── test_hashmap_normal.py  # 10+ cenários de fluxo normal
│   └── test_hashmap_edge.py    # 10+ cenários de fluxo de extensão/borda
├── scripts/
│   └── notify.py               # Script de notificação por e-mail
├── .github/
│   └── workflows/
│       └── ci.yml              # Pipeline CI/CD (GitHub Actions)
├── .gitignore
├── pyproject.toml              # Gerenciamento de dependências (Poetry)
└── README.md
```

---

## 🚀 Como executar localmente

### Pré-requisitos

- [pyenv](https://github.com/pyenv/pyenv) instalado
- [Poetry](https://python-poetry.org/) instalado

### Setup

```bash
# 1. Clone o repositório
git clone https://github.com/DaviRosimES/pymap.git
cd pymap

# 2. Defina a versão do Python com pyenv
pyenv local 3.11

# 3. Instale as dependências com Poetry
poetry install

# 4. Execute os testes
poetry run pytest

# 5. Veja o relatório de cobertura (HTML)
open reports/coverage/index.html   # macOS
# ou
xdg-open reports/coverage/index.html  # Linux
```

---

## 🧪 Testes

O projeto possui **22+ cenários de teste** divididos em dois arquivos:

| Arquivo | Foco | Quantidade |
|---|---|---|
| `test_hashmap_normal.py` | Fluxo normal / comportamento esperado | 11 classes / 30+ asserts |
| `test_hashmap_edge.py` | Bordas, erros, colisões, mocks | 10 classes / 25+ asserts |

Tecnologias usadas: **pytest** + **pytest-cov** + **unittest.mock**

---

## ⚙️ Pipeline CI/CD

O pipeline é definido em `.github/workflows/ci.yml` e possui **4 jobs**:

```
┌──────────────┐    ┌──────────────┐
│  🧪 test     │    │  📦 build    │  ← rodam em PARALELO
└──────┬───────┘    └──────┬───────┘
       └────────┬───────────┘
                ▼
        ┌──────────────┐
        │  🚀 deploy   │  ← só após test + build passarem
        └──────┬───────┘
               ▼
        ┌──────────────┐
        │  📧 notify   │  ← sempre, ao final
        └──────────────┘
```

### Artefatos gerados
- `junit-report` – Relatório XML de testes (JUnit)
- `coverage-html` – Relatório HTML de cobertura
- `coverage-xml` – Relatório XML de cobertura
- `dist-packages` – Wheel e sdist do pacote

### Deploy
Cria automaticamente uma **GitHub Release** com os artefatos ao fazer push na `main`.

### Configuração de Secrets/Variables (Settings → Secrets and Variables → Actions)

| Nome | Tipo | Descrição |
|---|---|---|
| `SMTP_HOST` | Secret | Servidor SMTP (ex: `smtp.gmail.com`) |
| `SMTP_PORT` | Secret | Porta SMTP (ex: `587`) |
| `SMTP_USER` | Secret | E-mail remetente |
| `SMTP_PASS` | Secret | Senha ou App Password |
| `NOTIFY_EMAIL` | Variable | E-mail destinatário das notificações |

---
