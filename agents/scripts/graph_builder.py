"""graph_builder.py -- Constrói grafo NTSK bidirecional entre versiculos.
Gera: nodes.json, edges.json (forward+inverse), graph_stats.json
Versão: bidirectional — arestas forward (NTSK) e inverse (inferidas).
"""
import json
import sys
from collections import defaultdict
from pathlib import Path

from vault_parser import parse_vault
from ntsk_parser import parse_ntsk_block, NTSKRef

def _book(ref_id: str) -> str:
    """Extrai a sigla do livro de um ID de versículo (e.g. 'Mt 1.1' -> 'Mt')."""
    return ref_id.split(" ")[0] if " " in ref_id else ""


# --- Mapa de símbolo -> tipo canônico de aresta ---
EDGE_TYPE_MAP: dict[str, str] = {
    "*":    "especially_clear",
    "+":    "full_collection",
    "=":    "type_antitype",
    "\u25d0": "contrast",
    "\u2a72": "type_antitype_scriptural",
    "\u25b6": "ot_quote_in_nt",
    "\u2721": "fulfills_prophecy",
    "\u2225": "parallel_passage",
    "\u2021": "false_doctrine_proof",
    "\u2713": "critically_clear",
}


def _edge_type_from_ref(ref: NTSKRef) -> str:
    """Deriva o edge_type mais específico a partir dos símbolos."""
    for sym in ref.symbols:
        if sym in EDGE_TYPE_MAP:
            return EDGE_TYPE_MAP[sym]
    return "cross_ref"


def _build_edges_from_ref(
    source_id: str,
    ref: NTSKRef,
) -> list[dict]:
    """Gera arestas forward e inverse para uma NTSKRef.
    
    Para cada versiculo emits UM par de arestas (forward + inverse),
    agregando todos os símbolos da ref num unico edge.
    """
    edges = []
    book = ref.book_vault
    if not book:
        return edges

    for verse in ref.verses:
        target_id = f"{book} {ref.chapter}.{verse.strip()}"
        primary_type = _edge_type_from_ref(ref)

        # ── Aresta forward: source -> target ────────────────────────────
        edges.append({
            "source":      source_id,
            "target":      target_id,
            "source_book": _book(source_id),
            "target_book": book,
            "edge_type":   primary_type,
            "symbols":     ref.symbols,
            "direction":   "forward",
            "inferred":    False,
        })

        # ── Aresta inversa: target -> source (bidirecionalidade) ─────────
        edges.append({
            "source":      target_id,
            "target":      source_id,
            "source_book": book,
            "target_book": _book(source_id),
            "edge_type":   primary_type,
            "symbols":     ref.symbols,
            "direction":   "inverse",
            "inferred":    True,
        })

    return edges


def _deduplicate_edges(edges: list[dict]) -> list[dict]:
    """Remove arestas duplicadas por (source, target, direction).
    
    Se o mesmo par aparece com symbols/types diferentes, agrega-os
    num unico edge (todos os símbolos + todos os types).
    """
    # agrupar por (source, target, direction)
    groups: dict = {}
    for e in edges:
        key = (e["source"], e["target"], e["direction"])
        if key not in groups:
            groups[key] = {**e, "symbols": set(e["symbols"])}
        else:
            # agregar símbolos
            groups[key]["symbols"].update(e["symbols"])
            # manter o tipo mais específico (não cross_ref quando há tipo específico)
            existing = groups[key]["edge_type"]
            incoming = e["edge_type"]
            if incoming != "cross_ref" and existing == "cross_ref":
                groups[key]["edge_type"] = incoming
            elif incoming != "cross_ref" and existing != incoming:
                groups[key]["edge_type"] = "; ".join(sorted(set(existing.split("; ")) | {incoming}))

    unique = []
    for key, e in groups.items():
        unique.append({**e, "symbols": sorted(e["symbols"])})
    return unique


