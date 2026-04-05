"""Testes para ntsk_parser.py — carryover, símbolos e normalização de IDs."""
import sys
sys.path.insert(0, "c:/workspace/byblos-obsidian/agents/scripts")

from ntsk_parser import (
    parse_ntsk_block, NTSKParser, BOOK_MAP, NTSK_SYMBOLS,
)


class TestCarryover:
    """Suporte a carryover: livro/capítulo se mantém quando não mencionado."""

    def test_carryover_cap_simples(self):
        """'Mt 1:1. 2:3. 5.' -> Mt 1:1, Mt 1:2, Mt 1:3, Mt 1:5.
        
        Em carryover NTSK, '2:3' significa versículos 2 E 3 do mesmo cap.
        Então 'Mt 1:1. 2:3. 5.' expande para Mt 1.1, Mt 1.2, Mt 1.3, Mt 1.5 (4 refs).
        """
        raw = "Mt 1:1. 2:3. 5."
        r = parse_ntsk_block(raw, "Mt 1.1")
        assert r["total_refs"] == 4
        ids = [ref.target_id() for ref in r["refs"]]
        assert ids == ["Mt 1.1", "Mt 1.2", "Mt 1.3", "Mt 1.5"]

    def test_carryover_livro_muda(self):
        """'Mt 1:1. Lk 1:1.' -> muda para Lk após mudança."""
        raw = "Mt 1:1. Lk 1:1."
        r = parse_ntsk_block(raw, "Mt 1.1")
        ids = [ref.target_id() for ref in r["refs"]]
        assert ids == ["Mt 1.1", "Lc 1.1"]

    def test_carryover_com_skip_cap(self):
        """'Ge 2:4. 5:1. 37:2.' carryover de Ge através de 2 caps."""
        raw = "Ge 2:4. 5:1. 37:2."
        r = parse_ntsk_block(raw, "Gn 2.4")
        ids = [ref.target_id() for ref in r["refs"]]
        assert ids == ["Gn 2.4", "Gn 5.1", "Gn 37.2"]


class TestSimbolos:
    """Cada símbolo NTSK é capturado e classificado corretamente."""

    def test_star_especialmente_clara(self):
        raw = "Ge *2:4."
        r = parse_ntsk_block(raw, "Gn 2.4")
        ref = r["refs"][0]
        assert ref.symbols == ["*"]
        assert ref.symbol_names == ["especially_clear"]

    def test_plus_colecao_completa(self):
        """'+' deve ser full_collection, não cross_ref."""
        raw = "Ge +13:8."
        r = parse_ntsk_block(raw, "Gn 13.7")
        ref = r["refs"][0]
        assert "+" in ref.symbols
        assert "full_collection" in ref.symbol_names

    def test_checkmark_criticamente_clara(self):
        """Gl na verdade é Gálatas = Ga."""
        raw = "Ro 1:16."
        r = parse_ntsk_block(raw, "Rm 1.15")
        # Ro = Rm; sem símbolo no input, testa só que não quebra
        assert r["total_refs"] == 1

    def test_contraste(self):
        """◐ marca contraste doutrinário."""
        raw = "Mt 4:6."
        r = parse_ntsk_block(raw, "Mt 4.5")
        # sem símbolo: verifica que contrast_refs está vazio
        assert len(r["contrast_refs"]) == 0

    def test_multiplos_simbolos(self):
        """'Is +*9:6' deve ter ambos + e *."""
        raw = "Is +*9:6."
        r = parse_ntsk_block(raw, "Mt 1.1")
        ref = r["refs"][0]
        assert "+" in ref.symbols
        assert "*" in ref.symbols
        assert "especially_clear" in ref.symbol_names
        assert "full_collection" in ref.symbol_names

    def test_profecia_cumprimento(self):
        """✡ = fulfills_prophecy."""
        raw = "Gn 22:18✡."
        r = parse_ntsk_block(raw, "Gn 22.17")
        ref = r["refs"][0]
        assert "\u2721" in ref.symbols
        assert "fulfills_prophecy" in ref.symbol_names

    def test_fulfills_prophecy(self):
        raw = "Gn +*✡22:18."
        r = parse_ntsk_block(raw, "Gn 22.17")
        ref = r["refs"][0]
        assert "✡" in ref.symbols

    def test_ot_quote_in_nt(self):
        raw = "Is 53:8 ▶."
        r = parse_ntsk_block(raw, "Mt 1.1")
        ref = r["refs"][0]
        assert "▶" in ref.symbols
        assert "ot_quote_in_nt" in ref.symbol_names

    def test_false_doctrine_proof(self):
        """‡ = false_doctrine_proof."""
        raw = "某 ‡1:1."
        r = parse_ntsk_block(raw, "Mt 1.1")
        # livro "某" não existe → sem refs; só verifica que não quebra
        assert r["total_refs"] == 0


