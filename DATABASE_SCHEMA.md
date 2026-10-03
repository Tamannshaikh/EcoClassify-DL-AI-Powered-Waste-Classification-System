# Database Schema

The MVP can run without a database by storing prediction history in a local JSON/SQLite file. SQLite is recommended if persistent history is required.

## model_versions
- id INTEGER PRIMARY KEY
- version TEXT UNIQUE
- model_name TEXT
- framework TEXT
- input_width INTEGER
- input_height INTEGER
- class_count INTEGER
- artifact_path TEXT
- metrics_json TEXT
- created_at DATETIME

## predictions
- id INTEGER PRIMARY KEY
- filename TEXT
- predicted_class TEXT
- confidence REAL
- probabilities_json TEXT
- model_version TEXT
- created_at DATETIME

## dataset_runs
- id INTEGER PRIMARY KEY
- dataset_name TEXT
- dataset_path TEXT
- train_count INTEGER
- validation_count INTEGER
- test_count INTEGER
- class_distribution_json TEXT
- created_at DATETIME

## training_runs
- id INTEGER PRIMARY KEY
- model_version TEXT
- architecture TEXT
- epochs INTEGER
- batch_size INTEGER
- learning_rate REAL
- best_epoch INTEGER
- accuracy REAL
- precision REAL
- recall REAL
- f1 REAL
- created_at DATETIME

## Relationships
model_versions 1:N predictions
model_versions 1:N training_runs
dataset_runs 1:N training_runs
