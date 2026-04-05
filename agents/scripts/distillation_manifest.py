"""Manifesto de fontes para a pipeline de destillacao."""
from pathlib import Path

from distillation_models import SourceManifest, SourceManifestItem


_SOURCE_ITEMS = (
    SourceManifestItem(
        sigla="AYBD",
        nivel=3,
        path="dicionarios-enciclopedias/AYBD",
        source_class="general_dictionary",
        domains=("AT", "NT", "historia", "arqueologia"),
        physical_layout="directory",
        expected_unit_types=("concept", "person", "place", "historical_context"),
        preferred_usage="broad synthesis and context",
        promotion_limits=("requires corroboration",),
        independence_group="AYBD",
        tradition="academic_reference",
        target_surface="wiki",
        target_domain="historia-da-interpretacao",
    ),
    SourceManifestItem(
        sigla="DJG1",
        nivel=3,
        path=(
            "dicionarios-enciclopedias/IVP-Black/"
            "Joel B. Green & Scot McKnight (eds.) - Dictionary of Jesus and the Gospels, 1st ed. (IVP DNT).txt"
        ),
        source_class="corpus_dictionary",
        domains=("evangelhos",),
        physical_layout="single_file",
        expected_unit_types=("concept", "person", "historical_context"),
        preferred_usage="gospels corpus concepts",
        promotion_limits=("requires corroboration",),
        independence_group="DJG",
        tradition="evangelical_reference",
        target_surface="wiki",
        target_domain="evangelhos",
    ),
    SourceManifestItem(
        sigla="DJG2",
        nivel=3,
        path=(
            "dicionarios-enciclopedias/IVP-Black/"
            "Joel B. Green & Jeannine K. Brown & Nicholas Perrin (eds.) - "
            "Dictionary of Jesus and the Gospels, 2nd ed. (IVP DNT).txt"
        ),
        source_class="corpus_dictionary",
        domains=("evangelhos",),
        physical_layout="single_file",
        expected_unit_types=("concept", "person", "historical_context"),
        preferred_usage="gospels corpus concepts",
        promotion_limits=("requires corroboration",),
        independence_group="DJG",
        tradition="evangelical_reference",
        target_surface="wiki",
        target_domain="evangelhos",
    ),
    SourceManifestItem(
        sigla="DPL1",
        nivel=3,
        path=(
            "dicionarios-enciclopedias/IVP-Black/"
            "Gerald F. Hawthorne & Ralph P. Martin (eds.) - Dictionary of Paul and His Letters, 1st ed. (IVP DNT).txt"
        ),
        source_class="corpus_dictionary",
        domains=("paulinas",),
        physical_layout="single_file",
        expected_unit_types=("concept", "person", "historical_context"),
        preferred_usage="pauline corpus concepts",
        promotion_limits=("requires corroboration",),
        independence_group="DPL",
        tradition="evangelical_reference",
        target_surface="wiki",
        target_domain="paulinas",
    ),
    SourceManifestItem(
        sigla="DPL2",
        nivel=3,
        path=(
            "dicionarios-enciclopedias/IVP-Black/"
            "Scot McKnight (eds.) - Dictionary of Paul and His Letters - "
            "A Compendium of Contemporary Biblical Scholarship, 2nd ed. (IVP DNT).txt"
        ),
        source_class="corpus_dictionary",
        domains=("paulinas",),
        physical_layout="single_file",
        expected_unit_types=("concept", "person", "historical_context"),
        preferred_usage="pauline corpus concepts",
        promotion_limits=("requires corroboration",),
        independence_group="DPL",
        tradition="evangelical_reference",
        target_surface="wiki",
        target_domain="paulinas",
    ),
    SourceManifestItem(
        sigla="DLNT",
        nivel=3,
        path=(
            "dicionarios-enciclopedias/IVP-Black/"
            "Ralph P. Martin & Peter H. Davids (eds.) - Dictionary of the "
            "Later New Testament & Its Developments (IVP DNT).txt"
        ),
        source_class="corpus_dictionary",
        domains=("nt",),
        physical_layout="single_file",
        expected_unit_types=("concept", "person", "historical_context"),
        preferred_usage="later new testament concepts",
        promotion_limits=("requires corroboration",),
        independence_group="DLNT",
        tradition="evangelical_reference",
        target_surface="wiki",
        target_domain="historia-da-interpretacao",
    ),
    SourceManifestItem(
        sigla="DNT-B",
        nivel=3,
        path=(
            "dicionarios-enciclopedias/IVP-Black/"
            "Craig A. Evans & Stanley E. Porter (eds.) - Dictionary of New "
            "Testament Background (IVP DNT).txt"
        ),
        source_class="background_dictionary",
        domains=("nt", "historia"),
        physical_layout="single_file",
        expected_unit_types=("historical_context", "concept", "place"),
        preferred_usage="nt background and context",
        promotion_limits=("requires corroboration",),
        independence_group="DNT-B",
        tradition="academic_reference",
        target_surface="wiki",
        target_domain="historia-da-interpretacao",
    ),
    SourceManifestItem(
        sigla="DOT-H",
        nivel=3,
        path=(
            "dicionarios-enciclopedias/IVP-Black/"
            "Bill T. Arnold & H. G. M. Williamson (eds.) - Dictionary of the "
            "Old Testament - Historical Books (IVP DOT).txt"
        ),
        source_class="corpus_dictionary",
        domains=("at",),
        physical_layout="single_file",
        expected_unit_types=("concept", "person", "place", "historical_context"),
        preferred_usage="historical books reference",
        promotion_limits=("requires corroboration",),
        independence_group="DOT",
        tradition="evangelical_reference",
        target_surface="wiki",
        target_domain="historia-da-interpretacao",
    ),
    SourceManifestItem(
        sigla="DOT-P",
        nivel=3,
        path=(
            "dicionarios-enciclopedias/IVP-Black/"
            "T. Desmond Alexander & David W. Baker (eds.) - Dictionary of the "
            "Old Testament - Pentateuch (IVP DOT).txt"
        ),
        source_class="corpus_dictionary",
        domains=("at",),
        physical_layout="single_file",
        expected_unit_types=("concept", "person", "place", "historical_context"),
        preferred_usage="pentateuch reference",
        promotion_limits=("requires corroboration",),
        independence_group="DOT",
        tradition="evangelical_reference",
        target_surface="wiki",
        target_domain="historia-da-interpretacao",
    ),
    SourceManifestItem(
        sigla="DOT-Pr",
        nivel=3,
        path=(
            "dicionarios-enciclopedias/IVP-Black/"
            "Mark J. Boda & J. Gordon McConville (eds.) - Dictionary of the "
            "Old Testament - Prophets (IVP DOT).txt"
        ),
        source_class="corpus_dictionary",
        domains=("at",),
        physical_layout="single_file",
        expected_unit_types=("concept", "person", "historical_context"),
        preferred_usage="prophets reference",
        promotion_limits=("requires corroboration",),
        independence_group="DOT",
        tradition="evangelical_reference",
        target_surface="wiki",
        target_domain="historia-da-interpretacao",
    ),
    SourceManifestItem(
        sigla="DOT-W",
        nivel=3,
        path=(
            "dicionarios-enciclopedias/IVP-Black/"
            "Tremper Longman III & Peter Enns (eds.) - Dictionary of the Old "
            "Testament - Wisdom, Poetry & Writings (IVP DOT).txt"
        ),
        source_class="corpus_dictionary",
        domains=("at",),
        physical_layout="single_file",
        expected_unit_types=("concept", "imagery", "historical_context"),
        preferred_usage="wisdom and writings reference",
        promotion_limits=("requires corroboration",),
        independence_group="DOT",
        tradition="evangelical_reference",
        target_surface="wiki",
        target_domain="historia-da-interpretacao",
    ),
    SourceManifestItem(
        sigla="NIDB",
        nivel=3,
        path="dicionarios-enciclopedias/NIDB",
        source_class="general_dictionary",
        domains=("AT", "NT", "historia"),
        physical_layout="directory",
        expected_unit_types=("concept", "person", "place", "historical_context"),
        preferred_usage="broad synthesis and canonical context",
        promotion_limits=("requires corroboration",),
        independence_group="NIDB",
        tradition="academic_reference",
        target_surface="wiki",
        target_domain="historia-da-interpretacao",
    ),
    SourceManifestItem(
        sigla="DDD",
        nivel=3,
        path="dicionarios-enciclopedias/Dictionary of Deities and Demons in the Bible.txt",
        source_class="theme_dictionary",
        domains=("at", "semitic_context"),
        physical_layout="single_file",
        expected_unit_types=("deity", "concept", "historical_context"),
        preferred_usage="deities and demons reference",
        promotion_limits=("requires corroboration",),
        independence_group="DDD",
        tradition="academic_reference",
        target_surface="wiki",
        target_domain="historia-da-interpretacao",
    ),
    SourceManifestItem(
        sigla="EDT",
        nivel=4,
        path="dicionarios-enciclopedias/EDT",
        source_class="theology_dictionary",
        domains=("teologia",),
        physical_layout="directory",
        expected_unit_types=("concept", "tradition_marker"),
        preferred_usage="systematic theology framing",
        promotion_limits=("level4_only_no_direct_factual_promotion",),
        independence_group="EDT",
        tradition="evangelical_reference",
        target_surface="knowledge",
        target_domain="hermeneutica",
    ),
    SourceManifestItem(
        sigla="EAC",
        nivel=3,
        path="dicionarios-enciclopedias/Encyclopedia of Ancient Christianity.txt",
        source_class="patristics_reference",
        domains=("patristica", "historia-da-interpretacao"),
        physical_layout="single_file",
        expected_unit_types=("person", "historical_context", "reception_history"),
        preferred_usage="ancient christianity and patristics",
        promotion_limits=("requires corroboration",),
        independence_group="EAC",
        tradition="patristic_reference",
        target_surface="wiki",
        target_domain="historia-da-interpretacao",
    ),
    SourceManifestItem(
        sigla="DTIB",
        nivel=4,
        path="dicionarios-enciclopedias/Dictionary for Theological Interpretation of the Bible.txt",
        source_class="hermeneutics_reference",
        domains=("hermeneutica",),
        physical_layout="single_file",
        expected_unit_types=("concept", "tradition_marker"),
        preferred_usage="theological interpretation framing",
        promotion_limits=("level4_only_no_direct_factual_promotion",),
        independence_group="DTIB",
        tradition="evangelical_reference",
        target_surface="knowledge",
        target_domain="hermeneutica",
    ),
    SourceManifestItem(
        sigla="DBI-R",
        nivel=4,
        path=(
            "dicionarios-enciclopedias/"
            "Leland Ryken & James C. Wilhoit & Tremper Longman - Dictionary of Biblical Imagery.txt"
        ),
        source_class="theme_dictionary",
        domains=("imagery",),
        physical_layout="single_file",
        expected_unit_types=("imagery", "concept"),
        preferred_usage="biblical imagery and motifs",
        promotion_limits=("level4_only_no_direct_factual_promotion",),
        independence_group="DBI-R",
        tradition="evangelical_reference",
        target_surface="knowledge",
        target_domain="hermeneutica",
    ),
)


def build_manifest(raw_root: str | Path) -> SourceManifest:
    return SourceManifest(raw_root=Path(raw_root), items=_SOURCE_ITEMS)


def build_raw_search_map(raw_root: str | Path) -> dict[str, dict[str, str | int]]:
    del raw_root
    return {
        item.sigla: {"path": item.path, "nivel": item.nivel}
        for item in _SOURCE_ITEMS
    }
