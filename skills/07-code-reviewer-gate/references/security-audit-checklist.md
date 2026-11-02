# Checklist de Auditoria de Segurança (OWASP API Top 10 & AgentShield)

Este checklist é a referência técnica obrigatória para o revisor **🕵️‍♂️ O Hacker** na Skill `07-code-reviewer-gate`. Todo item com violação comprovada no diff resulta em **REPROVAÇÃO IMEDIATA** da User Story.

---

## 1. Controle de Acesso e Autorização

- [ ] **BOLA / IDOR (Broken Object Level Authorization):**
  - O código valida se o ID recebido na rota/query pertence ao usuário autenticado?
  - *Exemplo de falha:* `GET /api/v1/orders/:id` sem cláusula `WHERE user_id = current_user.id`.
- [ ] **Mass Assignment (Atribuição em Massa de Propriedades):**
  - O endpoint utiliza schemas estritos (Zod, Pydantic, DTOs explícitos) em vez de repassar o body cru (`req.body`) diretamente para o repositório/banco?
  - Campos sensíveis como `role`, `isAdmin`, `tenantId`, `permissions` ou `balance` são blindados contra alteração via request?
- [ ] **BFLA (Broken Function Level Authorization):**
  - Operações administrativas ou mutações destrutivas (`DELETE`, `PUT`) possuem verificação de permissão no nível de rota e de caso de uso?

---

## 2. Autenticação e Gestão de Sessão

- [ ] **Validação Estrita de Tokens:**
  - Tokens JWT ou cookies de sessão são validados em todas as rotas protegidas?
  - O handshake de WebSockets ou conexões em tempo real exige autenticação antes de aceitar frames de dados?
- [ ] **Zero Hardcoded Credentials:**
  - Não existem chaves de API, segredos, senhas ou tokens mockados em arquivos de código ou de teste que subam para produção.
  - Todas as variáveis sensíveis são injetadas via `.env` ou Secret Managers.

---

## 3. Validação de Entrada e Prevenção de Injeção

- [ ] **Sanitização contra Injeções (SQL, NoSQL, Command Injection):**
  - Todas as consultas ao banco utilizam ORM seguro, parameterized queries ou builders tipados.
  - Comandos do sistema operacional (`exec`, `spawn`, `os.system`) nunca concatenam strings de entrada do usuário.
- [ ] **Prevenção de ReDoS (Regular Expression Denial of Service):**
  - Regexes utilizadas para validar e-mails, URLs ou formatos livres possuem limites de repetição ou proteções contra *catastrophic backtracking*.
- [ ] **Prevenção de SSRF (Server-Side Request Forgery):**
  - Se a aplicação consome ou faz download de URLs fornecidas pelo usuário (webhooks, avatares), valida se o host não aponta para IPs privados (`127.0.0.1`, `localhost`, `169.254.169.254`, `10.0.0.0/8`, `192.168.0.0/16`).

---

## 4. Consumo de Recursos e Resiliência (DoS)

- [ ] **Limites de Payload e Paginação:**
  - Requisições `POST`/`PUT` têm limite de tamanho configurado no parser de body.
  - Endpoints de listagem exigem paginação (`page`, `limit`) com teto máximo (ex: `limit <= 100`).
- [ ] **Prevenção de Ataques de Força Bruta e Spam:**
  - Endpoints públicos de login, registro ou operações caras possuem rate limiting configurado.

---

## 5. Vazamento de Dados e Tratamento de Erros (PII & Info Leak)

- [ ] **Ocultação de Stack Traces e Mensagens Internas:**
  - Em erros 500 ou falhas de infraestrutura, a API retorna apenas uma mensagem segura padronizada (ex: `Internal Server Error`).
  - Stack traces, queries SQL brutas ou detalhes de driver de banco nunca são devolvidos no payload da resposta HTTP.
- [ ] **Mascaramento em Logs (PII Leakage):**
  - Loggers não registram senhas, tokens de autorização (`Bearer ...`), CPFs ou dados financeiros em plain text.
