---
name: 00-software-factory-orchestrator
description: >-
  Orquestrador central (Maestro) da Fábrica de Software Multi-Agente. Use esta skill
  quando o usuário solicitar a construção estruturada de um projeto, épico ou User Story
  pela esteira (em modo Passo a Passo por Fase ou em modo Esteira Completa), coordenando
  Arquiteto, Analista Back, Analista Front, Gestor de Backlog/Kanban, QA TDD Red,
  Dev Back/Front TDD Green e Code Reviewer.
---

# 00 - Software Factory Orchestrator (Maestro da Esteira)

Esta skill define o protocolo operacional do **Agente Orquestrador (Tech Lead / Controller)** para construir sistemas completos, escaláveis e sem lacunas de escopo entre Backend e Frontend.

---

## 0. Seleção de Cadência (Pergunte ao Usuário ao Iniciar)

Antes de disparar subagentes, confirme com o usuário em qual cadência ele deseja rodar a tarefa atual:
1. **🕹️ Cadência Passo a Passo (Step-Gated — Ideal para estudo e inspeção fina):**
   - Executa **uma fase por vez** (ex: gera apenas o Contrato, ou gera apenas o teste RED, ou roda apenas o Dev Backend), mostra o resultado e **aguarda o "ok"** do usuário para avançar para o próximo passo.
2. **🚀 Cadência por User Story (Story-Gated — Ideal para velocidade após alinhar a Spec):**
   - Após o usuário aprovar o arquivo da User Story (`US-XXX-plan.md`), o Orquestrador coordena automaticamente a sequência `QA RED` -> `Dev GREEN (Back + Front)` -> `Code Review Gate` até a Story atingir `done` (ou parar caso encontre bloqueio).
3. **🎯 Execução de Peça Avulsa:**
   - Se o usuário pediu apenas uma etapa específica (ex: *"roda só o Code Review"* ou *"cria só o teste RED desse bug"*), acione exclusivamente a skill correspondente (`01` a `08`) sem executar o restante do pipeline.

---

## 1. Topologia de Subagentes e Permissões (`define_subagent` / `invoke_subagent`)

Ao acionar a esteira, o Orquestrador DEVE criar ou invocar subagentes com separação estrita de responsabilidades:

| Papel do Subagente | Nome Sugerido (`TypeName`) | `EnableWriteTools` | Skill Obrigatória que o Subagente Deve Ler |
| :--- | :--- | :--- | :--- |
| **Arquiteto de Software** | `architect-agent` | `true` (apenas docs/configs) | `01-architecture-spine-adr` |
| **Analista de Backend & Contratos** | `analyst-backend` | `true` (apenas `specs/`) | `02-analyst-contract-and-back` |
| **Analista de Frontend & Paridade** | `analyst-frontend` | `true` (apenas `specs/`) | `03-analyst-frontend-and-parity`, `09-frontend-design-craft` |
| **Agile & Backlog Manager** | `agile-scrum-master` | `true` (apenas `specs/` e GitHub MCP) | `04-agile-story-sharding` |
| **QA Test Writer (TDD RED)** | `qa-tdd-red` | `true` (apenas `tests/` + stubs) | `05-tdd-red-test-writer` |
| **Dev Backend (TDD GREEN)** | `dev-backend-green` | `true` (bloqueado em `tests/`) | `06-tdd-green-refactor-dev` |
| **Dev Frontend (TDD GREEN)** | `dev-frontend-green` | `true` (bloqueado em `tests/`) | `06-tdd-green-refactor-dev`, `09-frontend-design-craft` |
| **Code Reviewer & Auditor** | `tech-code-reviewer` | **`false` (Read-Only no código!)** | `07-code-reviewer-gate` |
| **Git & Living Docs Steward** | `git-docs-steward` | `true` | `08-living-docs-and-commit` |

---

## 2. Sequência de Execução da Esteira (End-to-End Pipeline)

### Fase 0: Fundação e Arquitetura (`01-architecture-spine-adr`)
1. Conduza o debate socrático com o usuário para definir: Stack/Linguagem, Padrão Arquitetural (Clean Arch, Hexagonal, Vertical Slice, Monólito Modular), Banco de Dados, Mensageria e Infra (`docker-compose.yml`).
2. Gere o `specs/architecture-spine.md`, a estrutura de diretórios semente e o ADR inicial em `docs/architecture-decisions.md`.
3. **Quality Gate 0:** Obtenha o "ok" explícito do usuário antes de avançar para a Fase 1.

### Fase 1: Engenharia de Requisitos, Contratos e Paridade (Paralelismo Controlado)
1. **Passo 1A (Contrato + Análise Backend):** Acione o `analyst-backend` com a skill `02-analyst-contract-and-back` para produzir:
   - Regras de domínio, casos de borda e invariantes de negócio.
   - O contrato explícito da API/Eventos em `specs/contracts/openapi.yaml` (ou schema equivalente) com `operationId` único para cada operação.