def build_graph(nodes) -> dict:
    """Constrói o grafo completo com arestas forward + inverse."""
    all_edges: list[dict] = []
    metas: list[dict] = []
    missing: dict = defaultdict(int)
    unresolved_targets: set = set()    # targets que nao existem como source
    forward_by_type: dict = defaultdict(int)
    inverse_by_type: dict = defaultdict(int)

    # ── 1ª passagem: nodes + edges forward ────────────────────────────────
    for node in nodes:
        if node.node_type != "versiculo" or not node.ntsk_raw:
            continue

        source_id = node.referencia
        r = parse_ntsk_block(node.ntsk_raw, source_id)

        metas.append({
            "id":           source_id,
            "sigla":        node.sigla,
            "livro":        node.livro,
            "capitulo":     node.capitulo,
            "versiculo":    node.versiculo,
            "testamento":   node.testamento,
            "canon_cristao": node.canon_cristao,
            "ref_count":    r["total_refs"],
            "strong_h":     r["strong_h"],
            "strong_g":     r["strong_g"],
        })

        for ref in r["refs"]:
            if not ref.book_vault:
                missing[ref.book_abbr] += 1
                continue

            edges = _build_edges_from_ref(source_id, ref)
            for e in edges:
                all_edges.append(e)
                if e["direction"] == "forward":
                    forward_by_type[e["edge_type"]] += 1
                else:
                    inverse_by_type[e["edge_type"]] += 1

    # ── 2ª passagem: marcar unresolved targets ───────────────────────────
    source_ids = {m["id"] for m in metas}
    for e in all_edges:
        if e["direction"] == "forward" and e["target"] not in source_ids:
            unresolved_targets.add(e["target"])

    # ── Deduplicação ─────────────────────────────────────────────────────
    unique_edges = _deduplicate_edges(all_edges)

    # ── Estatísticas ──────────────────────────────────────────────────────
    et = defaultdict(int)
    for e in unique_edges:
        et[e["edge_type"]] += 1

    return {
        "nodes": metas,
        "edges": unique_edges,
        "stats": {
            "total_nodes":          len(metas),
            "total_edges":          len(unique_edges),
            "forward_edges":        sum(1 for e in unique_edges if e["direction"] == "forward"),
            "inverse_edges":        sum(1 for e in unique_edges if e["direction"] == "inverse"),
            "edge_types":           dict(et),
            "forward_by_type":      dict(forward_by_type),
            "inverse_by_type":      dict(inverse_by_type),
            "missing_books":         dict(missing),
            "unresolved_targets":   sorted(unresolved_targets),
            "unresolved_count":     len(unresolved_targets),
            "carryover_examples":   [],    # preenchido se detectar padrão
        },
    }


def export_graph(vault_dir: str, output_dir: str = ".") -> None:
    """Exporta o grafo para JSON em output_dir."""
    # Tenta "Bíblia" com e sem acento (compatibilidade Windows)
    biblia_path = Path(vault_dir) / "Bíblia"
    if not biblia_path.exists():
        biblia_path = Path(vault_dir) / "Biblia"
    if not biblia_path.exists():
        print(f"[ERRO] Diretorio Biblia nao encontrado em: {vault_dir}")
        sys.exit(1)

    nodes = parse_vault(biblia_path)
    graph = build_graph(nodes)

    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    for key in ("nodes", "edges"):
        fp = out / f"{key}.json"
        with open(fp, "w", encoding="utf-8") as f:
            json.dump(graph[key], f, ensure_ascii=False, indent=2)
        print(f"  Salvo: {fp}  ({len(graph[key]):,} registros)")

    fp_stats = out / "graph_stats.json"
    with open(fp_stats, "w", encoding="utf-8") as f:
        json.dump(graph["stats"], f, ensure_ascii=False, indent=2)
    print(f"  Salvo: {fp_stats}")

    # Resumo rápido
    s = graph["stats"]
    print(
        f"\nGrafo gerado:"
        f" {s['total_nodes']} nos,"
        f" {s['total_edges']} arestas"
        f" ({s['forward_edges']} forward + {s['inverse_edges']} inverse)"
    )
    if s["unresolved_count"]:
        print(f"  [AVISO] {s['unresolved_count']} targets nao resolvidos como nos")
    if s["missing_books"]:
        print(f"  [AVISO] {len(s['missing_books'])} siglas sem mapeamento: {list(s['missing_books'].keys())}")


if __name__ == "__main__":
    vault_dir   = sys.argv[1] if len(sys.argv) > 1 else "."
    output_dir  = sys.argv[2] if len(sys.argv) > 2 else "agents/output"
    export_graph(vault_dir, output_dir)
