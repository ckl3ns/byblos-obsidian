"""Testes para graph_builder.py — bidirecionalidade, deduplicação e métricas."""
import sys
from types import SimpleNamespace
sys.path.insert(0, "c:/workspace/byblos-obsidian/agents/scripts")

from graph_builder import (
    _build_edges_from_ref, _deduplicate_edges, _edge_type_from_ref, _book, build_graph,
)
from ntsk_parser import NTSKRef


class TestBookHelper:
    """_book() extrai a sigla do livro de um ID de versículo."""

    def test_book_de_mt_1_1(self):
        assert _book("Mt 1.1") == "Mt"

    def test_book_de_gn_2_4(self):
        assert _book("Gn 2.4") == "Gn"

    def test_book_vazio(self):
        assert _book("") == ""


class TestEdgeTypeFromRef:
    """_edge_type_from_ref deriva o tipo canônico a partir dos símbolos."""

    def test_star_eh_especially_clear(self):
        ref = NTSKRef("", "Mt", "Mt", "1", ["1"], ["*"], [])
        assert _edge_type_from_ref(ref) == "especially_clear"

    def test_plus_eh_full_collection(self):
        ref = NTSKRef("", "Gn", "Gn", "13", ["8"], ["+"], [])
        assert _edge_type_from_ref(ref) == "full_collection"

    def test_sem_simbolo_eh_cross_ref(self):
        ref = NTSKRef("", "Mt", "Mt", "1", ["1"], [], [])
        assert _edge_type_from_ref(ref) == "cross_ref"

    def test_multiplos_toma_primeiro_especifico(self):
        ref = NTSKRef("", "Gn", "Gn", "22", ["18"], ["*", "+", "\u2721"], [])
        # * tem prioridade (primeiro no EDGE_TYPE_MAP)
        assert _edge_type_from_ref(ref) == "especially_clear"


class TestBuildEdgesFromRef:
    """_build_edges_from_ref gera um par (forward + inverse) por versículo."""

    def test_gera_par_forward_e_inverse(self):
        ref = NTSKRef("", "Mt", "Mt", "1", ["1"], ["*"], [])
        edges = _build_edges_from_ref("Gn 2.4", ref)
        assert len(edges) == 2
        fwd = [e for e in edges if e["direction"] == "forward"][0]
        inv = [e for e in edges if e["direction"] == "inverse"][0]
        assert fwd["source"] == "Gn 2.4"
        assert fwd["target"] == "Mt 1.1"
        assert fwd["inferred"] is False
        assert inv["source"] == "Mt 1.1"
        assert inv["target"] == "Gn 2.4"
        assert inv["inferred"] is True

    def test_forward_tem_book_correto(self):
        ref = NTSKRef("", "Gn", "Gn", "2", ["4"], [], [])
        edges = _build_edges_from_ref("Mt 1.1", ref)
        fwd = [e for e in edges if e["direction"] == "forward"][0]
        assert fwd["target_book"] == "Gn"
        assert fwd["source_book"] == "Mt"

    def test_edge_type_preservado_na_inversa(self):
        ref = NTSKRef("", "Mt", "Mt", "9", ["27"], ["*"], [])
        edges = _build_edges_from_ref("Mt 1.1", ref)
        for e in edges:
            assert e["edge_type"] == "especially_clear"

    def test_livro_nao_mapeado_nao_gera_edges(self):
        ref = NTSKRef("", "XYZ", None, "1", ["1"], [], [])
        edges = _build_edges_from_ref("Mt 1.1", ref)
        assert edges == []


