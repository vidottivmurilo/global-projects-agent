#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Gerencia a lista 'Precisa de Você' (perguntas e ações bloqueantes) no quadro.json."""

import argparse
import datetime
import json
import os
import sys
import uuid
from pathlib import Path

PAINEL_DIR = Path(__file__).resolve().parent
QUADRO_PADRAO = PAINEL_DIR / "quadro.json"

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

def carregar_quadro(caminho: Path):
    if not caminho.is_file():
        return {"editado_em": None, "missoes": {}, "pendencias": []}
    try:
        return json.loads(caminho.read_text(encoding="utf-8"))
    except Exception:
        return {"editado_em": None, "missoes": {}, "pendencias": []}

def salvar_quadro(caminho: Path, dados: dict):
    dados["editado_em"] = datetime.datetime.now(datetime.timezone.utc).isoformat().replace("+00:00", "Z")
    caminho.write_text(json.dumps(dados, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

def main():
    parser = argparse.ArgumentParser(description="Gerencia pendências do usuário no painel.")
    parser.add_argument("--pergunta", help="Texto de pergunta objetiva para o usuário")
    parser.add_argument("--recomendacao", help="Recomendação técnica sugerida pelo agente")
    parser.add_argument("--acao", help="Texto de ação que o usuário precisa executar")
    parser.add_argument("--passos", nargs="*", help="Passo a passo da ação (lista de instruções)")
    parser.add_argument("--destrava", help="O que esta ação desbloqueia no projeto")
    parser.add_argument("--listar", action="store_true", help="Lista todas as pendências ativas")
    parser.add_argument("--remover", type=int, help="Número da pendência para remover (1-based)")
    parser.add_argument("--limpar-tudo", action="store_true", help="Remove todas as pendências")
    parser.add_argument("--quadro", default=str(QUADRO_PADRAO), help="Caminho do quadro.json")
    args = parser.parse_args()

    quadro_path = Path(args.quadro).resolve()
    quadro = carregar_quadro(quadro_path)
    pendencias = quadro.setdefault("pendencias", [])

    if args.listar:
        if not pendencias:
            print("Nenhuma pendência ativa para o usuário.")
            return 0
        for i, p in enumerate(pendencias, 1):
            tipo = p.get("tipo", "acao").upper()
            txt = p.get("texto", "")
            rec = f" (Recomendo: {p['recomendacao']})" if p.get("recomendacao") else ""
            print(f"{i}. [{tipo}] {txt}{rec}")
        return 0

    if args.limpar_tudo:
        quadro["pendencias"] = []
        salvar_quadro(quadro_path, quadro)
        print("[OK] Todas as pendências foram removidas.")
        return 0

    if args.remover:
        idx = args.remover - 1
        if 0 <= idx < len(pendencias):
            removida = pendencias.pop(idx)
            salvar_quadro(quadro_path, quadro)
            print(f"[OK] Pendência #{args.remover} removida: {removida.get('texto')}")
            return 0
        else:
            print(f"[ERRO] Índice inválido. Total de pendências: {len(pendencias)}", file=sys.stderr)
            return 1

    if args.pergunta:
        nova = {
            "id": f"p-{uuid.uuid4().hex[:6]}",
            "tipo": "pergunta",
            "texto": args.pergunta.strip(),
            "recomendacao": (args.recomendacao or "Aprovar").strip(),
            "criada_em": datetime.datetime.now(datetime.timezone.utc).isoformat()
        }
        pendencias.append(nova)
        salvar_quadro(quadro_path, quadro)
        print(f"[OK] Pergunta adicionada: {nova['texto']}")
        return 0

    if args.acao:
        nova = {
            "id": f"a-{uuid.uuid4().hex[:6]}",
            "tipo": "acao",
            "texto": args.acao.strip(),
            "destrava": args.destrava,
            "passos": args.passos or [],
            "criada_em": datetime.datetime.now(datetime.timezone.utc).isoformat()
        }
        pendencias.append(nova)
        salvar_quadro(quadro_path, quadro)
        print(f"[OK] Ação adicionada: {nova['texto']}")
        return 0

    parser.print_help()
    return 0

if __name__ == "__main__":
    sys.exit(main())
