"""Tests for cross-file duplicate merging.

The negative cases come first, per the standing rule: merging two different
works is far worse than showing one work twice, so most of this file is about
what must *not* be merged.
"""

from __future__ import annotations

from papermint.dedupe import deduplicate, duplicate_key, normalize_doi, normalize_title
from papermint.models import BatchFileResult, BatchResult, Citation, ExtractionResult


def _citation(**kwargs) -> Citation:
    """Build a citation with only the fields a test cares about."""
    return Citation(**kwargs)


# --- What must not be merged ------------------------------------------------


def test_two_works_sharing_a_title_but_not_a_year_are_kept_apart():
    # Proceedings volumes, annual reports and chapters called "Introduction"
    # repeat their titles across years. A title alone is not identity.
    entries = [
        _citation(title="Annual Report", year="2019"),
        _citation(title="Annual Report", year="2020"),
    ]
    merged, removed = deduplicate(entries)
    assert removed == 0
    assert len(merged) == 2


def test_an_entry_without_strong_identity_is_never_merged():
    # No DOI and no year: the entry whose identity is least certain is exactly
    # the one a careless rule would collapse.
    entries = [
        _citation(title="Untitled fragment"),
        _citation(title="Untitled fragment"),
    ]
    merged, removed = deduplicate(entries)
    assert removed == 0
    assert len(merged) == 2
    assert duplicate_key(entries[0]) is None


def test_different_dois_are_different_works():
    entries = [
        _citation(title="Same title", year="2020", doi="10.1/aaa"),
        _citation(title="Same title", year="2020", doi="10.1/bbb"),
    ]
    _merged, removed = deduplicate(entries)
    assert removed == 0


def test_an_empty_run_is_handled():
    assert deduplicate([]) == ([], 0)


# --- What must be merged ----------------------------------------------------


def test_the_same_doi_is_one_work_however_it_was_written():
    entries = [
        _citation(title="A", year="2020", doi="10.1016/J.X", source_file="a.pdf"),
        _citation(title="B", year="2021", doi="https://doi.org/10.1016/j.x", source_file="b.pdf"),
    ]
    merged, removed = deduplicate(entries)
    assert removed == 1
    assert len(merged) == 1


def test_the_same_title_and_year_is_one_work_across_punctuation_and_case():
    entries = [
        _citation(title="Deep Learning, Revisited", year="2020", source_file="a.pdf"),
        _citation(title="deep learning revisited", year="2020", source_file="b.pdf"),
    ]
    merged, removed = deduplicate(entries)
    assert removed == 1
    assert len(merged) == 1


def test_the_fullest_record_survives_a_merge():
    # A merge may only ever add information.
    sparse = _citation(title="A study", year="2020", source_file="a.pdf")
    full = _citation(
        title="A study",
        year="2020",
        journal="Nature",
        volume="12",
        pages="1-9",
        source_file="b.pdf",
    )
    merged, _removed = deduplicate([sparse, full])
    assert merged[0].journal == "Nature"
    assert merged[0].pages == "1-9"


def test_a_merged_entry_records_every_file_it_came_from():
    # Provenance is the one fact merging would otherwise destroy.
    entries = [
        _citation(title="A study", year="2020", source_file="a.pdf"),
        _citation(title="A study", year="2020", source_file="b.pdf"),
        _citation(title="A study", year="2020", source_file="c.pdf"),
    ]
    merged, removed = deduplicate(entries)
    assert removed == 2
    assert sorted(merged[0].merged_sources) == ["a.pdf", "b.pdf", "c.pdf"]


def test_order_follows_first_appearance():
    entries = [
        _citation(title="First", year="2001"),
        _citation(title="Second", year="2002"),
        _citation(title="First", year="2001"),
    ]
    merged, _removed = deduplicate(entries)
    assert [c.title for c in merged] == ["First", "Second"]


def test_a_single_document_is_left_entirely_alone():
    # Nothing merged means nothing rewritten: merged_sources stays empty, so a
    # one-file run carries no trace of a feature it never used.
    entries = [_citation(title="A", year="2020"), _citation(title="B", year="2020")]
    merged, removed = deduplicate(entries)
    assert removed == 0
    assert all(not c.merged_sources for c in merged)


# --- Normalisation ----------------------------------------------------------


def test_doi_normalisation_strips_every_resolver_form():
    for written in ("10.1/X", "doi:10.1/x", "https://doi.org/10.1/X", " 10.1/x "):
        assert normalize_doi(written) == "10.1/x"


def test_title_normalisation_folds_accents_and_punctuation():
    assert normalize_title("Éducation: A Study!") == normalize_title("education a study")


# --- The batch surface ------------------------------------------------------


def test_a_batch_reports_its_duplicates_without_losing_the_raw_list():
    shared = {"title": "Shared work", "year": "2020"}
    result = BatchResult(
        files=[
            BatchFileResult(
                filename="a.pdf",
                result=ExtractionResult(citations=[_citation(**shared, source_file="a.pdf")]),
            ),
            BatchFileResult(
                filename="b.pdf",
                result=ExtractionResult(citations=[_citation(**shared, source_file="b.pdf")]),
            ),
        ]
    )
    assert len(result.citations) == 2
    assert len(result.unique_citations) == 1
    assert result.duplicate_count == 1
