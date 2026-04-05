"""graph_builder.py — Constrói e exporta o grafo de conhecimento do vault.
Uso: python graph_builder.py <vault_dir> [output_dir]
Produz: nodes.json, edges.json, graph_stats.json
"""
import json, sys
from pathlib import Path
from collections import defaultdict
from vault_parser import parse_vault
from ntsk_parser import parse_ntsk_block

EDGE_TYPE_MAP = {
    "\u2721":"fulfills_prophecy","\u25b6":"ot_quote_in_nt",
    "=":"type_antitype","\u2a72":"type_antitype_scriptural",
    "\u25d0":"contrast","\u2225":"parallel_passage",
    "\u2021":"false_doctrine_proof","*":"especially_clear",
    "\u2713":"critically_clear",
}

def build_graph(nodes):
    edges, metas, missing = [], [], defaultdict(int)
    for node in nodes:
        if node.node_type != "versiculo" or not node.ntsk_raw:
            continue
        r = parse_ntsk_block(node.ntsk_raw, node.referencia)
        metas.append({
            "id": node.referencia, "sigla": node.sigla, "livro": node.livro,
            "capitulo": node.capitulo, "versiculo": node.versiculo,
            "testamento": node.testamento, "canon_cristao": node.canon_cristao,
            "ref_count": r["total_refs"],
            "strong_h": r["strong_h"], "strong_g": r["strong_g"],
        })
        for ref in r["refs"]:
            if not ref.book_vault:
                missing[ref.book_abbr] += 1
                continue
            etype = next((EDGE_TYPE_MAP[s] for s in ref.symbols if s in EDGE_TYPE_MAP), "cross_ref")
            for vs in ref.verses:
                edges.append({
                    "source": node.referencia,
                    "target": f"{ref.book_vault}-{ref.chapter}.{vs.strip()}",
                    "target_book": ref.book_vault,
                    "edge_type": etype, "symbols": ref.symbols,
                })
    et = defaultdict(int)
    for e in edges: et[e["edge_type"]] += 1
    return {"nodes": metas, "edges": edges,
            "stats": {"total_nodes": len(metas), "total_edges": len(edges),
                      "edge_types": dict(et), "missing_books": dict(missing)}}

def export_graph(vault_dir: str, output_dir: str = "."):
    biblia_path = Path(vault_dir) / "Bíblia"
    if not biblia_path.exists():
        # fallback para "Biblia" sem acento (vaults antigos)
        biblia_path = Path(vault_dir) / "Biblia"
    if not biblia_path.exists():
        print(f"[ERRO] Diretório Bíblia não encontrado em: {vault_dir}")
        print(f"       Verifique o caminho: {Path(vault_dir).resolve()}")
        sys.exit(1)
    nodes = parse_vault(biblia_path)
    graph = build_graph(nodes)
    out   = Path(output_dir)
    out.mkdir(exist_ok=True)
    for key in ("nodes", "edges"):
        with open(out / f"{key}.json", "w", encoding="utf-8") as f:
            json.dump(graph[key], f, ensure_ascii=False, indent=2)
    with open(out / "graph_stats.json", "w", encoding="utf-8") as f:
        json.dump(graph["stats"], f, ensure_ascii=False, indent=2)
    print(f"Exportado: {graph['stats']['total_nodes']} nos, {graph['stats']['total_edges']} arestas")
    if graph["stats"]["missing_books"]:
        print(f"[WARN] missing: {graph['stats']['missing_books']}")

if __name__ == "__main__":
    vault_dir  = sys.argv[1] if len(sys.argv) > 1 else "."
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "./output"
    export_graph(vault_dir, output_dir)
