# Final paper quality audit

**Status:** FAIL
**PDF pages:** 50
**Bibliography:** 49 entries; 50 cited
**Abstract:** 343 words
**Figures/tables:** 5/9

## Automated checks

- PASS: `build_success`
- PASS: `page_count_exact_50`
- PASS: `pdfinfo_success`
- PASS: `pdftotext_success`
- PASS: `qpdf_check_success_or_unavailable`
- PASS: `not_encrypted`
- PASS: `all_fonts_embedded`
- PASS: `no_missing_source_refs`
- PASS: `no_duplicate_labels`
- FAIL: `no_missing_bib_entries`
- PASS: `all_bib_entries_cited`
- PASS: `no_undefined_log_refs`
- PASS: `no_undefined_log_citations`
- PASS: `no_latex_errors`
- PASS: `no_overfull_boxes`
- PASS: `no_todo_fixme`
- PASS: `no_double_question_mark`
- FAIL: `no_risky_acceptance_claim`
- PASS: `no_false_full_mechanization_claim`
- PASS: `no_unqualified_industrial_claim`
- FAIL: `abstract_reasonable_length`
- PASS: `no_duplicate_long_paragraphs`
- PASS: `all_pages_rendered`
- PASS: `no_blank_pages`
- PASS: `consistent_page_dimensions`
- PASS: `no_content_at_physical_edge`

## Limitations

- Raster checks detect blank/sparse pages and physical-edge collisions, not every semantic layout defect.
- Venue portal and human authorship declarations are external to the PDF.
