# DataForge — Enterprise Data Engineering & Pipeline Orchestration Platform

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.12-3776AB?style=flat-square&logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/FastAPI-0.115-009688?style=flat-square&logo=fastapi&logoColor=white" />
  <img src="https://img.shields.io/badge/Apache_Spark-3.5-E25A1C?style=flat-square&logo=apachespark&logoColor=white" />
  <img src="https://img.shields.io/badge/Apache_Kafka-231F20?style=flat-square&logo=apachekafka&logoColor=white" />
  <img src="https://img.shields.io/badge/Apache_Airflow-3.0-017CEE?style=flat-square&logo=apacheairflow&logoColor=white" />
  <img src="https://img.shields.io/badge/dbt-Data_Transforms-FF694B?style=flat-square&logo=dbt&logoColor=white" />
  <img src="https://img.shields.io/badge/PostgreSQL-15-336791?style=flat-square&logo=postgresql&logoColor=white" />
  <img src="https://img.shields.io/badge/Docker-Ready-2496ED?style=flat-square&logo=docker&logoColor=white" />
  <img src="https://img.shields.io/badge/License-MIT-22C55E?style=flat-square" />
</p>

> **Enterprise Data Engineering & Pipeline Orchestration Platform** — define, schedule, monitor, and observe data pipelines powered by Apache Spark, Kafka, Airflow, and dbt. Includes data quality validation, schema registry, lineage tracking, and alerting.

---

## Overview

DataForge is the control plane for enterprise data infrastructure. Data engineers define pipelines via REST API — specifying source, transformation logic, destination, and schedule. The platform orchestrates execution across Spark batch jobs, Kafka stream processors, and dbt models. Built-in data quality checks validate schema conformance, null rates, and statistical distributions. The lineage graph tracks every transformation from source to BI layer, making debugging and compliance auditing straightforward.

Designed for **data engineering teams, analytics platforms, and data platform organizations** that need observable, governable data pipelines at scale.

---

## Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                       DataForge Platform                         │
│                                                                  │
│  ┌──────────┐  ┌──────────────┐  ┌────────────┐  ┌──────────┐  │
│  │ Pipelines│  │  Data Quality│  │  Lineage   │  │  Auth    │  │
│  │   API    │  │     API      │  │   API      │  │  API     │  │
│  └────┬─────┘  └──────┬───────┘  └──────┬─────┘  └──────────┘  │
│       │               │                 │                       │
│  ┌────▼───────────────▼─────────────────▼──────────────────┐   │
│  │                  Orchestration Engine                    │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌────────────────┐ │   │
│  │  │ Spark Engine │  │ Kafka Stream │  │  dbt Runner    │ │   │
│  │  │ Batch Jobs   │  │  Processor   │  │  SQL Transforms│ │   │
│  │  └──────────────┘  └──────────────┘  └────────────────┘ │   │
│  └──────────────────────────────────────────────────────────┘   │
│                         │                                       │
│  ┌──────────────────────▼──────────────────────────────────┐   │
│  │    PostgreSQL 15  ·  Airflow Metadata  ·  Redis Cache   │   │
│  │    pipelines · runs · quality_checks · lineage_nodes    │   │
│  └─────────────────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────────────┘
```

---

## Features

### 1. Pipeline Definition & Scheduling
Define data pipelines with: source type (S3, PostgreSQL, Kafka, API), transformation type (Spark SQL, dbt model, Python UDF), destination, and Cron schedule. Pipelines are versioned; rollback to any previous version.

### 2. Multi-Engine Execution
- **Apache Spark**: Distributed batch processing for large-scale transformations
- **Apache Kafka**: Real-time stream processing with exactly-once semantics
- **dbt**: SQL-based transformations with dependency resolution and test execution

### 3. Data Quality Framework
Configurable quality checks per pipeline: schema validation, null rate thresholds, row count expectations, statistical distribution checks (mean, std), and referential integrity. Failed checks block downstream pipeline stages.

### 4. Data Lineage Tracking
Automatic column-level lineage extraction. Visualize the full dependency graph from raw source to BI dashboard. Impact analysis shows which downstream models break if an upstream source changes.

### 5. Pipeline Observability
Per-run metrics: rows processed, bytes read/written, transformation duration, quality check pass/fail, error logs. SLA alerts when pipelines miss their completion window.

---

## API Endpoints

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/api/v1/auth/register` | Public | Register user |
| POST | `/api/v1/auth/login` | Public | Login |
| POST | `/api/v1/pipelines` | Engineer/Admin | Define new pipeline |
| GET | `/api/v1/pipelines` | Required | List pipelines |
| POST | `/api/v1/pipelines/{id}/trigger` | Required | Trigger manual run |
| GET | `/api/v1/pipelines/{id}/runs` | Required | Get run history |
| GET | `/api/v1/pipelines/{id}/runs/{run_id}` | Required | Get run details + logs |
| POST | `/api/v1/quality/{pipeline_id}` | Required | Run quality checks |
| GET | `/api/v1/quality/{pipeline_id}` | Required | Get quality report |
| GET | `/api/v1/lineage/{pipeline_id}` | Required | Get lineage graph |
| GET | `/health` | Public | Health check |

---

## Getting Started

```bash
git clone https://github.com/Gokatech-Inc/DataForge.git
cd DataForge && cp .env.example .env
docker-compose up -d
# API: http://localhost:8000 · Docs: http://localhost:8000/docs
```

---

## License

MIT License — **Gokatech Inc** · Data Engineering
