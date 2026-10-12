# COVID-19 Economic Impact Dashboard

This project will become a multi-page Plotly Dash dashboard examining the
economic impact of the COVID-19 pandemic.

## Current status

The first raw-data bundle has been collected and validated. See
[`docs/DATASETS.md`](docs/DATASETS.md) for scope, provenance, limitations, and
the recommended analytical role of each source.

Re-download the sources with:

```bash
bash scripts/download_data.sh
```

Raw source files are kept unchanged under `data/raw/`. Cleaned, joined, and
analysis-ready tables should be written to a separate `data/processed/`
directory so that every transformation remains reproducible.
