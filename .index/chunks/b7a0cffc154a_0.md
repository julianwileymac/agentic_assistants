# Chunk: b7a0cffc154a_0

- source: `conf/base/catalog.yaml`
- lines: 1-91
- chunk: 1/2

```
# ============================================================================
# Data Catalog Configuration
# ============================================================================
# This file defines datasets for the Agentic framework using Kedro-style
# configuration. Datasets can be loaded and saved using the DataCatalog.
#
# Example usage:
#   from agentic_assistants.data.catalog import DataCatalog
#   catalog = DataCatalog.from_yaml("conf/base/catalog.yaml")
#   df = catalog.load("raw_data")
# ============================================================================

# -----------------------------------------------------------------------------
# Raw Layer (01_raw) - Immutable source data
# -----------------------------------------------------------------------------

raw_data:
  type: pandas.CSVDataset
  filepath: data/01_raw/data.csv
  load_args:
    encoding: utf-8
    sep: ","
  layer: 01_raw

raw_users:
  type: pandas.CSVDataset
  filepath: data/01_raw/users.csv
  load_args:
    encoding: utf-8
  layer: 01_raw

# -----------------------------------------------------------------------------
# Intermediate Layer (02_intermediate) - Cleaned data
# -----------------------------------------------------------------------------

cleaned_data:
  type: pandas.ParquetDataset
  filepath: data/02_intermediate/cleaned.parquet
  save_args:
    compression: snappy
  layer: 02_intermediate

# -----------------------------------------------------------------------------
# Primary Layer (03_primary) - Domain models
# -----------------------------------------------------------------------------

users:
  type: pandas.ParquetDataset
  filepath: data/03_primary/users.parquet
  versioned: true
  layer: 03_primary

# -----------------------------------------------------------------------------
# Feature Layer (04_feature) - ML features
# -----------------------------------------------------------------------------

user_features:
  type: pandas.ParquetDataset
  filepath: data/04_feature/user_features.parquet
  versioned: true
  layer: 04_feature

# -----------------------------------------------------------------------------
# Model Input/Output Layers
# -----------------------------------------------------------------------------

training_data:
  type: pandas.ParquetDataset
  filepath: data/05_model_input/training.parquet
  layer: 05_model_input

model:
  type: pickle.PickleDataset
  filepath: data/06_model_output/model.pkl
  versioned: true
  layer: 06_model_output

predictions:
  type: pandas.ParquetDataset
  filepath: data/06_model_output/predictions.parquet
  versioned: true
  layer: 06_model_output

# -----------------------------------------------------------------------------
# Reporting Layer
# -----------------------------------------------------------------------------

report_data:
  type: pandas.CSVDataset
  filepath: data/07_reporting/report.csv
```
