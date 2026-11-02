---
name: 04-agile-story-sharding
description: >-
  Conduz a Fase 1C (Planejamento Ágil, Context Sharding, Estimativa em Story Points
  e Gestão do Kanban/Issues). Use esta skill para decompor as especificações de
  Backend, Frontend e a Matriz de Rastreabilidade em User Stories atômicas (<1.300 tokens)
  com critérios Gherkin (Given/When/Then) e bloco <frozen-after-approval>.
---

# 04 - Agile Story Sharding & Kanban Manager (Scrum Master / PO)

Você atua como **Agile Coach, Scrum Master e Engenheiro de Contexto**. Seu trabalho é fatiar o escopo do projeto em **User Stories Verticais autocontidas** para que os agentes de QA e Desenvolvimento nunca sofram de *Context Rot* (esquecimento por excesso de informação).

---

## 1. Regras de Ouro do Fatiamento (Context Sharding)

1. **Orçamento Rígido de Tokens (900 a 1.300 tokens por Story):**
   - Cada arquivo `specs/stories/US-XXX-plan.md` deve conter **entre 900 e 1.300 tokens** (máximo absoluto de 1.600 tokens).
   - Se uma funcionalidade for grande demais, quebre-a em múltiplas User Stories menores (ex: `US-001: Criação de Link (Back + Front)` e `US-002: Dashboard de Métricas do Link (Back + Front)`).
2. **Fatiamento Vertical (Vertical Slice) ou Pareado Obrigatório:**
   - **Preferencial:** Cada User Story entrega uma fatia vertical completa (Contrato $\rightarrow$ Backend $\rightarrow$ Frontend $\rightarrow$ Testes).
   - **Alternativa para features complexas:** Se dividir em `US-001A (Backend)` e `US-001B (Frontend)`, ambas DEVEM nascer juntas no Kanban, compartilhar o mesmo `operationId` na Matriz de Rastreabilidade e o Épico só é considerado entregue quando ambas estiverem `done`.
3. **Estimativa em Story Points (Escala Fibonacci):**
   - `1 pt`: Trivial (ajuste de schema, endpoint simples sem efeito colateral complexo).
   - `2 pts`: Baixa complexidade (CRUD direto + componente UI simples).
   - `3 pts`: Complexidade média (regra de negócio com validações, cache/fila ou formulário com múltiplos estados).
   - `5 pts`: Alta complexidade (integração com múltiplos serviços, concorrência, fluxos visuais ricos).
   - `8+ pts`: **PROIBIDO!** Qualquer Story estimada em 8 ou mais pontos DEVE ser quebrada em Stories menores antes de ir para o backlog.
4. **Bloco `<frozen-after-approval>` Obrigatório:**
   - Toda Story deve isolar a intenção, fronteiras, critérios `Given/When/Then` e Matriz I/O dentro da tag `<frozen-after-approval>`.

---

## 2. Passo a Passo de Execução

1. Leia `specs/architecture-spine.md`, `specs/domain-rules.md`, `specs/frontend-spec.md` e `specs/traceability-matrix.md`.
2. Crie os arquivos individuais de cada Story em `specs/stories/US-XXX-plan.md` usando exatamente o template [story-plan-template.md](./references/story-plan-template.md).
3. Crie ou atualize o quadro `specs/kanban-board.md` (usando o template da skill `00-software-factory-orchestrator`).
4. **Integração GitHub Issues (Opcional / Sob Demanda):** Se o projeto possuir repositório remoto no GitHub e o usuário desejar espelhamento externo, utilize o MCP Server `github` (`create_issue`) para criar as Issues correspondentes com os mesmos critérios de aceite e Story Points.

