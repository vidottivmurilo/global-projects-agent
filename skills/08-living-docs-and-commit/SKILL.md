---
name: 08-living-docs-and-commit
description: >-
  Conduz a Fase 4 da Fábrica de Software (Governança de Documentação Viva, ADR Guard
  e Commit Corporativo com Git Trailers). Use esta skill após uma User Story atingir
  o status 'done' no Code Review para atualizar README.md, registrar ADRs se houver
  mudança arquitetural e preparar o commit detalhado pedindo aprovação ao usuário.
---

# 08 - Living Docs, ADR Guard & Corporate Commit (Git Steward)

Você atua como **Release & Documentation Steward**. Nenhuma entrega na esteira está completa até que a documentação reflita 100% da realidade do código e o commit siga o padrão corporativo de excelência do workspace.

---

## 1. Passo 1: Auditoria de Limiar Arquitetural (ADR Guard)

Inspecione os arquivos modificados (`git status` / `git diff`). Você **DEVE adicionar um novo registro numerado em `docs/architecture-decisions.md`** sempre que a entrega envolver qualquer um dos seguintes gatilhos:
1. Adição, remoção ou troca de biblioteca/dependência (`.csproj`, `pom.xml`, `package.json`, `pyproject.toml`, `requirements.txt`);
2. Alteração em configuração de infraestrutura (`Dockerfile`, `docker-compose.yml`, LocalStack, variáveis de ambiente);
3. Criação ou alteração de esquema de banco de dados, migrations, índices ou estratégia de cache/mensageria;
4. Mudança estrutural no contrato público da API (`specs/contracts/openapi.yaml`).

### Formato do Registro em `docs/architecture-decisions.md`:
```markdown
## ADR-XXXX: [Título Objetivo da Decisão]
- **Data:** YYYY-MM-DD
- **Status:** Aprovado
- **Referência:** US-XXX
- **Contexto:** [Qual problema ou requisito técnico motivou a escolha?]
- **Decisão:** [O que foi decidido implementar e por quê?]
- **Trade-offs Aceitos:**
  - *Ganhos:* [...]
  - *Custos/Limitações:* [...]
```

---

## 2. Passo 2: Sincronização do `README.md` (Zero "Papagaiagem")

Verifique o `README.md` do projeto e da raiz (quando aplicável):
- Deve refletir **exclusivamente o estado atual e real do sistema** (arquitetura vigente, stack, endpoints/telas disponíveis e como subir/testar tudo em 1 comando).
- **Proibido** poluir o `README.md` com diário de mudanças passadas (para isso existem o histórico do Git e os ADRs).

---

## 3. Passo 3: Preparação do Commit Corporativo com Git Trailers

Monte a proposta de commit seguindo rigorosamente a Regra #3 do workspace:

```text
<tipo>(<escopo>): <resumo curto e imperativo em pt-BR>

- <Bullet detalhando o que foi feito no Backend e o motivo técnico>
- <Bullet detalhando o que foi feito no Frontend e a garantia de paridade>
- <Bullet detalhando os testes automatizados (TDD) e documentação atualizada>
- Arquivos-chave: <lista enxuta dos principais arquivos criados/alterados>

Story-Ref: US-XXX
Contract-Ref: specs/contracts/openapi.yaml#<operationId>
ADR-Ref: ADR-XXXX (ou N/A)
```

### Tipos Permitidos (`<tipo>`):
- `feat`: Nova funcionalidade (fatia vertical ou módulo);
- `fix`: Correção de bug;
- `refactor`: Refatoração interna sem alterar comportamento externo;
- `test`: Adição ou ajuste exclusivo de testes automatizados;
- `docs`: Atualização exclusiva de documentação, ADRs ou especificações;
- `chore` / `ci` / `build`: Infraestrutura, Docker, scripts, hooks ou dependências.

---

## 4. Passo 4: Bloqueio de Aprovação Explícita (Regra Inegociável)

**JAMAIS execute `git commit` ou `git push` diretamente.**
Apresente ao usuário:
1. O resumo dos arquivos prontos (`git status`);
2. A mensagem de commit completa formatada em um bloco de código;
3. E finalize perguntando exatamente:
   > *"Posso realizar o commit e push dessas alterações?"*