2. **Passo 1B (Análise Frontend + Paridade 1:1):** Acione o `analyst-frontend` com a skill `03-analyst-frontend-and-parity` para produzir:
   - Mapeamento de rotas, componentes, estados visuais obrigatórios (`Loading`, `Empty`, `Error`, `Success`).
   - A **Matriz de Rastreabilidade e Paridade (`specs/traceability-matrix.md`)**, garantindo que **100% dos `operationId`s de usuário do Backend possuam tela/componente consumidor no Frontend**.
3. **Passo 1C (Sharding de Stories + Kanban):** Acione o `agile-scrum-master` com a skill `04-agile-story-sharding` para:
   - Fatiar o trabalho em **Vertical Slices** priorizados (`P1 - MVP`, `P2`, `P3`).
   - Criar um arquivo individual por User Story (`specs/stories/US-XXX-plan.md`) respeitando o limite máximo de **900 a 1.300 tokens**, com Story Points (Fibonacci) e bloco `<frozen-after-approval>`.
   - Atualizar o quadro Kanban em `specs/kanban-board.md` (e Issues no GitHub via MCP, se houver repositório remoto configurado).
4. **Quality Gate 1:** Apresente a Matriz de Paridade e o Kanban ao usuário e aguarde o "ok".

### Fase 2: Loop TDD Estrito por User Story (`US-XXX`)
Para cada User Story em ordem de prioridade:
1. **Registro de Baseline:** Grave o hash atual do Git (`git rev-parse HEAD`) no campo `baseline_revision` do `US-XXX-plan.md` e mude o status para `in-progress`.
2. **Etapa RED (`05-tdd-red-test-writer`):**
   - Remova qualquer arquivo `.tdd-green-lock` existente.
   - Acione o subagente `qa-tdd-red` passando **apenas** o arquivo `US-XXX-plan.md` e a referência do contrato.
   - O QA cria os testes automatizados (Backend e/ou Frontend) + **Stubs/Interfaces vazias** (lançando `NotImplementedException` ou equivalente) para que o código compile e falhe na asserção (**Clean Red**).
   - O QA executa a suíte de testes e comprova a falha esperada no log.
   - *(Se estiver na Cadência Passo a Passo, mostre o resultado RED ao usuário e aguarde o "ok" antes de ir para o GREEN).*
3. **Ativação da Trava de Testes (`.tdd-green-lock`):**
   - Crie o arquivo sentinela `.tdd-green-lock` na raiz do projeto antes de acionar os Desenvolvedores. Isso ativa o Hook `PreToolUse` que impede os Devs de editarem arquivos de teste.
4. **Etapa GREEN + REFACTOR (`06-tdd-green-refactor-dev`):**
   - Acione em paralelo (ou em sequência, conforme dependência) o `dev-backend-green` e o `dev-frontend-green`, passando **apenas** o `US-XXX-plan.md`, o contrato e o log do teste falhando.
   - Os Devs implementam o código de produção até que 100% dos testes fiquem **GREEN**, realizam a refatoração limpa e executam o *Mutation Check*.
   - Ao terminar, os Devs atualizam o status da Story para **`built`** (JAMAIS `done`) e removem o `.tdd-green-lock`.

### Fase 3: Quality Gate & Code Review Bifurcado (`07-code-reviewer-gate`)
1. Mude o status da Story para `in-review`.
2. Acione o subagente `tech-code-reviewer` (sem permissão de escrita em código) para auditar o `git diff baseline_revision..HEAD` contra o `US-XXX-plan.md` e a `traceability-matrix.md`.
3. O Reviewer emite dois vereditos:
   - **Spec Compliance Review (`✅` ou `❌`):** Verifica itens faltantes (*Missing*), código não solicitado (*Extra*), testes enfraquecidos e **paridade real Back-Front** (proibido mock esquecido no lugar da chamada real da API).
   - **Code Quality Review (`Approved` ou `Needs Fixes`):** Avalia SOLID, Clean Architecture, segurança e higiene de testes.
4. **Loop de Correção (Circuit Breaker de 5 Rodadas):**
   - Se reprovado (`❌` ou `Needs Fixes` com severidade *Critical* ou *Important*), o status volta para `in-progress`, incrementa-se `review_loop_iteration` e o Dev corrige os apontamentos (reativando `.tdd-green-lock`).
   - **Rodadas 1 a 3:** Mesmo subagente Dev.
   - **Rodadas 4 a 5:** Novo subagente Dev com contexto limpo.
   - **Acima de 5 rodadas:** Interrompa a automação imediatamente e escale para o Usuário (Tech Lead Humano).
5. Se aprovado em ambos os vereditos, o Reviewer promove a Story para **`done`** e atualiza o `specs/kanban-board.md`.

### Fase 4: Governança, Living Docs e Commit (`08-living-docs-and-commit`)
1. Acione a skill `08-living-docs-and-commit` para:
   - Verificar se houve mudança arquitetural que exija novo ADR em `docs/architecture-decisions.md`.
   - Sincronizar o `README.md` com o estado real e atual do projeto.
   - Montar a mensagem de commit corporativa com *Git Trailers* (`Story-Ref`, `Contract-Ref`, `ADR-Ref`) e **pedir autorização explícita ao usuário** antes de rodar `git commit`.

---

## 3. Referências
- Template de Quadro Kanban e Backlog: [kanban-board-template.md](./references/kanban-board-template.md)
