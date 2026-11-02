import unittest
import os
import json
import tempfile
import sys
from pathlib import Path

# Adiciona o diretório do painel ao sys.path
PAINEL_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PAINEL_DIR))

import coletor

class TestColetorFabrica(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.workspace = Path(self.temp_dir.name)
        self.specs_dir = self.workspace / "specs"
        self.stories_dir = self.specs_dir / "stories"
        self.stories_dir.mkdir(parents=True, exist_ok=True)
        
        # Cria arquivos de teste
        (self.workspace / ".tdd-green-lock").write_text("lock ativo", encoding="utf-8")
        
        (self.specs_dir / "kanban-board.md").write_text("""# Quadro Kanban
| ID | Épico | Título da User Story | Prioridade | Story Points | Escopo (Back/Front) | Contrato (`operationId`) | Status | Loops de Review | Arquivo do Plano |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `US-001` | `EPIC-01` | Criação de Link | `P1` | `3` | `Full-Stack` | `createShortUrl` | `in-progress` | `0` | [US-001-plan.md](./stories/US-001-plan.md) |
| `US-002` | `EPIC-01` | Redirecionamento | `P1` | `3` | `Full-Stack` | `resolveShortUrl` | `done` | `0` | [US-002-plan.md](./stories/US-002-plan.md) |
""", encoding="utf-8")

        (self.specs_dir / "traceability-matrix.md").write_text("""# Matriz
| ID | Operação (`operationId`) | Método HTTP | Rota da API | Componente Frontend Consumidor | Rota Frontend | Status de Paridade |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `M-01` | `createShortUrl` | `POST` | `/api/v1/links` | `UrlShortenerCard.tsx` | `/` | `✅ Coberto 1:1` |
| `M-02` | `resolveShortUrl` | `GET` | `/{shortCode}` | `RedirectHandler.tsx` | `/{shortCode}` | `✅ Coberto 1:1` |
""", encoding="utf-8")

        (self.workspace / "quadro.json").write_text(json.dumps({
            "editado_em": "2026-11-02T14:00:00Z",
            "missoes": {
                "Dev Backend": {"missao": "Codificando US-001", "situacao": "trabalhando"}
            },
            "pendencias": [
                {"id": "p-1", "tipo": "pergunta", "texto": "Aprovar commit?", "recomendacao": "Sim", "criada_em": "2026-11-02T14:00:00Z"}
            ]
        }), encoding="utf-8")

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_ler_trava_tdd(self):
        self.assertTrue(coletor.ler_trava_tdd(self.workspace))
        (self.workspace / ".tdd-green-lock").unlink()
        self.assertFalse(coletor.ler_trava_tdd(self.workspace))

    def test_ler_kanban(self):
        kanban = coletor.ler_kanban(self.specs_dir)
        self.assertEqual(len(kanban["stories"]), 2)
        self.assertEqual(kanban["total_points"], 6)
        self.assertEqual(kanban["done_points"], 3)
        self.assertEqual(kanban["stories"][0]["id"], "US-001")
        self.assertEqual(kanban["stories"][0]["status"], "in-progress")
        self.assertEqual(kanban["stories"][1]["status"], "done")

    def test_ler_paridade(self):
        paridade = coletor.ler_paridade(self.specs_dir / "traceability-matrix.md")
        self.assertEqual(paridade["total_endpoints"], 2)
        self.assertEqual(paridade["cobertos"], 2)
        self.assertEqual(paridade["percentual"], 100)

    def test_ler_stories_individuais(self):
        (self.stories_dir / "US-003-metrics.md").write_text("""---
id: "US-003"
title: "Métricas de Acesso"
points: 5
status: "in-progress"
priority: "P2"
---
# US-003
""", encoding="utf-8")
        stories = coletor.ler_stories_individuais(self.specs_dir)
        self.assertEqual(len(stories), 1)
        self.assertEqual(stories[0]["id"], "US-003")
        self.assertEqual(stories[0]["pontos"], 5)
        self.assertEqual(stories[0]["status"], "in-progress")

    def test_detectar_nome_projeto(self):
        (self.specs_dir / "architecture-spine.md").write_text("# 🏛️ Architecture Spine: Corporate Messenger\n", encoding="utf-8")
        nome = coletor.detectar_nome_projeto(self.workspace)
        self.assertEqual(nome, "Corporate Messenger")

    def test_ler_quadro(self):
        quadro, erro = coletor.ler_quadro(self.workspace / "quadro.json")
        self.assertIsNone(erro)
        self.assertIn("Dev Backend", quadro["missoes"])
        self.assertEqual(len(quadro["pendencias"]), 1)

    def test_montar_e_gravar_dados(self):
        saida_dir = self.workspace / "publico"
        saida_dir.mkdir(parents=True, exist_ok=True)
        
        dados = coletor.montar_dados_esteira(self.workspace, self.workspace / "quadro.json")
        self.assertIn("agentes", dados)
        self.assertIn("kanban", dados)
        self.assertIn("esteira", dados)
        self.assertIn("quadro", dados)
        
        coletor.gravar_dados(dados, saida_dir)
        self.assertTrue((saida_dir / "dados.json").exists())
        self.assertTrue((saida_dir / "dados.js").exists())
        
        conteudo_js = (saida_dir / "dados.js").read_text(encoding="utf-8")
        self.assertTrue(conteudo_js.startswith("window.__painelDados && window.__painelDados("))

if __name__ == "__main__":
    unittest.main()
