# Snapshot de Sessão (Context Checkpoint)

> **Arquivo:** `specs/context-checkpoint.md`  
> **Propósito:** Snapshot condensado (< 200 tokens) para congelar o estado mental da esteira antes de comandos de compactação (`/compact`), pausas de trabalho ou troca de contexto entre sessões.

---

```markdown
# Context Checkpoint — [Nome do Projeto]

- **Timestamp:** YYYY-MM-DD HH:mm:ss (UTC-3)
- **Modo Atual:** [Marcha 1: Livre | Marcha 2: Fase Isolada | Marcha 3: Esteira Completa]
- **Story Ativa:** [US-XXX: Nome Curto da Story]
- **Fase da Esteira:** [Fase 0: Arquiteto | 1A: Back | 1B: Front | 1C: Kanban | 2A: RED | 2B: GREEN | 3: Review | 4: Commit]
- **Status do Kanban:** [in-progress | built | in-review | done]
- **Git Baseline Revision:** [hash-do-git]

### 1. Estado da Suíte de Testes
- **Testes Backend:** [X passando, Y falhando]
- **Testes Frontend:** [X passando, Y falhando]
- **Trava `.tdd-green-lock`:** [Ativa | Inativa]

### 2. Últimas Decisões & Entregas da Sessão
- [Decisão arquitetural ou componente entregue 1]
- [Decisão arquitetural ou componente entregue 2]

### 3. Próximo Passo Imediato (Ação Determinística)
- [Ação exata que o próximo agente ou sessão deve executar ao reiniciar, ex: "Subagente Dev Frontend implementar View para fazer teste X passar"]
```