class TestDeduplicacao:
    """_deduplicate_edges agrega por (source, target, direction)."""

    def test_duplicata_exata_removida(self):
        edges = [
            {"source": "A", "target": "B", "edge_type": "cross_ref",
             "symbols": [], "direction": "forward"},
            {"source": "A", "target": "B", "edge_type": "cross_ref",
             "symbols": [], "direction": "forward"},
        ]
        deduped = _deduplicate_edges(edges)
        assert len(deduped) == 1

    def test_mesmo_par_direcoes_diferentes_ambos_preservados(self):
        edges = [
            {"source": "A", "target": "B", "edge_type": "cross_ref",
             "symbols": [], "direction": "forward"},
            {"source": "B", "target": "A", "edge_type": "cross_ref",
             "symbols": [], "direction": "inverse"},
        ]
        deduped = _deduplicate_edges(edges)
        assert len(deduped) == 2

    def test_simbolos_agregados_em_duplicata(self):
        """Se mesmo par aparece com [] e depois com ['*'], agrega em ['*']."""
        edges = [
            {"source": "A", "target": "B", "edge_type": "cross_ref",
             "symbols": [], "direction": "forward"},
            {"source": "A", "target": "B", "edge_type": "cross_ref",
             "symbols": ["*"], "direction": "forward"},
        ]
        deduped = _deduplicate_edges(edges)
        assert len(deduped) == 1
        assert "*" in deduped[0]["symbols"]

    def test_tipo_nao_cross_ref_preservado_sobre_cross_ref(self):
        """Se um par aparece como cross_ref e depois como especially_clear,
        o não-cross_ref tem prioridade."""
        edges = [
            {"source": "A", "target": "B", "edge_type": "cross_ref",
             "symbols": [], "direction": "forward"},
            {"source": "A", "target": "B", "edge_type": "especially_clear",
             "symbols": ["*"], "direction": "forward"},
        ]
        deduped = _deduplicate_edges(edges)
        assert deduped[0]["edge_type"] == "especially_clear"
        assert "*" in deduped[0]["symbols"]

    def test_multiplos_tipos_nao_cross_ref_agregados(self):
        """Tipos específicos diferentes são unidos com '; '."""
        edges = [
            {"source": "A", "target": "B", "edge_type": "especially_clear",
             "symbols": ["*"], "direction": "forward"},
            {"source": "A", "target": "B", "edge_type": "full_collection",
             "symbols": ["+"], "direction": "forward"},
        ]
        deduped = _deduplicate_edges(edges)
        assert "especially_clear" in deduped[0]["edge_type"]
        assert "full_collection" in deduped[0]["edge_type"]
        assert "*" in deduped[0]["symbols"]
        assert "+" in deduped[0]["symbols"]


class TestBidirectionalIntegrity:
    """Para cada aresta forward, existe uma aresta inversa correspondente."""

    def test_forward_e_inverse_sao_mutuamente_inversas(self):
        ref = NTSKRef("", "Mt", "Mt", "1", ["1"], ["*"], [])
        edges = _deduplicate_edges(_build_edges_from_ref("Gn 2.4", ref))
        fwd = [e for e in edges if e["direction"] == "forward"][0]
        inv = [e for e in edges if e["direction"] == "inverse"][0]
        assert fwd["source"] == inv["target"]
        assert fwd["target"] == inv["source"]
        assert inv["inferred"] is True
        assert fwd["inferred"] is False


def _verse_node(
    referencia: str,
    sigla: str,
    livro: str,
    capitulo: int,
    versiculo: int,
    ntsk_raw: str | None = None,
):
    return SimpleNamespace(
        node_type="versiculo",
        referencia=referencia,
        sigla=sigla,
        livro=livro,
        capitulo=capitulo,
        versiculo=versiculo,
        testamento="NT",
        canon_cristao="NT",
        ntsk_raw=ntsk_raw,
    )


class TestBuildGraph:
    """build_graph deve incluir todos os versículos como nós."""

    def test_verse_without_ntsk_appears_as_node_with_zero_refs(self):
        nodes = [
            _verse_node("Gn 1.1", "Gn", "Gênesis", 1, 1, "Jn 3:16."),
            _verse_node("Jo 3.16", "Jo", "João", 3, 16, None),
        ]

        graph = build_graph(nodes)

        metas = {n["id"]: n for n in graph["nodes"]}
        assert len(graph["nodes"]) == 2
        assert metas["Jo 3.16"]["ref_count"] == 0
        assert metas["Jo 3.16"]["strong_h"] == []
        assert metas["Jo 3.16"]["strong_g"] == []

    def test_valid_target_without_ntsk_is_not_unresolved(self):
        nodes = [
            _verse_node("Gn 1.1", "Gn", "Gênesis", 1, 1, "Jn 3:16."),
            _verse_node("Jo 3.16", "Jo", "João", 3, 16, None),
        ]

        graph = build_graph(nodes)

        assert "Jo 3.16" not in graph["stats"]["unresolved_targets"]
        assert graph["stats"]["unresolved_count"] == 0

    def test_truly_invalid_target_remains_unresolved(self):
        nodes = [
            _verse_node("Gn 1.1", "Gn", "Gênesis", 1, 1, "Mt 99:99."),
            _verse_node("Jo 3.16", "Jo", "João", 3, 16, None),
        ]

        graph = build_graph(nodes)

        assert "Mt 99.99" in graph["stats"]["unresolved_targets"]
        assert graph["stats"]["unresolved_count"] == 1