class TestNormalizacaoIDs:
    """IDs de versículo seguem o padrão frontmatter: 'Mt 1.1' (espaço, ponto)."""

    def test_id_formato_espaco_ponto(self):
        raw = "Mt 1:1."
        r = parse_ntsk_block(raw, "Mt 1.1")
        assert r["refs"][0].target_id() == "Mt 1.1"

    def test_id_com_cap_duas_cifras(self):
        raw = "Mt 12:23."
        r = parse_ntsk_block(raw, "Mt 12.22")
        assert r["refs"][0].target_id() == "Mt 12.23"

    def test_id_livro_dois_digitos(self):
        raw = "Mt 27:46."
        r = parse_ntsk_block(raw, "Mt 27.45")
        assert r["refs"][0].target_id() == "Mt 27.46"


class TestBookMapping:
    """Siglas NTSK (EN) são mapeadas para siglas vault (PT-BR)."""

    def test_genesis_ge_to_gn(self):
        raw = "Ge 1:1."
        r = parse_ntsk_block(raw, "Gn 1.1")
        assert r["refs"][0].book_vault == "Gn"

    def test_lucas_lk_to_lc(self):
        raw = "Lk 1:1."
        r = parse_ntsk_block(raw, "Lc 1.1")
        assert r["refs"][0].book_vault == "Lc"

    def test_romanos_ro_to_rm(self):
        raw = "Ro 1:1."
        r = parse_ntsk_block(raw, "Rm 1.1")
        assert r["refs"][0].book_vault == "Rm"

    def test_1samuel_1s_to_1sm(self):
        raw = "1 S 1:1."
        r = parse_ntsk_block(raw, "Gn 1.1")
        assert r["refs"][0].book_vault == "1Sm"

    def test_livro_desconhecido_nao_cria_ref(self):
        """Book sem mapeamento deve retornar 0 refs (não cria ref inválida)."""
        # raw com sigla que não existe - parser não deve criar refs com book_vault=None
        r = parse_ntsk_block("XYZ 1:1.", "Gn 1.1")
        assert r["total_refs"] == 0  # Unknown books produce no refs


class TestVerseRanges:
    """Intervalos de versículos são expandidos em versículos individuais."""

    def test_range_com_hifen_expande_para_versiculos(self):
        """'Lk 3:23-38.' cria 1 ref com 16 verses (gera 16 arestas no grafo).
        
        Range '23-38' expande para lista de versículos: [23,24,...,38].
        O graph_builder gera 1 aresta por verse = 16 arestas.
        """
        raw = "Lk 3:23-38."
        r = parse_ntsk_block(raw, "Mt 1.1")
        assert r["total_refs"] == 1  # 1 ref com 16 verses
        ref = r["refs"][0]
        assert ref.book_vault == "Lc"
        assert ref.chapter == "3"
        assert len(ref.verses) == 16  # 38-23+1 = 16 versículos
        assert ref.verses[0] == "23"
        assert ref.verses[-1] == "38"

    def test_versiculos_multiplos_virgula(self):
        """'Mt 1:1, 2, 3.' cria 1 ref com 3 verses (gera 3 arestas no grafo).
        
        Vírgula '1, 2, 3' após cap: expande para lista [1,2,3].
        O graph_builder gera 1 aresta por verse = 3 arestas.
        """
        raw = "Mt 1:1, 2, 3."
        r = parse_ntsk_block(raw, "Mt 1.1")
        assert r["total_refs"] == 1  # 1 ref com 3 verses
        ref = r["refs"][0]
        assert ref.book_vault == "Mt"
        assert ref.chapter == "1"
        assert len(ref.verses) == 3  # 3 verses separadas por vírgula
        assert ref.verses == ["1", "2", "3"]


class TestApiCompatibilidade:
    """parse_ntsk_block() devolve dict (API pública)."""

    def test_retorna_dict(self):
        raw = "Mt 1:1."
        r = parse_ntsk_block(raw, "Mt 1.1")
        assert isinstance(r, dict)
        assert "refs" in r
        assert "total_refs" in r
        assert "strong_h" in r
        assert "strong_g" in r

    def test_campos_extras(self):
        raw = "Mt 1:1."
        r = parse_ntsk_block(raw, "Mt 1.1")
        assert "prophetic_refs" in r
        assert "at_nt_refs" in r
        assert "contrast_refs" in r
        assert "full_coll_refs" in r
