# Changelog

All notable changes to PaperMint are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.1.6] - 2026-09-06

The light theme, rebuilt around measured contrast.

**Fixed** - most of the sidebar was never bound to the design tokens, so it
kept Streamlit's own dark-theme colours and simply disappeared on a light
ground: the navigation, the section labels, the captions and the Settings
panel. Every one is now coloured from a token.

**Changed** - the light palette has three genuinely distinct surfaces, borders
that are visible against the canvas, and a deeper accent, because mint cannot
carry text on white. Every text pair now clears WCAG AA and body text clears
AAA, and a test computes the ratios so a palette edit cannot quietly undo it.

**Known** - the dark palette has two pairs below AA. They are unchanged and
pinned by name in the suite, so a third cannot appear unnoticed.

---

## [2.1.5] - 2026-09-06

A fabricated author that survived its own fix, and a light theme.

**Fixed** - `Washington, D.C.` was still being read as an author. The previous
guard covered only the colon form of a catalogue imprint; the same place with a
full stop or a comma went on inventing a person. The guard now also declines a
candidate whose given part is a state or province abbreviation, in the tight
form only, so `Smith, D. C.` stays a person while `Washington, D.C.` does not.
A parametrised test covers every punctuation an imprint uses.

**Added** - a Settings gear at the foot of the sidebar with a Dark/Light
switch. Every rule in the stylesheet is written against a design token, so one
swapped `:root` block repaints the whole interface - no JavaScript and no
reload - and a motion token eases the change rather than flashing it. Card
bands and notice tones now carry CSS variable references instead of literals,
which is what lets a palette swap reach markup built at render time.

**Fixed** - `build_navigation(only=...)` handed a cached page object to a
single-page navigation, and Streamlit set its default flag in place, so a later
full navigation saw two defaults and raised. It never bit the app, which only
ever builds the full navigation, but it made the test suite order-dependent.

**Known limitation** - `.streamlit/config.toml` declares the dark palette to
Streamlit itself and cannot change at runtime, so chrome Streamlit renders into
its own portals stays dark in light mode.

---

## [2.1.4] - 2026-09-06

The repository moved to the src layout.

**Changed** - `papermint/` is now `src/papermint/`. The root no longer carries a
directory sharing the project's own name, and holds only project files: what you
configure, what you read, and the four directories the work lives in. The layout
is the one the Python Packaging Authority recommends, and it means `import
papermint` can only ever resolve to the installed distribution, never to a
directory that happens to be in the working directory - so the suite tests what
a user would actually install.

`app.py` stays at the root, because it is the path handed to `streamlit run`
rather than a module anyone imports.

Everything that computed a path was moved with it: hatchling's wheel target,
pytest's `pythonpath`, ruff's per-file ignores, `config.PROJECT_ROOT`, and the
architecture gate's `PACKAGE_ROOT`. Every file moved with `git mv`, so history
follows the code.

---

## [2.1.3] - 2026-09-06

A fabricated author, and the route that was missing beside it.

**Fixed** - `Washington, D.C.` was being reported as an author. A catalogue
imprint opens `Washington, D.C.: Childrens Books, 1933`, and the place matches
the inverted-name form exactly: a capitalised surname, a comma, a run of
initials. Because the invented author filled the field confidence weighs most
heavily, the worst-parsed entry on the page carried the highest badge. The
guard is structural - no citation style puts a colon after an author, every
imprint puts one after its place - so there is no list of place names to keep.

**Changed** - the reference formatter can now take its references from a batch,
not only from the analyzer. A reader who had run a batch was previously offered
nothing but the paste box. It also gained a narrowing box, so one reference can
be found in a three-hundred-entry run, and the downloads contain exactly what
the box leaves on screen.

**Fixed** - counts now agree with their nouns: "1 entry", not "1 entries", in
the notices and in the Word document's subtitle; and "This entry is missing an
element" rather than "1 of 1 entries are missing an element".

