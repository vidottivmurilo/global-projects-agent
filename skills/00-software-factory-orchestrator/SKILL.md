---
name: 00-software-factory-orchestrator
description: >-
  Orquestrador central (Maestro) da Fábrica de Software Multi-Agente. Use esta skill
  quando o usuário solicitar a construção estruturada de um projeto, épico ou User Story
  pela esteira no Modo Rígido Multi-Agente, coordenando via subagentes dedicados (invoke_subagent)
  o Arquiteto, Analistas de Back e Front, Gestor Ágil, QA TDD Red, Devs Green e a Banca dos 5 Revisores.
---

# 00 - Software Factory Orchestrator (Maestro da Esteira)

Esta skill define o protocolo operacional do **Agente Orquestrador (Tech Lead / Controller)** para construir sistemas completos, escaláveis e sem lacunas de escopo entre Backend e Frontend.

---

## 0. O Modo Rígido Multi-Agente (Padrão Obrigatório)

No Modo Rígido da esteira:
1. **O Maestro NÃO escreve código de produção nem testes diretamente na thread principal.**
2. O Maestro atua como maestro de engenharia: analisa requisitos, planeja contratos, gerencia o Kanban e **invoca subagentes dedicados (atividades-filho) via `invoke_subagent`**.
3. Cada subagente opera em seu próprio processo com contexto restrito (`< 1.300 tokens`), persona especializada e permissões delimitadas.

---

## 1. Topologia de Subagentes e Permissões (`invoke_subagent`)

Ao acionar a esteira, o Orquestrador DEVE delegar as tarefas via `invoke_subagent`:

| Papel do Subagente | Nome Sugerido (`TypeName`) | `EnableWriteTools` | Skill Obrigatória |
| :--- | :--- | :--- | :--- |
| **Arquiteto de Software** | `architect-agent` | `true` (apenas docs/configs) | `01-architecture-spine-adr` |
| **Analista de Backend & Contratos** | `analyst-backend` | `true` (apenas `specs/`) | `02-analyst-contract-and-back` |
| **Analista de Frontend & Paridade** | `analyst-frontend` | `true` (apenas `specs/`) | `03-analyst-frontend-and-parity`, `09-frontend-design-craft` |
| **Agile & Backlog Manager** | `agile-scrum-master` | `true` (apenas `specs/`) | `04-agile-story-sharding` |
| **QA Test Writer (TDD RED)** | `qa-tdd-red` | `true` (apenas `tests/` + stubs) | `05-tdd-red-test-writer` |
| **Dev Backend (TDD GREEN)** | `dev-backend-green` | `true` (bloqueado em `tests/`) | `06-tdd-green-refactor-dev` |
| **Dev Frontend (TDD GREEN)** | `dev-frontend-green` | `true` (bloqueado em `tests/`) | `06-tdd-green-refactor-dev`, `09-frontend-design-craft` |
| **Banca dos 5 Revisores** | `tech-code-reviewer` | **`false` (Read-Only total)** | `07-code-reviewer-gate` |
| **Git & Living Docs Steward** | `git-docs-steward` | `true` | `08-living-docs-and-commit` |

---

## 2. Sequência de Execução da Esteira (End-to-End Pipeline)

### Fase 0: Fundação e Arquitetura (`01-architecture-spine-adr`)
1. Conduza o debate socrático com o usuário para definir: Stack/Linguagem, Padrão Arquitetural, Banco de Dados, Mensageria e Infra (`docker-compose.yml`).
2. Gere o `specs/architecture-spine.md`, a estrutura de diretórios semente e o ADR inicial em `docs/architecture-decisions.md`.
3. **Quality Gate 0:** Obtenha o "ok" explícito do usuário antes de avançar para a Fase 1.

### Fase 1: Engenharia de Requisitos, Contratos e Paridade (Paralelismo Controlado)
1. **Passo 1A (Contrato + Análise Backend):** Acione o `analyst-backend` com a skill `02-analyst-contract-and-back` para produzir regras de domínio e contrato `specs/contracts/openapi.yaml`.
2. **Passo 1B (Análise Frontend + Paridade 1:1):** Acione o `analyst-frontend` com a skill `03-analyst-frontend-and-parity` para produzir telas e a **Matriz de Rastreabilidade (`specs/traceability-matrix.md`)**, garantindo que **100% dos `operationId`s do Backend possuam tela correspondente**.
3. **Passo 1C (Sharding de Stories + Kanban):** Acione o `agile-scrum-master` com a skill `04-agile-story-sharding` para fatiar o trabalho em Stories atômicas (`specs/stories/US-XXX-plan.md`, 900-1.300 tokens) e atualizar o Kanban.
4. **Quality Gate 1:** Apresente a Matriz de Paridade e o Kanban ao usuário e aguarde o "ok".

