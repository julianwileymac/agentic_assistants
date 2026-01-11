# Chunk: b7a0cffc154a_1

- source: `conf/base/catalog.yaml`
- lines: 81-112
- chunk: 2/2

```
true
  layer: 06_model_output

# -----------------------------------------------------------------------------
# Reporting Layer
# -----------------------------------------------------------------------------

report_data:
  type: pandas.CSVDataset
  filepath: data/07_reporting/report.csv
  save_args:
    index: false
  layer: 07_reporting

# -----------------------------------------------------------------------------
# Pattern-based Datasets (Factory Pattern)
# -----------------------------------------------------------------------------
# These patterns automatically create datasets based on naming conventions

"{layer}_{name}_parquet":
  type: pandas.ParquetDataset
  filepath: data/{layer}/{name}.parquet
  versioned: false

# -----------------------------------------------------------------------------
# Parameters (accessed via params:key syntax in pipelines)
# -----------------------------------------------------------------------------

parameters:
  type: pandas.JSONDataset
  filepath: conf/base/parameters.yaml
```