**Added** - a `Source file` column on merged CSV and Excel exports, present
only when there is provenance to report, so a single document's export keeps
the columns it always had.

---

## [2.1.2] - 2026-09-06

The batch page's document switcher.

**Changed** - the switcher was a rail of per-file containers beside a
two-thirds pane. Its entries overlapped one another, its labels would not
align, and academic filenames did not fit the width it had. It is now a single
row of pills above a full-width pane: one widget that owns its own selection,
cannot overlap itself, keeps the choice across a page switch, and gives the
citation cards the whole page. Each pill names its file and how many
references came out of it.

**Removed** - `micro_note()`, whose only caller was the rail, and every
stylesheet rule that had accumulated trying to make the rail behave.

**Fixed** - a clipped filename no longer reads `report_2019.` before its
ellipsis.

---

## [2.1.1] - 2026-09-06

The batch page became a workbench.

**Added** - `ui/components/citation_browser.py`: search, ordering, a
needs-review filter and paging over any citation list, namespaced by a key
prefix so several can coexist on one screen. The analyzer and both of the
batch page's lists now share it, so a long reference list behaves the same
wherever it appears. `render_compact_export()` gives a document its own export
in a popover; `document_header()` and `micro_note()` are the two primitives the
new layout needed.

**Changed** - batch results are a rail and a pane instead of a stack of
expanders. The rail names every file with how it turned out; selecting one puts
that document in the pane with its own controls and its own export. The merged
export moved into a tab of its own, so it is one click from the top of the
results rather than below every file. Every entry in the merged library names
the file it came from.

**Fixed** - opening a 163-entry file no longer renders 163 cards at once, and
reaching the export no longer means scrolling past every document in the run.

---

## [2.1.0] - 2026-09-06

Interface and coverage work, driven by using 2.0.0 on a real education
catalogue.

**Added** - `formatters/reference_formatter.py` and the **Reference formatter** page:
a `Citation` rendered as APA 7, MLA 9, IEEE or Chicago 17, with an account of
what each style is for, its ordered elements and the punctuation that closes
each, and the same entry shown four ways. `PipelineService.parse_reference()`
parses one pasted reference. `ui/state.py` keeps widget values across a page
switch. About gained a full "Citation styles, explained" section.

**Changed** - the citation card is now an aligned label-and-value grid with a
coverage meter, so every field says what it is. The processing indicator is an
animated flow that names what each stage is doing. Bibliography detection
collects *every* qualifying reference block rather than the text after the last
heading, bounded by appendix, index and glossary headings. Both workspace pages
show their cached result when the upload control comes back empty after a page
switch.

**Removed** - the DOI lookup page, replaced by the reference formatter; the "Segments
set aside" panel, though the quarantine behind it still runs and still keeps
non-bibliographic segments out of every export; `_has_bibliographic_density()`,
dead since 2.0.0.

**Unchanged, and deliberately so** - nothing is invented. The new formatter
omits any element the source did not supply and names it, and it never recases
a title, because deciding which words are proper nouns is exactly the judgement
a machine gets wrong.

---

---

## [2.0.0] - 2026-09-03

A rebuild of the architecture, the parsing engine and the interface. The public
signatures of `detect_bibliography_section`, `split_citations`, `parse_citation`,
`detect_style`, `summarize` and every exporter are unchanged, so the original
48 tests still pass untouched.

### Added

#### Architecture
- **`papermint/pipeline.py`** — `PipelineService` orchestrating extract,
  characterise, parse and summarise, with a `PipelineStage` enum, per-stage
  progress callbacks, `PipelineOptions`, and `process_batch()` with per-file
  error isolation.
- **`papermint/errors.py`** — the full `PaperMintError` hierarchy. Each error
  carries a reader-facing message, an optional `remedy`, and a stable `kind`.
- **`papermint/extractors/registry.py`** — resolves an extractor by MIME type
  with an extension fallback, replacing the `if/elif` chain duplicated in both
  Streamlit pages.
