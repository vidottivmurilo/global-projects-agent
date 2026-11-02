# 📐 Arquitetura do Painel de Telemetria da Fábrica Multi-Agente

> **Módulo:** `.agents/painel/`  
> **Status:** Ativo / Homologado  
> **Origem / Inspiração:** Adaptado de [cauecarneiro/Overview-Painel](https://github.com/cauecarneiro/Overview-Painel)  

---

## 1. Contexto e Motivação
A esteira corporativa multi-agente opera através de múltiplos papéis especializados (Orquestrador, Arquiteto, Analistas, QA TDD Red, Devs TDD Green, Code Reviewer e Docs Steward) orientados por contratos OpenAPI (`specs/contracts/openapi.yaml`), User Stories atômicas e travas de segurança (`.tdd-green-lock`).

Anteriormente, o acompanhamento de progresso era puramente textual. Este módulo introduz um **painel visual gráfico autônomo, reativo e desacoplado**, que permite ao usuário e aos agentes visualizarem em tempo real:
1. O **Quadro Kanban da Sprint** com status das User Stories e Story Points.
2. O **Estado dos Subagentes** e suas missões atuais.
3. O indicador de **Paridade Full-Stack** (Backend ↔ Frontend).
4. O bloco **"Precisa de Você"** para Quality Gates e decisões humanas.
5. As **Cotas e limites dos modelos** de IA.

---

## 2. Invariantes Técnicas
- **Zero Dependências Externas (Zero-NPM / Zero-Pip):**
  - O coletor utiliza exclusivamente a biblioteca padrão do Python 3.9+ (`http.server`, `json`, `pathlib`, `re`, `argparse`, `unittest`).
  - O frontend é Vanilla HTML5, CSS3 moderno (Custom Properties, Flexbox, CSS Grid) e ES6 nativo.
- **Leitura Segura Local (file:///):**
  - O coletor gera simultaneamente `dados.json` e `dados.js` (com JSONP callback `window.__painelDados`). Isso permite que a página abra instantaneamente no navegador por duplo clique ou `file:///` sem bloqueios de CORS.
- **Gatilho Reativo POST /refresh:**
  - O coletor mantém um servidor HTTP mínimo em `127.0.0.1:7420` escutando exclusivamente `POST /refresh` para acordar a passada sob demanda.
- **Portabilidade Submódulo Git:**
  - Todo o código reside dentro de `.agents/painel/`, garantindo que qualquer projeto que utilize o submodule `.agents` herde o painel imediatamente.

---

## 3. Topologia de Arquivos

```text
.agents/
├── scripts/
│   └── iniciar-painel.ps1          # Launcher PowerShell em 1 comando
└── painel/
    ├── coletor.py                  # Coletor de telemetria das fontes Markdown e Git
    ├── painel-missao.py            # CLI para atualizar status dos agentes
    ├── painel-pendencia.py         # CLI para registrar bloqueios/perguntas
    ├── quadro.json                 # Estado vivo das missões e pendências
    ├── testes/
    │   └── test_coletor.py         # Suíte de testes TDD em Python unittest
    └── publico/
        ├── index.html              # Interface do usuário com Kanban e Agentes
        ├── cartao-apoio.js         # Cálculos de tempo e privacidade
        ├── cotas.js                # Renderizador de cotas
        ├── dados.json              # Gerado em tempo de execução (ignorado no git)
        └── dados.js                # Gerado em tempo de execução (ignorado no git)
```

---

## 4. Como Executar

No PowerShell, na raiz de qualquer projeto com `.agents`:
```powershell
./.agents/scripts/iniciar-painel.ps1
```

Para rodar uma passada única (para testes em CI):
```bash
python .agents/painel/coletor.py --uma-vez
```

Para rodar os testes unitários do painel:
```bash
python -m unittest discover -s .agents/painel/testes
```
