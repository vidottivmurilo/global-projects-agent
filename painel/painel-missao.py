#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Atualiza a missão e a situação de um agente no quadro.json."""

import argparse
import datetime
import json
import os
import sys
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
    parser = argparse.ArgumentParser(description="Atualiza a missão de um agente no painel.")
    parser.add_argument("agente", nargs="?", help="Nome do agente (ex: 'Dev Backend')")
    parser.add_argument("--missao", help="Texto descritivo do que o agente está fazendo")
    parser.add_argument("--situacao", choices=["trabalhando", "ocioso", "esperando"], default="trabalhando")
    parser.add_argument("--frente", default="Esteira", help="Frente de trabalho ou Épico")
    parser.add_argument("--listar", action="store_true", help="Lista as missões atuais")
    parser.add_argument("--limpar", action="store_true", help="Remove a missão do agente")
    parser.add_argument("--quadro", default=str(QUADRO_PADRAO), help="Caminho do quadro.json")
    args = parser.parse_args()

    quadro_path = Path(args.quadro).resolve()
    quadro = carregar_quadro(quadro_path)

    if args.listar:
        if not quadro.get("missoes"):
            print("Nenhuma missão ativa registrada.")
            return 0
        for agente, info in quadro["missoes"].items():
            print(f"- {agente} [{info.get('situacao')}]: {info.get('missao')} ({info.get('frente')})")
        return 0

    if not args.agente:
        parser.error("Informe o nome do agente.")

    if args.limpar:
        quadro.setdefault("missoes", {}).pop(args.agente, None)
        salvar_quadro(quadro_path, quadro)
        print(f"[OK] Missão de '{args.agente}' removida.")
        return 0

    quadro.setdefault("missoes", {})[args.agente] = {
        "missao": args.missao or "Em execução",
        "situacao": args.situacao,
        "frente": args.frente,
        "atualizado_em": datetime.datetime.now(datetime.timezone.utc).isoformat()
    }
    salvar_quadro(quadro_path, quadro)
    print(f"[OK] Missão de '{args.agente}' atualizada para: {args.missao} [{args.situacao}]")
    return 0

if __name__ == "__main__":
    sys.exit(main())
