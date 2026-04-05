"""Testes para raw_searcher.py — layout real de raw/ e obras fragmentadas."""
import sys
sys.path.insert(0, "c:/workspace/byblos-obsidian/agents/scripts")

import raw_searcher
from raw_searcher import RawSearcher


class TestRawSearcher:
    def test_busca_em_obra_fragmentada_varre_multiplos_arquivos(self, tmp_path, monkeypatch):
        raw_root = tmp_path / "raw"
        multi_dir = raw_root / "dicionarios-enciclopedias" / "Colecao"
        multi_dir.mkdir(parents=True)
        (multi_dir / "A.txt").write_text("primeira linha\nnada aqui\n", encoding="utf-8")
        (multi_dir / "B.txt").write_text("termo especial\nsegunda linha\n", encoding="utf-8")

        monkeypatch.setattr(raw_searcher, "OBRA_MAP", {
            "TST": {"path": "dicionarios-enciclopedias/Colecao", "nivel": 3},
        })

        searcher = RawSearcher(raw_root)
        hits = searcher.search("especial", siglas=["TST"])

        assert len(hits) == 1
        assert hits[0].file_name == "B.txt"
        assert hits[0].citation_tag == (
            "[Fonte: raw/dicionarios-enciclopedias/Colecao/B.txt | Obra: TST | Nível: 3]"
        )

    def test_busca_em_arquivo_unico_usa_path_exato(self, tmp_path, monkeypatch):
        raw_root = tmp_path / "raw"
        single = raw_root / "dicionarios-enciclopedias" / "single.txt"
        single.parent.mkdir(parents=True)
        single.write_text("Alpha beta gamma\n", encoding="utf-8")

        monkeypatch.setattr(raw_searcher, "OBRA_MAP", {
            "ONE": {"path": "dicionarios-enciclopedias/single.txt", "nivel": 4},
        })

        searcher = RawSearcher(raw_root)
        hits = searcher.search("beta", siglas=["ONE"])

        assert len(hits) == 1
        assert hits[0].obra_path == "dicionarios-enciclopedias"
        assert hits[0].file_name == "single.txt"
        assert searcher.get_citation("ONE", 1) == (
            "[Fonte: raw/dicionarios-enciclopedias/single.txt | Obra: ONE | Nível: 4]"
        )
