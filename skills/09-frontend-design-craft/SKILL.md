---
name: 09-frontend-design-craft
description: >-
  Diretrizes de excelência em UI/UX corporativo, design tokens, ergonomia de chat
  em tempo real e combate ativo a clichês visuais de IA ("AI slop"). Use esta skill
  ao planejar telas (Fase 1B) ou implementar código de Frontend (Fase 2B) com Vue 3,
  Tailwind CSS e shadcn-vue/Radix.
---

# 09 - Frontend Design Craft & Human UI System

Esta skill estabelece o **padrão de qualidade visual e ergonômico** para todas as interfaces da Fábrica de Software. Sua missão é garantir que o produto final tenha o acabamento, a sobriedade e a densidade de softwares corporativos de classe mundial (como Linear, Slack, Raycast e Vercel), **eliminando completamente a estética genérica de "tela gerada por IA"**.

---

## 1. O Manifesto Anti-Clichê de IA ("Anti-AI-Slop")

Interfaces geradas ingenuamente por modelos de linguagem frequentemente compartilham vícios visuais que denunciam sua origem artificial e prejudicam a usabilidade no mundo real.

### 🚫 Padrões Estritamente Proibidos:
1. **Gradientes Roxos/Cianos Sem Justificativa:** Proibido usar gradientes de fundo coloridos ou botões neon (`bg-gradient-to-r from-purple-500 to-indigo-600`) em sistemas corporativos internos. Use superfícies sólidas, limpas e elegantes.
2. **Cards Flutuantes com Sombras Exageradas:** Proibido usar `shadow-2xl` ou `shadow-xl` soltos sem borda estrutural. O contraste deve vir de bordas sutis (`border border-border` ou `border-white/10`) combinadas com sombras óticas curtas (`shadow-sm` ou `shadow-md`).
3. **Botões de Cápsula Genéricos ("Pill Buttons"):** Evite `rounded-full` em botões principais de ação em interfaces corporativas. Prefira `rounded-md` ou `rounded-lg` (4px a 8px) com padding proporcional.
4. **Falta de Densidade de Informação (Telas Vazias):** Interfaces corporativas não devem gastar 80% da tela com espaço em branco inútil e dois botões gigantes. A densidade de dados deve ser confortável e permitir leitura rápida de listas, status e mensagens.
5. **Animações Lentas e Teatrais:** Evite transições de mais de 200ms que atrasam a produtividade. Microinterações devem durar entre 100ms e 150ms (`ease-out`) apenas para dar fluidez visual, nunca para criar espetáculo.

---

## 2. Sistema de Tokens Semânticos & Cores

Utilize a convenção de tokens semânticos do **Tailwind CSS + shadcn-vue**:

| Token | Propósito | Exemplo Dark Mode | Exemplo Light Mode |
| :--- | :--- | :--- | :--- |
| `background` | Fundo principal da aplicação | `#090D16` / `zinc-950` | `#F8FAFC` / `slate-50` |
| `surface` / `card` | Painéis laterais, modais e containers | `#111827` / `zinc-900` | `#FFFFFF` |
| `border` | Linhas divisórias e contornos | `zinc-800` / `border-white/10` | `slate-200` |
| `foreground` | Texto primário de alta legibilidade | `#F9FAFB` (`zinc-50`) | `#0F172A` (`slate-900`) |
| `muted-foreground` | Metadados, timestamps, hints | `#9CA3AF` (`zinc-400`) | `#64748B` (`slate-500`) |
| `primary` | Cor intencional de ação principal | `#3B82F6` (Azul) ou `#10B981` | `#2563EB` ou `#059669` |
| `destructive` | Ações perigosas e erros críticos | `#EF4444` (`red-500`) | `#DC2626` (`red-600`) |

> **Regra de Ouro:** Escolha **uma única cor de destaque (accent/primary)** para a aplicação inteira. Todo o restante deve ser composto por neutros funcionais bem calibrados.

---

## 3. Ergonomia de Chat em Tempo Real

Aplicações de chat exigem padrões comportamentais específicos consolidados pelo mercado:

### A. Layout e Navegação
- **Estrutura de 2 a 3 Colunas:**
  - **Coluna 1 (Sidebar):** Lista de Canais (`#geral`, `#anuncios`) e Conversas Diretas (DMs), com avatar compacto, indicador de presença e contador de não-lidas discreto.
  - **Coluna 2 (Chat Ativo):** Cabeçalho fixo com nome do canal/pessoa, área de histórico com scroll infinito reverso, e caixa de composição de mensagem fixa na base.
  - **Coluna 3 (Opcional/Gaveta):** Detalhes da sala ou lista de membros online.

### B. Agrupamento de Mensagens (Message Grouping)
- Mensagens consecutivas enviadas pelo **mesmo remetente dentro de um intervalo de 5 minutos** NÃO devem repetir o avatar nem o nome do autor.
- O texto da mensagem subsequente é exibido logo abaixo com espaçamento vertical reduzido (`mt-1` vs `mt-4` entre remetentes diferentes).
- O timestamp exato (ex: `14:32`) é exibido de forma discreta à esquerda ou no hover da mensagem.

### C. Smart Auto-Scroll (Scroll Inteligente)
- Quando uma nova mensagem chega via WebSocket:
  - Se o usuário **já estiver no final da conversa** (distância menor que 150px da base), faça o auto-scroll suave até a mensagem mais recente.
  - Se o usuário estiver **rolando o histórico superior** (lendo mensagens antigas), **NÃO balance a tela**. Mantenha a posição do scroll intacta e exiba um botão flutuante discreto: *"Novas mensagens ↓"*.

### D. Caixa de Composição & Atalhos de Teclado
- Utilizar `textarea` auto-ajustável (que cresce verticalmente até um máximo de 150px antes de ativar scroll interno).
- **Atalhos Obrigatórios:**
  - `Enter`: Envia a mensagem (sem enviar se o texto estiver vazio).
  - `Shift + Enter`: Insere quebra de linha normal.
  - `Esc`: Limpa a mensagem em edição ou fecha popups/modais.
  - `Ctrl + K` / `Cmd + K`: Abre barra de busca global de canais e conversas.

### E. Indicador de Conexão e Presença
- Indicador visual sutil no topo:
  - 🟢 **Conectado:** Discreto (sem alertas barulhentos).
  - 🟡 **Reconectando:** Banner fino no topo com contagem regressiva (`Reconectando em 3s... [Tentar agora]`).
  - 🔴 **Desconectado:** Aviso com botão de reconexão manual.

---

## 4. Checklist de Aceite Visual (Design Quality Gate)

Antes de aprovar qualquer entrega de Frontend no Code Review:
- [ ] A tela segue a paleta de neutros sóbria com apenas 1 cor de destaque?
- [ ] O layout possui densidade adequada para uso corporativo rápido?
- [ ] Os estados de `Loading`, `Empty`, `Error` e `Success` estão implementados com componentes consistentes (Skeletons ao invés de spinners genéricos no meio da tela vazia)?
- [ ] Não há gradientes exagerados ou sombras difusas desnecessárias?
- [ ] Todos os campos de input e botões possuem anel de foco visível (`focus-visible:ring-2`) para navegação por teclado?
