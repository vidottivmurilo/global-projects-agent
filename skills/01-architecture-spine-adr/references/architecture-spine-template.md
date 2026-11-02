# 🏛️ Architecture Spine: [NOME DO PROJETO]

## 1. Stack Tecnológica & Comandos Oficiais (Single Source of Truth)

| Camada | Tecnologia / Versão | Comando de Build | Comando de Teste | Comando de Lint |
| :--- | :--- | :--- | :--- | :--- |
| **Backend** | Ex: C# .NET 9 / Java 21 / Python 3.12 | `dotnet build` | `dotnet test` | `dotnet format --verify-no-changes` |
| **Frontend** | Ex: React + TypeScript + Vite | `npm run build` | `npm run test -- --run` | `npm run lint` |
| **InfraLocal** | Docker Compose + Postgres + Redis | `docker compose build` | `docker compose ps` | N/A |

---

## 2. Árvore de Diretórios Canônica

```text
<projeto>/
├── docker-compose.yml
├── README.md
├── docs/
│   └── architecture-decisions.md
├── specs/
│   ├── architecture-spine.md
│   ├── traceability-matrix.md
│   ├── kanban-board.md
│   ├── contracts/
│   │   └── openapi.yaml
│   └── stories/
│       └── US-001-plan.md
├── backend/
│   ├── src/
│   └── tests/
└── frontend/
    ├── src/
    └── tests/
```

---

## 3. Regras Invariantes de Arquitetura (`AD-1..AD-N`)

> **Atenção Subagentes:** Violar qualquer invariante abaixo resulta em reprovação imediata no Code Review Gate.

### `AD-01`: Isolamento de Domínio e Camadas
- **Binds:** `backend/src/`
- **Rule:** A camada de Domínio/Aplicação não depende de frameworks web, ORM concreto ou bibliotecas de infraestrutura externa. Use inversão de dependência (Interfaces/Ports).
- **Prevents:** Acoplamento direto de Controllers/Endpoints com banco de dados ou clientes HTTP externos.

### `AD-02`: Consumo Tipado e Centralizado no Frontend
- **Binds:** `frontend/src/`
- **Rule:** Componentes visuais nunca fazem chamadas `fetch`/`axios` soltas com URLs hardcoded. Toda comunicação HTTP passa pela camada de serviço/cliente tipado derivado de `specs/contracts/openapi.yaml`.
- **Prevents:** Divergência de payload entre Front e Back e URLs espalhadas em componentes.

### `AD-03`: Tratamento Padronizado de Erros
- **Binds:** `backend/` e `frontend/`
- **Rule:** O Backend retorna erros estruturados (RFC 7807 Problem Details ou envelope padrão do contrato). O Frontend captura e exibe feedback visual claro para estados de erro (`4xx` validação vs `5xx` falha inesperada).
- **Prevents:** Exceptions não tratadas vazando stacktrace ou falhas silenciosas na tela do usuário.

