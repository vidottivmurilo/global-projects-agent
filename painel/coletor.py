#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Coletor de Telemetria da Fábrica de Software Multi-Agente.

Monitora continuamente o workspace sem dependência de tmux:
- Lê o status do Kanban e User Stories em specs/ (stories/*.md e kanban-board.md)
- Lê a paridade Full-Stack em specs/traceability-matrix.md
- Detecta a trava de segurança sentinela .tdd-green-lock
- Monitora missões e pendências do usuário em quadro.json
- Gera dados.json e dados.js atômicos para o dashboard web
- Oferece endpoint loopback POST /refresh em 127.0.0.1:7420
"""

import argparse
import datetime
import http.server
import json
import os
import re
import subprocess
import sys
import threading
import time
from pathlib import Path

# Configura UTF-8 seguro para terminais Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

PORTA_PADRAO = 7420
PAINEL_DIR = Path(__file__).resolve().parent
AGENTS_DIR = PAINEL_DIR.parent
WORKSPACE_PADRAO = AGENTS_DIR.parent

ROLES_ESTEIRA = [
    {"nome": "Maestro / Orquestrador", "skill": "00-software-factory-orchestrator", "ferramenta": "agy", "modelo": "Gemini 3.8 Flash"},
    {"nome": "Arquiteto de Software", "skill": "01-architecture-spine-adr", "ferramenta": "agy", "modelo": "Gemini 3.8 Flash"},
    {"nome": "Analista de Backend", "skill": "02-analyst-contract-and-back", "ferramenta": "agy", "modelo": "Gemini 3.8 Flash"},
    {"nome": "Analista de Frontend", "skill": "03-analyst-frontend-and-parity", "ferramenta": "agy", "modelo": "Gemini 3.8 Flash"},
    {"nome": "Agile Scrum Master", "skill": "04-agile-story-sharding", "ferramenta": "agy", "modelo": "Gemini 3.8 Flash"},
    {"nome": "QA Test Writer (RED)", "skill": "05-tdd-red-test-writer", "ferramenta": "agy", "modelo": "Gemini 3.8 Flash"},
    {"nome": "Dev Backend (GREEN)", "skill": "06-tdd-green-refactor-dev", "ferramenta": "agy", "modelo": "Gemini 3.8 Flash"},
    {"nome": "Dev Frontend (GREEN)", "skill": "06-tdd-green-refactor-dev", "ferramenta": "agy", "modelo": "Gemini 3.8 Flash"},
    {"nome": "Code Reviewer & Gate", "skill": "07-code-reviewer-gate", "ferramenta": "agy", "modelo": "Gemini 3.8 Flash"},
    {"nome": "Git & Docs Steward", "skill": "08-living-docs-and-commit", "ferramenta": "agy", "modelo": "Gemini 3.8 Flash"}
]

def iso_agora():
    return datetime.datetime.now(datetime.timezone.utc).isoformat().replace("+00:00", "Z")

def ler_trava_tdd(workspace: Path) -> bool:
    lock_file = workspace / ".tdd-green-lock"
    return lock_file.is_file()

def detectar_nome_projeto(workspace: Path) -> str:
    # 1. Tenta extrair de specs/architecture-spine.md
    spine = workspace / "specs" / "architecture-spine.md"
    if spine.is_file():
        try:
            for l in spine.read_text(encoding="utf-8").splitlines():
                if l.startswith("#") and ":" in l:
                    nome = l.split(":", 1)[1].strip()
                    if nome:
                        return nome
        except Exception:
            pass
    # 2. Tenta extrair de package.json
    pkg = workspace / "package.json"
    if pkg.is_file():
        try:
            dados = json.loads(pkg.read_text(encoding="utf-8"))
            if "name" in dados:
                return dados["name"].replace("-", " ").title()
        except Exception:
            pass
    return workspace.name.replace("-", " ").title()

def ler_stories_individuais(specs_dir: Path) -> list:
    stories_dir = specs_dir / "stories"
    stories = []
    if not stories_dir.is_dir():
        return stories
    
    for f in sorted(stories_dir.glob("US-*.md")):
        try:
            conteudo = f.read_text(encoding="utf-8")
            match = re.search(r"^---\s*\n(.*?)\n---", conteudo, re.DOTALL | re.MULTILINE)
            if not match:
                continue
            bloco = match.group(1)
            meta = {}
            for linha in bloco.splitlines():
                if ":" in linha:
                    k, v = linha.split(":", 1)
                    meta[k.strip()] = v.strip().strip('"').strip("'")
            
            s_id = meta.get("id") or f.stem.split("-")[0]
            titulo = meta.get("title") or f.stem
            try:
                pts = int(re.sub(r"[^\d]", "", meta.get("points", "0")))
            except (ValueError, TypeError):
                pts = 0
            status = meta.get("status", "backlog").strip()
            contrato = meta.get("contract_ref", "")
            
            stories.append({
                "id": s_id,
                "epic": meta.get("epic", "EPIC-01"),
                "titulo": titulo,
                "prioridade": meta.get("priority", "P1 (MVP)"),
                "pontos": pts,
                "escopo": meta.get("scope", "Full-Stack"),
                "contrato": contrato,
                "status": status,
                "reviews": meta.get("reviews", "0"),
                "arquivo": f.name
            })
        except Exception:
            continue
    return stories

def ler_kanban(specs_dir: Path) -> dict:
    kanban_file = specs_dir / "kanban-board.md"
    stories_map = {}
    
    # 1. Lê stories dos arquivos individuais (fonte da verdade de frontmatter)
    for s in ler_stories_individuais(specs_dir):
        stories_map[s["id"]] = s
    
    # 2. Lê quadro kanban-board.md
    if kanban_file.is_file():
        try:
            texto = kanban_file.read_text(encoding="utf-8")
            linhas = texto.splitlines()
            for l in linhas:
                l = l.strip()
                if not l.startswith("|") or ":---" in l or "Título da User Story" in l or ("Título" in l and "ID" in l):
                    continue
                partes = [p.strip().replace("`", "").replace("**", "") for p in l.split("|")[1:-1]]
                if len(partes) >= 3:
                    s_id = partes[0].strip()
                    if not re.match(r"^US-\d{2,4}$", s_id):
                        continue
                    
                    if len(partes) >= 8:
                        epic = partes[1]
                        titulo = partes[2]
                        prio = partes[3]
                        try:
                            pts = int(re.sub(r"[^\d]", "", partes[4]))
                        except (ValueError, TypeError):
                            pts = 0
                        escopo = partes[5]
                        contrato = partes[6]
                        status = partes[7]
                        reviews = partes[8] if len(partes) > 8 else "0"
                        arquivo = partes[9] if len(partes) > 9 else f"{s_id}-plan.md"
                    else:
                        # Tabela simplificada
                        epic = "EPIC-01"
                        titulo = partes[1]
                        try:
                            pts = int(re.sub(r"[^\d]", "", partes[2]))
                        except (ValueError, TypeError):
                            pts = 0
                        prio = "P1 (MVP)"
                        escopo = partes[3] if len(partes) > 3 else "Full-Stack"
                        contrato = ""
                        status = partes[4] if len(partes) > 4 and partes[4] in ("done", "built", "in-progress", "ready", "backlog") else "ready-for-dev"
                        reviews = "0"
                        arquivo = partes[-1] if len(partes) > 4 else f"{s_id}-plan.md"
                    
                    story_existente = stories_map.get(s_id, {})
                    stories_map[s_id] = {
                        "id": s_id,
                        "epic": epic or story_existente.get("epic", "EPIC-01"),
                        "titulo": titulo or story_existente.get("titulo", s_id),
                        "prioridade": prio or story_existente.get("prioridade", "P1 (MVP)"),
                        "pontos": pts or story_existente.get("pontos", 0),
                        "escopo": escopo or story_existente.get("escopo", "Full-Stack"),
                        "contrato": contrato or story_existente.get("contrato", ""),
                        "status": story_existente.get("status") or status,
                        "reviews": reviews or story_existente.get("reviews", "0"),
                        "arquivo": arquivo or story_existente.get("arquivo", f"{s_id}-plan.md")
                    }
        except Exception:
            pass

    stories = list(stories_map.values())
    stories.sort(key=lambda s: s["id"])
    
    total_points = sum(s["pontos"] for s in stories)
    done_points = sum(s["pontos"] for s in stories if s["status"].lower() in ("done", "completed", "concluido", "concluído"))

    colunas = {
        "backlog": [s for s in stories if s["status"].lower() in ("ready-for-dev", "backlog", "draft", "ready", "todo")],
        "in_progress": [s for s in stories if s["status"].lower() in ("in-progress", "in_progress", "progress")],
        "built": [s for s in stories if s["status"].lower() in ("built", "build")],
        "in_review": [s for s in stories if s["status"].lower() in ("in-review", "review", "in_review")],
        "done": [s for s in stories if s["status"].lower() in ("done", "completed", "concluido", "concluído")]
    }
    
    return {
        "stories": stories,
        "total_stories": len(stories),
        "done_stories": len(colunas["done"]),
        "total_points": total_points,
        "done_points": done_points,
        "colunas": colunas
    }

def ler_paridade(traceability_file: Path) -> dict:
    if not traceability_file.is_file():
        return {"total_endpoints": 0, "cobertos": 0, "percentual": 0}
    try:
        texto = traceability_file.read_text(encoding="utf-8")
        linhas = [l.strip() for l in texto.splitlines() if l.strip().startswith("|") and not ":---" in l and not "operationId" in l and not "Requisito" in l]
        total = 0
        cobertos = 0
        for l in linhas:
            partes = [p.strip().replace("`", "") for p in l.split("|")[1:-1]]
            if len(partes) >= 5:
                primeiro = partes[0]
                if (primeiro.startswith("FR-") or primeiro.startswith("M-") or 
                    any(m in l for m in ("GET", "POST", "PUT", "DELETE", "PATCH", "WS:", "REST", "UI Component", "Widget"))):
                    total += 1
                    status_paridade = partes[-1].lower()
                    if any(ok in status_paridade for ok in ("✅", "coberto", "paridade ok", "[x]", "planejado", "implementado", "ok")):
                        cobertos += 1
        pct = int(round((cobertos / total) * 100)) if total > 0 else 100
        return {"total_endpoints": total, "cobertos": cobertos, "percentual": pct}
    except Exception:
        return {"total_endpoints": 0, "cobertos": 0, "percentual": 0}

def ler_quadro(quadro_file: Path):
    if not quadro_file.is_file():
        return {"editado_em": None, "missoes": {}, "pendencias": []}, None
    try:
        dados = json.loads(quadro_file.read_text(encoding="utf-8"))
        if not isinstance(dados, dict):
            return {"editado_em": None, "missoes": {}, "pendencias": []}, "formato inválido"
        dados.setdefault("missoes", {})
        dados.setdefault("pendencias", [])
        return dados, None
    except Exception as e:
        return {"editado_em": None, "missoes": {}, "pendencias": []}, str(e)

def ler_cotas_antigravity():
    try:
        res = subprocess.run(["agy", "-p", "/quota", "--output-format", "json"],
                             capture_output=True, text=True, timeout=5)
        if res.returncode == 0 and res.stdout.strip():
            return json.loads(res.stdout)
    except Exception:
        pass
    return None

def montar_dados_esteira(workspace: Path, quadro_file: Path, cotas_data: dict = None) -> dict:
    specs_dir = workspace / "specs"
    lock_ativo = ler_trava_tdd(workspace)
    kanban = ler_kanban(specs_dir)
    paridade = ler_paridade(specs_dir / "traceability-matrix.md")
    quadro, erro_quadro = ler_quadro(quadro_file)
    nome_projeto = detectar_nome_projeto(workspace)
    
    # Determina fase atual do pipeline
    if lock_ativo:
        fase_atual = "Fase 2B: TDD GREEN & REFACTOR (Desenvolvimento Ativo)"
    elif len(kanban["colunas"]["in_review"]) > 0:
        fase_atual = "Fase 3: Code Review & Quality Gate"
    elif len(kanban["colunas"]["in_progress"]) > 0:
        fase_atual = "Fase 2: Execução de User Story (TDD)"
    elif kanban["done_stories"] == kanban["total_stories"] and kanban["total_stories"] > 0:
        fase_atual = "Fase 4: Concluído / Living Docs & Commit"
    else:
        fase_atual = "Fase 1: Especificação & Planejamento"

    # Monta agentes
    agentes = []
    for r in ROLES_ESTEIRA:
        nome = r["nome"]
        m = quadro["missoes"].get(nome, {})
        estado = m.get("situacao", "ocioso")
        
        # Ajuste dinâmico se estiver no lock TDD
        if lock_ativo and "Dev" in nome:
            estado = "trabalhando"
        elif lock_ativo and "QA" in nome:
            estado = "ocioso"
            
        agentes.append({
            "nome": nome,
            "papel": r["skill"],
            "ferramenta": r["ferramenta"],
            "ferramenta_nome": "Antigravity",
            "modelo": r["modelo"],
            "modelo_lido_da_tela": True,
            "esforco": "high",
            "conta": "default",
            "leitura": "ok",
            "motivo": None,
            "estado": estado,
            "atividade": m.get("missao") or ("Implementando código GREEN" if estado == "trabalhando" else None),
            "ultima_fala": None,
            "contexto_pct": 25,
            "sessao_5h_pct": 18,
            "semanal_pct": 12,
            "missao": {
                "texto": m.get("missao") or ("Em execução" if estado == "trabalhando" else "Aguardando próxima etapa"),
                "situacao": estado,
                "frente": m.get("frente") or nome_projeto
            },
            "prs": []
        })

    momento = datetime.datetime.now(datetime.timezone.utc)
    
    return {
        "versao": 1,
        "gerado_em": iso_agora(),
        "gerado_em_epoch": int(momento.timestamp()),
        "intervalo_s": 5,
        "origem": "esteira",
        "esteira": {
            "fase_atual": fase_atual,
            "lock_ativo": lock_ativo,
            "paridade": paridade,
            "kanban_resumo": {
                "total_stories": kanban["total_stories"],
                "done_stories": kanban["done_stories"],
                "total_points": kanban["total_points"],
                "done_points": kanban["done_points"],
                "progresso_pct": int(round((kanban["done_points"] / kanban["total_points"]) * 100)) if kanban["total_points"] > 0 else 0
            }
        },
        "kanban": kanban,
        "agentes": agentes,
        "cotas": {},
        "contas": {
            "consultadas": cotas_data is not None,
            "erro": None,
            "lista": cotas_data.get("accounts", []) if cotas_data else []
        },
        "sonda": {"ligada": False, "contas": []},
        "prs": {
            "consultado": False,
            "lido_em_epoch": None,
            "erro": None,
            "intervalo_s": 180,
            "total": 0,
            "sem_dono": []
        },
        "quadro": {
            "editado_em": quadro.get("editado_em"),
            "erro": erro_quadro,
            "pendencias": quadro.get("pendencias", [])
        },
        "frentes": [
            {
                "nome": nome_projeto,
                "membros": [{"nome": a["nome"], "situacao": a["estado"]} for a in agentes if a["estado"] in ("trabalhando", "esperando")]
            }
        ]
    }

def gravar_dados(dados: dict, saida_dir: Path):
    saida_dir = Path(saida_dir)
    saida_dir.mkdir(parents=True, exist_ok=True)
    
    json_path = saida_dir / "dados.json"
    js_path = saida_dir / "dados.js"
    
    temp_json = saida_dir / "dados.json.tmp"
    temp_js = saida_dir / "dados.js.tmp"
    
    raw_json = json.dumps(dados, ensure_ascii=False, indent=2) + "\n"
    raw_js = f"window.__painelDados && window.__painelDados({json.dumps(dados, ensure_ascii=True)});\n"
    
    temp_json.write_text(raw_json, encoding="utf-8")
    temp_js.write_text(raw_js, encoding="utf-8")
    
    temp_json.replace(json_path)
    temp_js.replace(js_path)

class HandlerRefresh(http.server.BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass

    def do_POST(self):
        if self.path != "/refresh":
            self.send_response(404)
            self.end_headers()
            return
        if hasattr(self.server, "evento_refresh"):
            self.server.evento_refresh.set()
        self.send_response(204)
        self.end_headers()

    def do_GET(self):
        if self.path == "/refresh":
            self.send_response(405)
        else:
            self.send_response(404)
        self.end_headers()

def iniciar_servidor_http(porta: int, evento_refresh: threading.Event):
    try:
        servidor = http.server.HTTPServer(("127.0.0.1", porta), HandlerRefresh)
        servidor.evento_refresh = evento_refresh
        t = threading.Thread(target=servidor.serve_forever, daemon=True)
        t.start()
        return servidor
    except Exception as e:
        print(f"coletor: aviso: servidor HTTP na porta {porta} falhou ({e})", file=sys.stderr)
        return None

def main():
    parser = argparse.ArgumentParser(description="Coletor de Telemetria da Fábrica de Software")
    parser.add_argument("--uma-vez", action="store_true", help="Executa uma única passada e sai")
    parser.add_argument("--intervalo", type=int, default=3, help="Intervalo em segundos entre passadas (padrão: 3s)")
    parser.add_argument("--porta", type=int, default=PORTA_PADRAO, help="Porta do servidor HTTP /refresh")
    parser.add_argument("--workspace", type=str, default=str(WORKSPACE_PADRAO), help="Caminho raiz do workspace")
    parser.add_argument("--quadro", type=str, default=str(PAINEL_DIR / "quadro.json"), help="Caminho do quadro.json")
    parser.add_argument("--saida", type=str, default=str(PAINEL_DIR / "publico"), help="Pasta de saída dos dados")
    args = parser.parse_args()

    workspace = Path(args.workspace).resolve()
    quadro_file = Path(args.quadro).resolve()
    saida_dir = Path(args.saida).resolve()

    evento_refresh = threading.Event()
    if not args.uma_vez:
        iniciar_servidor_http(args.porta, evento_refresh)
        print(f"[PAINEL] Coletor ativo | Workspace: {workspace.name} | Atualizando a cada {args.intervalo}s", flush=True)

    while True:
        try:
            dados = montar_dados_esteira(workspace, quadro_file)
            gravar_dados(dados, saida_dir)
            if args.uma_vez:
                print(f"[OK] Passada concluída: dados gravados em {saida_dir / 'dados.json'}")
                return 0
        except Exception as e:
            print(f"Erro na passada do coletor: {e}", file=sys.stderr, flush=True)
            if args.uma_vez:
                return 1

        evento_refresh.wait(timeout=args.intervalo)
        evento_refresh.clear()

if __name__ == "__main__":
    sys.exit(main())