### Fase 2: Loop TDD Estrito por User Story via Subagentes (`US-XXX`)
Para cada User Story em ordem de prioridade:
1. **Registro de Baseline:** Grave o hash atual do Git (`git rev-parse HEAD`) no campo `baseline_revision` do `US-XXX-plan.md` e mude o status para `in-progress`.
2. **Etapa RED (Subagente Filho QA via `invoke_subagent`):**
   - Remova qualquer `.tdd-green-lock`.
   - Dispare o subagente `qa-tdd-red` com a skill `05-tdd-red-test-writer`.
   - O subagente cria os testes automatizados + Stubs vazios e comprova a falha esperada no log (**Clean Red**).
3. **Ativação da Trava de Testes (`.tdd-green-lock`):**
   - Crie o arquivo sentinela `.tdd-green-lock` na raiz do projeto antes de chamar os Desenvolvedores.
4. **Etapa GREEN + REFACTOR (Subagente Filho Dev via `invoke_subagent`):**
   - Dispare o `dev-backend-green` e/ou `dev-frontend-green` com a skill `06-tdd-green-refactor-dev`.
   - Os subagentes implementam o código de produção até que 100% dos testes fiquem **GREEN**, realizam a refatoração limpa e executam o Mutation Check.
   - Ao terminar, o status da Story é atualizado para **`built`** (JAMAIS `done`) e remove-se o `.tdd-green-lock`.

### Fase 3: Quality Gate & A Banca dos 5 Revisores (`07-code-reviewer-gate`)
1. Mude o status da Story para `in-review`.
2. Dispare o subagente filho `tech-code-reviewer` via `invoke_subagent` (com `EnableWriteTools: false` - modo Read-Only total) para convocar a **Banca dos 5 Revisores Implacáveis**:
   - 🕵️‍♂️ **O Hacker:** Procura falhas de segurança, vazamento de credenciais, injeções, broken access control e ausência de validação estrita.
   - 🤯 **O Usuário Confuso:** Usa o sistema de forma caótica (duplo clique, race conditions, campos vazios, tipos errados, mensagens de erro vagas).
   - 🧙‍♂️ **O Programador Sênior:** Avalia Clean Code, SOLID, DRY, tipagem estrita e manutenibilidade a longo prazo.
   - 🧪 **O Testador:** Audita cenários cobertos, roda a suíte de testes e aponta testes faltantes e casos de borda.
   - 👑 **O Chefe dos Desenvolvedores:** Analisa os 4 relatórios e emite **UM ÚNICO VEREDITO**: `APROVADO PRA SUBIR` ou `REPROVADO`, com a lista consolidada do mais grave ao menos grave com arquivo e linha.
3. **Loop de Correção:**
   - Se o veredito for `REPROVADO`, a Story volta para `in-progress`, incrementa-se `review_loop_iteration` e o Maestro dispara um subagente filho Dev via `invoke_subagent` para sanar a lista consolidada de apontamentos (reativando `.tdd-green-lock`).
4. Se o veredito for `APROVADO PRA SUBIR`, a Story é promovida para **`done`**, a Matriz de Paridade é marcada como `[X] Paridade OK` e o `specs/kanban-board.md` é atualizado.

### Fase 4: Governança, Living Docs e Commit (`08-living-docs-and-commit`)
1. Acione a skill `08-living-docs-and-commit` para sincronizar o `README.md` e ADRs.
2. Monte a mensagem de commit corporativa com Git Trailers (`Story-Ref`, `Contract-Ref`, `ADR-Ref`) e solicite autorização explícita ao usuário antes de rodar `git commit`.

---

## 3. Gestão de Contexto e Checkpoint de Sessão (`ck`)

Para evitar *Context Rot* em sessões longas ou antes de compactar o chat via `/compact`:
1. **Geração do Checkpoint (`specs/context-checkpoint.md`):**
   - Utilize o template [session-checkpoint-template.md](./references/session-checkpoint-template.md) para registrar o estado condensado da esteira (< 200 tokens).
   - Atualize este snapshot sempre que uma User Story for concluída, antes de pausas no desenvolvimento ou ao sincronizar com o painel (`.agents/painel/`).
2. **Reidratação Instantânea de Sessão:**
   - Ao reiniciar a conversa ou após compactação de contexto, o Maestro lê imediatamente `specs/context-checkpoint.md` para retomar o trabalho a partir do "Próximo Passo Imediato", sem perda de contexto nem alucinação.
