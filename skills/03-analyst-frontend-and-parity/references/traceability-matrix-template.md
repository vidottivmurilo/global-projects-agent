# 🔗 Matriz de Rastreabilidade e Paridade Full-Stack: [NOME DO PROJETO]

> **Invariante de Paridade:** Todo `operationId` do tipo `user-facing` definido em `specs/contracts/openapi.yaml` DEVE possuir mapeamento completo nesta tabela (Backend Handler + Componente Frontend + Estados de UI + Testes Automatizados).

---

## 1. Mapeamento Ponta-a-Ponta (Contrato $\leftrightarrow$ Backend $\leftrightarrow$ Frontend $\leftrightarrow$ Testes)

| Requisito (`FR`) | Story ID | `operationId` (OpenAPI) | Método & Rota HTTP | Handler / Caso de Uso (Backend) | Rota & Componente (Frontend) | Estados de UI Exigidos | Teste Backend | Teste Frontend / E2E | Status de Paridade |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `FR-001` | `US-001` | `createResource` | `POST /api/v1/resources` | `CreateResourceHandler` | `/resources` (`CreateResourceForm`) | `Loading`, `Error 422/409`, `Success` | `CreateResourceTests` | `CreateResourceForm.spec` | `[ ] Pendente` |
| `FR-002` | `US-002` | `listResources` | `GET /api/v1/resources` | `ListResourcesHandler` | `/resources` (`ResourceListTable`) | `Loading`, `Empty`, `Error 500`, `Success` | `ListResourcesTests` | `ResourceListTable.spec` | `[ ] Pendente` |

---

## 2. Checklist de Verificação de Paridade (Executado no Gate de Code Review)
- [ ] Todos os `operationId`s de `specs/contracts/openapi.yaml` constam na tabela acima?
- [ ] Nenhum componente Frontend utiliza dados mockados/hardcoded no código de produção em vez de chamar o cliente da API?
- [ ] Todos os 4 estados visuais (`Loading`, `Empty`, `Error`, `Success`) possuem cobertura nos testes de componente/UI?