- **`papermint/cli.py`** — headless entry point running the identical service.
  Installed as the `papermint` console script.
- **`papermint/ui/navigation.py`** — routes built once so any page can link to
  any other.

#### Parsing
- **`papermint/parsers/text_normalizer.py`** — ligature folding, de-hyphenation
  across line breaks, dash and quote unification, page-number and
  running-header removal, and sentence counting that is not fooled by author
  initials or DOIs.
- `characterize_document()` returning a `DetectionOutcome` with the document
  kind, the detection method, the body text, a confidence score, and
  human-readable reasoning the interface displays.
- `score_citation()` exposed publicly so confidence can be recomputed after a
  manual correction.
- Page counts, per-page text and non-fatal warnings on every extractor.

#### Models
- `DocumentKind`, `DetectionMethod`, `ConfidenceBand`, `DocumentStats`,
  `BatchResult`, `BatchFileResult`.
- Display properties on `Citation`: `display_title`, `short_author_string`,
  `venue`, `locator`, `doi_url`, `confidence_band`, `needs_review`,
  `missing_fields`, `is_parsed`.

#### Interface
- **`papermint/ui/theme.py`** — every colour, type step, space step, radius and
  duration as one token set, emitted as CSS custom properties.
- **`papermint/ui/icons.py`** — 21 inline SVG icons on `currentColor`,
  replacing emoji throughout.
- **`papermint/ui/html.py`** — `esc()`, `render()` over `st.html()`, `clamp()`,
  `dot_join()`.
- **`papermint/ui/components/primitives.py`** — page headers, section headers,
  statistic tiles, chips, notices, empty states, definition lists, tile grids.
- Inline citation editor for all eight fields, with confidence rescored on save.
- Per-card BibTeX view, search across five fields, six sort orders, a "Needs
  review" filter, and pagination beyond 25 entries.
- Export preview for the text formats, and filenames derived from the source
  document.

#### Testing
- `tests/test_architecture.py` (223 checks) enforcing the layering and coding
  rules by parsing every module with `ast`.
- `tests/test_pipeline.py` (18) covering orchestration, batch isolation, the
  registry and the CLI.
- `tests/test_normalization.py` (26) covering text repair and the parser guards.
- `tests/test_ui.py` (30) covering markup, escaping, components, and rendering
  all five pages through `streamlit.testing.v1.AppTest`.
- Total: 345 tests, up from 48. No test makes a network call.

### Changed

- **Both Streamlit pages now call `PipelineService`.** `extract.py` replaced six
  inline domain calls plus a MIME dispatch with one service call; `batch.py`
  likewise.
- **Results are cached in session state** against a digest of the file and the
  options, so typing in the search box no longer reprocesses the document.
- **The density scan walks backwards to a block boundary** instead of returning
  the trailing half of the document, so the closing paragraphs of a paper are no
  longer parsed as citations.
- **The references heading match takes the last occurrence**, so a table of
  contents entry cannot win over the real section.
- **Every split is validated before acceptance**, and continuation fragments are
  merged, so prose is no longer shredded into fake entries.
- **Author surnames** now match particles, hyphens, apostrophes and all-caps
  forms.
- **spaCy is optional.** The summariser falls back to a deterministic regex
  segmenter, and a CI job runs without the model to keep that path exercised.
- **`ruff` configuration is explicit.** Fifteen rule families selected in
  `pyproject.toml` rather than inherited from the installed version's defaults.
- CI split into lint, test across three Python versions, and a separate job with
  the NLP extra installed.
- `.streamlit/config.toml` realigned to the design tokens.

### Fixed

- **Uploads returned zero bytes on every rerun.** `UploadedFile` is a `BytesIO`
  whose cursor persists, so `.read()` worked once. Every later interaction read
  nothing and the page reported that no text could be extracted. Now
  `getvalue()`.
- **The pipeline stepper stacked four progress bars.** Its render function was
  called once per stage, appending a new widget each time. It now draws into a
  single placeholder.
