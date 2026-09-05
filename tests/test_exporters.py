from io import BytesIO

from papermint.exporters.bibtex_exporter import export_bibtex
from papermint.exporters.csv_exporter import export_csv, export_excel
from papermint.exporters.ris_exporter import export_ris


def test_bibtex_export_valid(sample_citations):
    output = export_bibtex(sample_citations)
    assert "@article{smith_2020_machine," in output
    assert "author  = {Smith, John A. and Doe, Robert B.}" in output
    assert "title   = {Machine learning in citation parsing}" in output
    assert "year    = {2020}" in output


def test_bibtex_export_empty():
    assert export_bibtex([]) == ""


def test_ris_export_valid(sample_citations):
    output = export_ris(sample_citations)
    assert "TY  - JOUR" in output
    assert "AU  - Smith, John A." in output
    assert "TI  - Machine learning in citation parsing" in output
    assert "PY  - 2020" in output
    assert "ER  - " in output


def test_ris_export_empty():
    assert export_ris([]) == ""


def test_csv_export_headers(sample_citations):
    output = export_csv(sample_citations)
    headers = "Title,Authors,Year,Journal,Volume,Issue,Pages,DOI,URL,Publisher,Confidence"
    assert headers in output


def test_csv_export_data(sample_citations):
    output = export_csv(sample_citations)
    assert "Machine learning in citation parsing" in output
    assert "Smith, John A. & Doe, Robert B." in output or "Smith, John A.; Doe, Robert B." in output
    assert "2020" in output


def test_excel_export_returns_bytesio(sample_citations):
    output = export_excel(sample_citations)
    assert isinstance(output, BytesIO)
    output.seek(0)
    assert len(output.read()) > 0


def test_a_merged_export_names_each_entrys_source_file(sample_citations):
    # A batch merges several documents into one list; a spreadsheet that cannot
    # say which file a row came from has lost the fact the merge destroyed.
    merged = [c.model_copy(update={"source_file": "ERIC_ED060699.pdf"}) for c in sample_citations]
    header, first, *_ = export_csv(merged).splitlines()
    assert header.endswith("Source file")
    assert "ERIC_ED060699.pdf" in first


def test_a_single_documents_export_has_no_source_column(sample_citations):
    # Nothing to report, so nothing is added: the analyzer's export keeps the
    # columns it always had.
    assert "Source file" not in export_csv(sample_citations).splitlines()[0]
