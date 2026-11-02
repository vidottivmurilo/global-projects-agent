---
id: "US-001"
epic: "EPIC-01"
title: "[Título Curto e Acoplado ao Valor de Negócio]"
priority: "P1" # P1 (MVP) | P2 | P3
story_points: 3 # Fibonacci: 1 | 2 | 3 | 5 (8+ deve ser quebrado!)
scope: "full-stack" # full-stack | backend | frontend | infra
covers_requirements: ["FR-001"]
contract_operations: ["createResource"]
status: "ready-for-dev" # draft | ready-for-dev | in-progress | built | in-review | done | blocked
baseline_revision: "" # Hash Git gravado pelo Orquestrador/Dev antes de iniciar a codificação
review_loop_iteration: 0
---

<frozen-after-approval reason="human-and-analyst-owned intent — Dev and QA agents MUST NOT modify this block">

## 1. User Story & Valor de Negócio
- **Como** [persona/ator],
- **Quero** [ação/funcionalidade no sistema],
- **Para que** [benefício/valor mensurável].

## 2. Fronteiras e Invariantes da Story (Boundaries)
- **Referências Arquiteturais:** `specs/architecture-spine.md#AD-01`, `specs/architecture-spine.md#AD-02`
- **Contrato Vinculado:** `specs/contracts/openapi.yaml` (`operationId: createResource`)
- **Always (Obrigatório):** [Regras que devem ser seguidas estritamente]
- **Never (Proibido):** [Anti-padrões, acoplamentos ou alterações fora de escopo proibidas]

## 3. Critérios de Aceite em BDD (Gherkin)

### Cenário 1: Caminho Feliz (Happy Path)
- **Given (Dado)** [estado inicial válido do sistema/usuário]
- **When (Quando)** [ação disparada na UI e/ou chamada ao endpoint]
- **Then (Então)** [resposta esperada do Backend, persistência/efeito colateral e estado visual `Success` no Frontend]

### Cenário 2: Validação / Regra de Negócio Violada
- **Given (Dado)** [input inválido ou conflito de estado]
- **When (Quando)** [submissão ocorre]
- **Then (Então)** [Backend retorna código HTTP exato + erro estruturado, e Frontend exibe estado `Error` correspondente]

### Cenário 3: Estados Assíncronos de UI (Quando envolver Frontend)
- **Given (Dado)** que a requisição está em voo ou a listagem está vazia
- **When (Quando)** o componente renderiza
- **Then (Então)** deve exibir estado `Loading` (bloqueando duplo envio) ou estado `Empty` quando aplicável.

## 4. Matriz I/O & Edge Cases
| Cenário | Input / Estado | Output Esperado (Backend) | Comportamento Esperado (Frontend) |
| :--- | :--- | :--- | :--- |
| `HAPPY_PATH` | Payload válido | `HTTP 201` + DTO | Exibe feedback de sucesso e atualiza lista |
| `INVALID_INPUT` | Campo vazio/inválido | `HTTP 422` + erros | Destaca erro no campo do formulário |
| `CONFLICT` | Registro duplicado | `HTTP 409` + código | Exibe alerta de conflito |

</frozen-after-approval>

---

## 5. Mapa de Arquivos (Code Map)
- **Testes Backend (TDD Red):** `[caminho exato do arquivo de teste backend]`
- **Testes Frontend (TDD Red):** `[caminho exato do arquivo de teste frontend]`
- **Implementação Backend (TDD Green):** `[caminhos dos arquivos de produção backend]`
- **Implementação Frontend (TDD Green):** `[caminhos dos arquivos de produção frontend]`

---

## 6. Checklist Passo a Passo de Execução
- [ ] **Passo 1 (QA - TDD RED Backend):** Criar teste automatizado para os cenários Gherkin + stubs vazios até atingir *Clean Red* (falha por asserção).
- [ ] **Passo 2 (QA - TDD RED Frontend):** Criar teste de componente/integração para os estados `Loading`, `Error`, `Empty` e `Success` + stubs vazios até atingir *Clean Red*.
- [ ] **Passo 3 (Dev Back - TDD GREEN & REFACTOR):** Implementar regra de negócio e endpoint sem tocar nos testes até 100% dos testes Backend passarem.
- [ ] **Passo 4 (Dev Front - TDD GREEN & REFACTOR):** Implementar tela/componente consumindo o cliente da API sem tocar nos testes até 100% dos testes Frontend passarem.
- [ ] **Passo 5 (Auto-Verificação & Mutation Check):** Rodar linter, build completo e verificar se mutar condições quebra os testes. Mover status para `built`.

---

## 7. Evidências de Execução (TDD Logs - Append-Only)
<!-- O Agente QA registra aqui o comando e o resumo do output RED. -->
<!-- Os Agentes Dev registram aqui o comando e o resumo do output GREEN. -->

---

## 8. Histórico de Code Review (Append-Only pelo Agente Reviewer)
<!-- O Agente Code Reviewer adiciona aqui o veredito de Spec Compliance e Code Quality. -->