- **Three-or-more-author APA citations lost their authors.** The regex captured
  `"C. D., Brown, E."` as one author's given name.
- **A date span in a title was read as a page range.** `1700-2000` became
  `pp. 1700-2000`.
- **Unescaped document text corrupted cards.** A title containing an angle
  bracket ate the rest of the card.
- **The export panel's wrapper never wrapped anything.** An opening `<div>` in
  one `st.markdown` call and its closing tag in another are separate DOM nodes.
- **Sentence counts were inflated** by counting every period, including author
  initials and DOIs.
- **Page counts were always zero** although `extract_text_by_page` existed.
- **Domain-layer logging went nowhere.** No handler was ever configured.
- **The About page rendered its Mermaid diagram as a grey code block**, because
  every line carried four spaces of indentation.
- **CrossRef network failures were indistinguishable from a missing DOI.**
- **`--force-parse` reported the wrong document kind** for annotated
  bibliographies.

### Removed

- `pytextrank`, `bibtexparser` and `httpx` from dependencies. None were imported
  anywhere in the codebase.
- `spacy.cli.download()` from the request path, which stalled a user-facing page
  for minutes with no feedback.
- Named entity recognition from author extraction, which reported place names
  and common nouns as people.
- Gradient text, emoji iconography and hover-lift animation from the interface.
- Silent `return ""` on extractor failure, replaced by typed exceptions.

---

## [1.0.0] - 2026-08-12

### Added
- **Multi-format document support**: PDF, Image (PNG/JPG with OCR), Word (DOCX), PowerPoint (PPTX)
- **Bibliography section detection**: Automatically finds "References" / "Bibliography" headers in documents
- **Citation splitting**: Multi-heuristic pipeline (numbered, blank-line, hanging indent, author boundary)
- **Citation style auto-detection**: Identifies APA, MLA, IEEE, and Chicago with confidence scores
- **Smart citation parsing**: Regex + spaCy NLP extraction of authors, title, year, journal, volume, pages, DOI
- **Confidence scoring**: Each citation gets a 0-100% extraction confidence score
- **CrossRef DOI lookup**: Fetch complete citation metadata from CrossRef API by DOI
- **Batch file processing**: Upload and process multiple documents at once
- **TextRank summarization**: Extractive document summarization using PyTextRank via spaCy
- **Export formats**: BibTeX (.bib), RIS (.ris), CSV, Excel (.xlsx), Word (.docx), PDF
- **Multi-page Streamlit UI**: Extract, Batch Processing, DOI Lookup, and About pages
- **Dark theme**: Mint-green accent on deep slate background via `.streamlit/config.toml`
- **Pydantic data models**: Type-safe Citation, Author, and ExtractionResult models
- **Test suite**: pytest tests for models, parsers, exporters, and enrichment
- **CI pipeline**: GitHub Actions workflow for linting and testing
- **Modern Python packaging**: `pyproject.toml` with PEP 621 compliance

### Removed
- Single-file `app.py` monolith architecture (replaced with `papermint/` package)
- Hardcoded regex-only extraction (3 patterns → multi-strategy pipeline)
- "First 2 sentences" summarization (replaced with TextRank)
- Dead dependencies (`requests`, `python-dotenv`, `numpy`)
- Misspelled `steamlit/` config directory (replaced with `.streamlit/`)
- `requirements.txt` and `requirements.in` (replaced with `pyproject.toml`)

### Fixed
- Streamlit theme config was never applied due to `steamlit/` folder typo
- `extract_title_from_nlp()` created spaCy doc but never used it
- `extract_year_from_nlp()` `[-4:]` slicing broke on non-year DATE entities
- DOCX/PPTX claimed in README but not accepted in file uploader
- `pytesseract` missing from dependencies
- README had placeholder `yourusername` and `your-email@example.com`
- Missing LICENSE file despite README claiming MIT License
- `st.write(f"*Title:*")` used single asterisks (italic, not bold)
