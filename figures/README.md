# Manuscript figure reproduction

Four semantic schematics are generated directly by Matplotlib:

```sh
python -B figures/draw_schematics.py --outdir scratch/figures
```

Their arrows describe declared rewrite, closure, evidence, and implication
relations, not measured execution traces. The companion manuscript build
regenerates these four PDFs and the count chart below, including every label.

`results-bars.csv` contains the five counts shown in the manuscript, in the
original category order, among 451,736 staged systems. The properties overlap;
the bars are not an additive partition and are not runtime measurements.

From the artifact directory:

```sh
python -m pip install -r figures/requirements.txt
python -B figures/draw_results_bars.py
```

To rederive the plotting CSV from saved enumeration totals, without enumerating:

```sh
python -B figures/draw_results_bars.py --refresh-data results/staged/staged-enumeration-summary.json
```

The axes retain thousands of systems, the existing labels, and the original
physical box. The manuscript's caption/description are unchanged. Its include
is `paper/figures/results-bars.tex` in the manuscript-containing project.
The scientific reproduction driver does not overwrite this figure wrapper.

The unmodified Linux Libertine regular TrueType font has its own license at
`../fonts/OFL-1.1.txt`. `--font` or installed matching TeX/Matplotlib regular
TrueType is also supported. No font substitution is performed. Matplotlib is
only an optional plotting dependency, not a dependency of the scientific core.
