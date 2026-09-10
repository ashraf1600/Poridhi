import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

def set_cell_background(cell, hex_color):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{hex_color}"/>')
    tcPr.append(shd)

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = parse_xml(f'<w:tcMar {nsdecls("w")}><w:top w:w="{top}" w:type="dxa"/><w:bottom w:w="{bottom}" w:type="dxa"/><w:left w:w="{left}" w:type="dxa"/><w:right w:w="{right}" w:type="dxa"/></w:tcMar>')
    tcPr.append(tcMar)

def add_code_block(doc, code_text):
    table = doc.add_table(rows=1, cols=1)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False
    
    cell = table.cell(0, 0)
    cell.width = Inches(6.5)
    set_cell_background(cell, "F4F5F7")
    set_cell_margins(cell, top=120, bottom=120, left=180, right=180)
    
    # Border
    tcPr = cell._tc.get_or_add_tcPr()
    borders = parse_xml(f'<w:tcBorders {nsdecls("w")}><w:top w:val="single" w:sz="4" w:space="0" w:color="E2E4E8"/><w:left w:val="single" w:sz="18" w:space="0" w:color="0052CC"/><w:bottom w:val="single" w:sz="4" w:space="0" w:color="E2E4E8"/><w:right w:val="single" w:sz="4" w:space="0" w:color="E2E4E8"/></w:tcBorders>')
    tcPr.append(borders)
    
    p = cell.paragraphs[0]
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after = Pt(2)
    p.paragraph_format.line_spacing = 1.15
    run = p.add_run(code_text.strip())
    run.font.name = 'Consolas'
    run.font.size = Pt(9.5)
    run.font.color.rgb = RGBColor(23, 43, 77)

def add_callout(doc, title, body_text):
    table = doc.add_table(rows=1, cols=1)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    cell = table.cell(0, 0)
    cell.width = Inches(6.5)
    set_cell_background(cell, "EBF3FC")
    set_cell_margins(cell, top=140, bottom=140, left=180, right=180)
    
    tcPr = cell._tc.get_or_add_tcPr()
    borders = parse_xml(f'<w:tcBorders {nsdecls("w")}><w:top w:val="single" w:sz="4" w:space="0" w:color="CCE0F5"/><w:left w:val="single" w:sz="24" w:space="0" w:color="0052CC"/><w:bottom w:val="single" w:sz="4" w:space="0" w:color="CCE0F5"/><w:right w:val="single" w:sz="4" w:space="0" w:color="CCE0F5"/></w:tcBorders>')
    tcPr.append(borders)
    
    p = cell.paragraphs[0]
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after = Pt(4)
    run_t = p.add_run(title + "\n")
    run_t.bold = True
    run_t.font.name = 'Calibri'
    run_t.font.size = Pt(10.5)
    run_t.font.color.rgb = RGBColor(0, 82, 204)
    
    run_b = p.add_run(body_text)
    run_b.font.name = 'Calibri'
    run_b.font.size = Pt(10)
    run_b.font.color.rgb = RGBColor(23, 43, 77)

def add_image(doc, img_path, caption_text, width=Inches(6.2)):
    import os
    if os.path.exists(img_path):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Pt(8)
        p.paragraph_format.space_after = Pt(2)
        run = p.add_run()
        run.add_picture(img_path, width=width)
        
        cp = doc.add_paragraph()
        cp.alignment = WD_ALIGN_PARAGRAPH.CENTER
        cp.paragraph_format.space_before = Pt(2)
        cp.paragraph_format.space_after = Pt(8)
        c_run = cp.add_run(caption_text)
        c_run.font.name = 'Calibri'
        c_run.font.size = Pt(9.5)
        c_run.font.italic = True
        c_run.font.color.rgb = RGBColor(107, 119, 140)

def style_table(table, col_widths, headers, rows):
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False
    
    # Header row
    hdr_cells = table.rows[0].cells
    for i, title in enumerate(headers):
        hdr_cells[i].text = title
        hdr_cells[i].width = Inches(col_widths[i])
        set_cell_background(hdr_cells[i], "0052CC")
        set_cell_margins(hdr_cells[i], top=120, bottom=120, left=120, right=120)
        p = hdr_cells[i].paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        for r in p.runs:
            r.font.name = 'Calibri'
            r.font.bold = True
            r.font.size = Pt(10)
            r.font.color.rgb = RGBColor(255, 255, 255)
            
    # Data rows
    for r_idx, row_data in enumerate(rows):
        row_cells = table.add_row().cells
        bg_col = "FFFFFF" if r_idx % 2 == 0 else "F8F9FA"
        for c_idx, val in enumerate(row_data):
            row_cells[c_idx].text = str(val)
            row_cells[c_idx].width = Inches(col_widths[c_idx])
            set_cell_background(row_cells[c_idx], bg_col)
            set_cell_margins(row_cells[c_idx], top=80, bottom=80, left=120, right=120)
            p = row_cells[c_idx].paragraphs[0]
            for r in p.runs:
                r.font.name = 'Calibri'
                r.font.size = Pt(9.5)
                r.font.color.rgb = RGBColor(23, 43, 77)

doc = docx.Document()

# Page Setup
sections = doc.sections
for s in sections:
    s.top_margin = Inches(0.8)
    s.bottom_margin = Inches(0.8)
    s.left_margin = Inches(0.8)
    s.right_margin = Inches(0.8)

# Document Title
title_p = doc.add_paragraph()
title_p.alignment = WD_ALIGN_PARAGRAPH.LEFT
title_p.paragraph_format.space_before = Pt(0)
title_p.paragraph_format.space_after = Pt(2)
run_title = title_p.add_run("Dockerizing Feast: Building a Local Feature Store with Docker and SQLite")
run_title.font.name = 'Calibri'
run_title.font.size = Pt(22)
run_title.font.bold = True
run_title.font.color.rgb = RGBColor(9, 30, 66)

sub_p = doc.add_paragraph()
sub_p.paragraph_format.space_after = Pt(14)
run_sub = sub_p.add_run("Poridhi Labs MLOps Development Guide Compliant Technical Lab")
run_sub.font.name = 'Calibri'
run_sub.font.size = Pt(11)
run_sub.font.italic = True
run_sub.font.color.rgb = RGBColor(107, 119, 140)

# Helper for headings
def add_h2(text):
    h = doc.add_paragraph()
    h.paragraph_format.space_before = Pt(14)
    h.paragraph_format.space_after = Pt(4)
    r = h.add_run(text)
    r.font.name = 'Calibri'
    r.font.size = Pt(15)
    r.font.bold = True
    r.font.color.rgb = RGBColor(0, 82, 204)
    return h

def add_h3(text):
    h = doc.add_paragraph()
    h.paragraph_format.space_before = Pt(10)
    h.paragraph_format.space_after = Pt(2)
    r = h.add_run(text)
    r.font.name = 'Calibri'
    r.font.size = Pt(12)
    r.font.bold = True
    r.font.color.rgb = RGBColor(23, 43, 77)
    return h

def add_p(text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after = Pt(4)
    p.paragraph_format.line_spacing = 1.15
    r = p.add_run(text)
    r.font.name = 'Calibri'
    r.font.size = Pt(10.5)
    r.font.color.rgb = RGBColor(23, 43, 77)
    return p

# Introduction
add_h2("Introduction")
add_p("This lab teaches you how to containerize Feast, an open-source feature store, using Docker and Docker Compose. You will construct a local feature store architecture that pairs a file-based Parquet offline store with an embedded SQLite online store, exposing feature vectors through an HTTP REST endpoint and visual catalog.")
add_image(doc, "images/feast_architecture.png", "Figure 1: Feast Local Feature Store Containerized Architecture", width=Inches(6.0))

ascii_arch = """+-----------------------------------------------------------------------+
| Docker Host Machine                                                   |
|                                                                       |
|  +-------------------+        +------------------------------------+  |
|  | Client / ML Model |------->| Container: feast-server            |  |
|  | (HTTP Requests)   | :6566  | (Serves online features via REST)  |  |
|  +-------------------+        +------------------+-----------------+  |
|                                                  |                    |
|  +-------------------+                           v                    |
|  | Web Browser       | :8888  +------------------------------------+  |
|  | (Catalog UI)      |------->| Container: feast-ui                |  |
|  +-------------------+        | (Interactive Web UI Catalog)       |  |
|                               +------------------+-----------------+  |
|                                                  |                    |
|             Docker Bind Mount (./feature_repo:/app)                   |
|  +-----------------------------------------------+-----------------+  |
|  | Host Persistent Storage: ./feature_repo/data/                   |  |
|  | - driver_stats.parquet   (Offline Historical Batch Data)        |  |
|  | - registry.db            (Schema and Metadata Registry)         |  |
|  | - online_store.db        (SQLite Embedded Online Store)         |  |
|  +-----------------------------------------------------------------+  |
+-----------------------------------------------------------------------+"""
add_code_block(doc, ascii_arch)
add_image(doc, "images/feast_bind_mount.png", "Figure 2: Host Machine Bind Mount and Storage Architecture", width=Inches(6.0))

# Learning Objectives
add_h2("Learning Objectives")
add_p("By the end of this lab, you will be able to:")
objs = [
    "Configure a Feast repository targeting local Parquet offline storage and SQLite online storage.",
    "Persist database state across container lifecycles using host directory bind mounts.",
    "Build an immutable Docker runtime image with Feast and SQLite support.",
    "Orchestrate container services using Docker Compose.",
    "Materialize historical feature data from Parquet offline storage to SQLite online storage.",
    "Retrieve online feature vectors via the Feast HTTP REST API for real-time model inference.",
    "Inspect the underlying SQLite storage tables and verify data persistence on the host.",
    "Explore feature catalogs and metadata through the Feast Web UI dashboard."
]
for idx, obj in enumerate(objs, 1):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(1)
    p.paragraph_format.space_after = Pt(2)
    p.paragraph_format.left_indent = Inches(0.25)
    r = p.add_run(f"{idx}. {obj}")
    r.font.name = 'Calibri'
    r.font.size = Pt(10)

add_p("Prerequisites: Familiarity with Python, Docker containers, and REST API conventions.")

# Prologue
add_h2("Prologue: The Challenge")
add_p("You join the machine learning platform team at an on-demand logistics company. The dispatch system matches drivers with delivery requests using machine learning models that require sub-millisecond access to driver metrics, including 24-hour conversion rates and daily trip totals.")
add_p("Currently, data scientists calculate features in Jupyter notebooks using batch queries against data lakes, while production engineers re-implement feature computation using custom SQL queries on live production databases. This divergence causes training-serving skew, resulting in degraded prediction accuracy when models are deployed to production.")
add_p("Your task is to build a containerized local feature store using Feast, Parquet, and SQLite. This system will serve as a reproducible foundation for feature management across development and production environments, storing all state on the host machine through Docker bind mounts without requiring external in-memory database engines.")

# Environment Setup
add_h2("Environment Setup")
add_p("Verify that Docker and Docker Compose are installed on your workstation:")
add_code_block(doc, "docker --version\ndocker compose version")
add_p("Create the directory structure for the project:")
add_code_block(doc, "mkdir -p feast-docker-lab/feature_repo/data\ncd feast-docker-lab")

# Chapter 1
add_h2("Chapter 1: Storage Backends and Feature Repository Configuration")
add_p("Feast uses a declarative configuration file, feature_store.yaml, to specify metadata registries, offline data stores, and online serving databases.")

add_h3("1.1 Project Directory Structure")
add_p("Before configuring storage backends, review the project layout. The complete directory and file structure for this lab is organized as follows:")
dir_structure = """feast-docker-lab/
├── docker-compose.yml          # Multi-container orchestration (Feast Server, Feast UI)
├── Dockerfile                  # Feast custom runtime container definition
├── requirements.txt            # Python package dependencies
├── entrypoint.sh               # Container startup and feature materialization script
├── inspect_sqlite.py           # Verification script for SQLite storage inspection
├── test_client.py              # Script to query real-time online features via REST
└── feature_repo/
    ├── feature_store.yaml      # Central Feast storage configuration (SQLite + File)
    ├── features.py             # Feature definitions (Entity, FileSource, FeatureView)
    ├── generate_data.py        # Python script to generate sample Parquet data
    └── data/
        ├── driver_stats.parquet # Historical batch dataset (Offline store)
        ├── registry.db         # Metadata registry database tracking schemas
        └── online_store.db     # SQLite database for low-latency online serving"""
add_code_block(doc, dir_structure)

add_h3("1.2 What You Will Build")
add_p("You will configure Feast to persist metadata in a SQLite registry, read historical data from local Parquet files, and write online features directly to a local SQLite database stored on the host filesystem via a Docker bind mount.")
add_h3("1.3 Think First: Embedded Storage vs Daemon Stores")
add_callout(doc, "Think First: Storage Engine Selection", "Question: Why is SQLite chosen for local development and testing rather than a standalone database service?\n\nAnswer: SQLite is an embedded, serverless database engine that writes directly to disk files. It eliminates network configuration overhead, consumes minimal memory, and requires no auxiliary background daemon processes. For local developer environments, CI pipelines, and unit tests, SQLite provides full feature store functionality with zero infrastructure complexity.")
add_h3("1.4 Implementation: Configuration File")
add_p("Create feature_repo/feature_store.yaml with SQLite online store configuration:")
cfg_code = """project: driver_ranking
registry: data/registry.db
provider: local
online_store:
  type: sqlite
  path: data/online_store.db
offline_store:
  type: file
entity_key_serialization_version: 3"""
add_code_block(doc, cfg_code)

add_h3("1.5 Understanding the Configuration")
t1 = doc.add_table(rows=1, cols=2)
style_table(t1, [2.2, 4.3], ["Key", "Purpose"], [
    ["registry", "Specifies location of the central catalog tracking schemas, entities, and feature views."],
    ["provider", "Specifies infrastructure environment implementation (local, AWS, or GCP)."],
    ["online_store", "Specifies storage for low-latency key-value lookups during live inference."],
    ["offline_store", "Specifies storage for historical feature values used in batch training datasets."]
])

add_h3("1.6 Checkpoint")
add_callout(doc, "Self-Assessment Checklist", "[X] File feature_repo/feature_store.yaml is created.\n[X] The online_store.type is set to sqlite.\n[X] The online_store.path points to data/online_store.db.")

# Chapter 2
add_h2("Chapter 2: Data Modeling and Feature Definitions")
add_p("Feast schemas rely on three core primitives: Entities (primary keys), Data Sources (physical data references), and FeatureViews (schema, properties, and freshness constraints).")
add_h3("2.1 What You Will Build")
add_p("You will write a Python script to generate synthetic historical driver metrics in Parquet format, and define Feast feature objects in features.py.")
add_h3("2.2 Think First: Feature Freshness")
add_callout(doc, "Think First: Time-To-Live (TTL)", "Question: Why must an ML feature store define Time-To-Live (TTL) on feature views?\n\nAnswer: TTL defines the maximum allowable age of a feature value relative to a prediction request timestamp. This prevents inference services from consuming stale data and prevents historical training sets from joining future data.")

add_h3("2.3 Implementation: Synthetic Data Generator")
add_p("Create feature_repo/generate_data.py:")
gen_code = """import os
from datetime import datetime, timedelta, timezone
import numpy as np
import pandas as pd

def generate_driver_data():
    now = datetime.now(timezone.utc)
    timestamps = [now - timedelta(hours=i) for i in range(24)]
    driver_ids = [1001, 1002, 1003, 1004, 1005]
    records = []

    np.random.seed(42)

    for driver_id in driver_ids:
        for ts in timestamps:
            records.append({
                "driver_id": driver_id,
                "conv_rate": float(np.random.uniform(0.2, 0.95)),
                "acc_rate": float(np.random.uniform(0.6, 0.99)),
                "avg_daily_trips": int(np.random.randint(15, 85)),
                "event_timestamp": ts,
                "created": now,
            })

    df = pd.DataFrame(records)
    output_dir = "data"
    os.makedirs(output_dir, exist_ok=True)
    file_path = os.path.join(output_dir, "driver_stats.parquet")
    df.to_parquet(file_path, index=False)
    print(f"Generated {len(df)} records at {file_path}")

if __name__ == "__main__":
    generate_driver_data()"""
add_code_block(doc, gen_code)

add_h3("2.4 Implementation: Feature Definitions")
add_p("Create feature_repo/features.py:")
feat_code = """from datetime import timedelta
from feast import Entity, FeatureView, Field, FileSource
from feast.types import Float32, Int64

driver = Entity(
    name="driver",
    join_keys=["driver_id"],
    description="Driver identifier"
)

driver_stats_source = FileSource(
    name="driver_stats_source",
    path="data/driver_stats.parquet",
    timestamp_field="event_timestamp",
    created_timestamp_column="created"
)

driver_stats_fv = FeatureView(
    name="driver_hourly_stats",
    entities=[driver],
    ttl=timedelta(days=7),
    schema=[
        Field(name="conv_rate", dtype=Float32),
        Field(name="acc_rate", dtype=Float32),
        Field(name="avg_daily_trips", dtype=Int64),
    ],
    online=True,
    source=driver_stats_source
)"""
add_code_block(doc, feat_code)

# Chapter 3
add_h2("Chapter 3: Containerization and Startup Automation")
add_p("Containerizing Feast ensures runtime parity across different host machines and automates the registration and materialization lifecycle.")
add_h3("3.1 What You Will Build")
add_p("You will define explicit dependencies in requirements.txt, write an entrypoint.sh script to manage startup tasks, and create a Dockerfile.")
add_h3("3.2 Think First: Container Entrypoints")
add_callout(doc, "Think First: Startup Automation", "Question: Why should registry updates (feast apply) and materialization occur inside the container entrypoint rather than during image build?\n\nAnswer: During image build time, mounted host directories are unavailable. Executing feast apply and materialization at runtime ensures access to the host-mounted volume, allowing data/online_store.db and data/registry.db to persist directly on the host machine.")

add_h3("3.3 Implementation: Dependencies")
add_p("Create requirements.txt:")
add_code_block(doc, "feast>=0.38.0\npandas>=2.0.0\npyarrow>=12.0.0\nfastapi>=0.100.0\nuvicorn>=0.22.0\nrequests>=2.31.0\ngrpcio\ngrpcio-health-checking\ngrpcio-reflection")

add_h3("3.4 Implementation: Entrypoint Script")
add_p("Create entrypoint.sh:")
ep_code = """#!/usr/bin/env bash
set -eo pipefail

cd /app

echo "=================================================="
echo "Starting Feast Service Container"
echo "=================================================="

# 1. Generate Parquet data if missing
if [ ! -f "data/driver_stats.parquet" ]; then
    echo "Parquet data not found. Generating synthetic dataset..."
    python3 generate_data.py
else
    echo "Found existing Parquet dataset."
fi

# 2. Register Feature Store definitions
echo "Applying feature definitions to registry..."
feast apply

# 3. Materialize features into SQLite if requested
if [ "${MATERIALIZE:-false}" = "true" ]; then
    echo "Materializing features to SQLite online store..."
    feast materialize-incremental "$(date -u +"%Y-%m-%dT%H:%M:%S")"
    echo "Materialization complete."
fi

# 4. Route commands
case "$1" in
    "serve")
        echo "Launching Feast Feature Server on 0.0.0.0:6566..."
        exec feast serve -h 0.0.0.0 -p 6566
        ;;
    "ui")
        echo "Launching Feast Web Dashboard on 0.0.0.0:8888..."
        exec feast ui -h 0.0.0.0 -p 8888
        ;;
    *)
        exec "$@"
        ;;
esac"""
add_code_block(doc, ep_code)

add_h3("3.5 Implementation: Dockerfile")
add_p("Create Dockerfile:")
df_code = """FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE=1 \\
    PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \\
    curl \\
    gcc \\
    python3-dev \\
    dos2unix \\
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \\
    pip install --no-cache-dir -r requirements.txt

COPY feature_repo/ /app/
COPY entrypoint.sh /usr/local/bin/entrypoint.sh
RUN dos2unix /usr/local/bin/entrypoint.sh && chmod +x /usr/local/bin/entrypoint.sh

EXPOSE 6566 8888

ENTRYPOINT ["entrypoint.sh"]"""
add_code_block(doc, df_code)

# Chapter 4
add_h2("Chapter 4: Multi-Service Orchestration with Docker Compose")
add_p("Running a complete local feature store platform involves two core interfaces: an API server for low-latency feature serving, and an interactive web user interface for catalog discovery.")
add_h3("4.1 What You Will Build")
add_p("You will construct a docker-compose.yml file defining services for feast-server and feast-ui using a shared network and host bind mount.")
add_h3("4.2 Think First: Bind Mount Persistence")
add_callout(doc, "Think First: Storage Persistence", "Question: How does mounting ./feature_repo:/app solve data persistence across container updates?\n\nAnswer: Container filesystems are ephemeral by default. When ./feature_repo:/app is bind-mounted, any writes made by Feast to /app/data/online_store.db or /app/data/registry.db are written directly to the host machine disk. Even if containers are destroyed with docker compose down, all materialized features remain intact on the host.")

add_h3("4.3 Implementation: Docker Compose Configuration")
add_p("Create docker-compose.yml:")
dc_code = """services:
  # 1. Feast Feature Server (REST Serving API)
  feast-server:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: feast-server
    command: ["serve"]
    environment:
      - MATERIALIZE=true
    ports:
      - "6566:6566"
    volumes:
      - ./feature_repo:/app
    networks:
      - feast-net
    restart: unless-stopped

  # 2. Feast Web UI (Catalog Dashboard)
  feast-ui:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: feast-ui
    command: ["ui"]
    environment:
      - MATERIALIZE=false
    ports:
      - "8888:8888"
    volumes:
      - ./feature_repo:/app
    networks:
      - feast-net
    restart: unless-stopped

networks:
  feast-net:
    driver: bridge"""
add_code_block(doc, dc_code)

add_h3("4.4 Test and Verify")
add_p("Start all containers in detached mode:")
add_code_block(doc, "docker compose up --build -d")

add_p("Inspect container statuses:")
add_code_block(doc, "docker compose ps")
add_image(doc, "images/ss1_docker_compose_ps.png", "Figure 3: Docker Compose Service Status")

add_p("Inspect server startup and feature materialization logs:")
add_code_block(doc, "docker compose logs feast-server")
add_image(doc, "images/ss2_feast_server_logs.png", "Figure 4: Feast Server Startup and Materialization Logs")

add_p("Verify file persistence on the host machine filesystem:")
add_code_block(doc, "Get-ChildItem feature_repo\\data")
add_image(doc, "images/ss3_host_data_files.png", "Figure 5: Host Storage File Verification")

add_p("Inspect the SQLite online store directly on the host using Python:")
add_code_block(doc, "python inspect_sqlite.py")
add_image(doc, "images/ss4_sqlite_inspection.png", "Figure 6: Direct SQLite Database Inspection")

# Chapter 5
add_h2("Chapter 5: Real-Time Feature Ingestion and Serving")
add_p("With services active and features materialized into SQLite, client applications can query feature vectors using the Feast REST API or direct SQL queries.")

add_h3("5.1 Test with Python Client")
add_p("Create test_client.py:")
test_client_code = """import requests

FEAST_URL = "http://localhost:6566/get-online-features"

request_payload = {
    "features": [
        "driver_hourly_stats:conv_rate",
        "driver_hourly_stats:acc_rate",
        "driver_hourly_stats:avg_daily_trips"
    ],
    "entities": {
        "driver_id": [1001, 1002, 1003, 1004, 1005]
    }
}

response = requests.post(FEAST_URL, json=request_payload, timeout=5)
data = response.json()
cols = [r["values"] for r in data.get("results", [])]

print("Connected successfully. Features retrieved from SQLite online store:")
print("=" * 65)
print(f"{'DRIVER ID':<12} | {'CONV RATE':<12} | {'ACC RATE':<12} | {'DAILY TRIPS':<12}")
print("=" * 65)
for driver_id, conv_rate, daily_trips, acc_rate in zip(*cols):
    conv_str = f"{conv_rate:<12.4f}" if conv_rate is not None else f"{'None':<12}"
    acc_str = f"{acc_rate:<12.4f}" if acc_rate is not None else f"{'None':<12}"
    trips_str = f"{daily_trips:<12}" if daily_trips is not None else f"{'None':<12}"
    print(f"{driver_id:<12} | {conv_str} | {acc_str} | {trips_str}")"""
add_code_block(doc, test_client_code)

add_p("Execute the test client:")
add_code_block(doc, "python test_client.py")
add_image(doc, "images/ss5_python_client_output.png", "Figure 7: Python Client Feature Retrieval Output")

add_h3("5.2 Test with cURL REST API")
add_p("Query online feature vectors using cURL with request.json payload:")
add_code_block(doc, "curl.exe -s -X POST http://localhost:6566/get-online-features -H \"Content-Type: application/json\" -d @request.json")
add_image(doc, "images/ss6_curl_rest_api.png", "Figure 8: REST API Query via cURL Output")

add_h3("5.3 Direct SQLite Table Query")
add_p("To verify how Feast internally organizes feature tables inside SQLite, open the database using sqlite3:")
add_code_block(doc, "sqlite3 feature_repo/data/online_store.db\nsqlite> .tables\nsqlite> SELECT entity_key, feature_name, value FROM driver_ranking_driver_hourly_stats LIMIT 3;")
add_image(doc, "images/ss10_sqlite_table_query.png", "Figure 9: SQLite3 Command Line Table Query")

# Chapter 6
add_h2("Chapter 6: Feast Web UI and Metadata Catalog Exploration")
add_p("The Feast Web UI provides a centralized catalog for data scientists and ML engineers to browse entities, feature views, schemas, and source definitions.")

add_h3("6.1 Inspect Feature Store Catalog")
add_p("Open your web browser and navigate to http://localhost:8888. Verify that the driver_ranking project, driver entity, and driver_hourly_stats feature view appear in the catalog.")
add_image(doc, "images/ss7_feast_web_ui.png", "Figure 10: Feast Web UI Catalog Dashboard at http://localhost:8888")

add_h3("6.2 Inspect Registered Entities via CLI")
add_p("Inspect registered Feast entities from the command line:")
add_code_block(doc, "docker exec feast-server feast entities list")
add_image(doc, "images/ss8_feast_entities_list.png", "Figure 11: Feast CLI Registered Entities List")

add_h3("6.3 Inspect Registered Feature Views via CLI")
add_p("List registered feature views and verify the online store backend:")
add_code_block(doc, "docker exec feast-server feast feature-views list")
add_image(doc, "images/ss9_feast_feature_views_list.png", "Figure 12: Feast CLI Registered Feature Views List")

# Chapter 7
add_h2("Chapter 7: Architectural Evaluation: SQLite vs Redis")
add_p("Choosing an online store backend depends on system latency requirements, deployment topology, and operational overhead:")
t_eval = doc.add_table(rows=1, cols=3)
style_table(t_eval, [1.8, 2.3, 2.4], ["Dimension", "SQLite Online Store", "Redis Online Store"], [
    ["Architecture", "Serverless embedded file database", "Dedicated in-memory caching daemon"],
    ["Deployment Complexity", "Zero infrastructure overhead (single .db file)", "Requires separate container, network, and healthcheck"],
    ["Persistence Model", "Immediate disk write via Docker bind mount", "In-memory with optional append-only file (AOF/RDB)"],
    ["Read Latency", "Low (approx 2 to 5 milliseconds)", "Sub-millisecond (approx 0.5 to 1 millisecond)"],
    ["Concurrent Writes", "Limited by SQLite database file locking", "Highly concurrent non-blocking single-threaded engine"],
    ["Optimal Use Case", "Local development, testing, edge devices, single-node", "High-throughput distributed production clusters"]
])

# Chapter 8
add_h2("Chapter 8: Troubleshooting Guide")
add_p("Error: OperationalError: database is locked\nCause: SQLite uses file-level locking during write operations. Concurrent feast materialize executions can result in lock contention.\nSolution: Ensure only one container performs materialization at a time. In docker-compose.yml, set MATERIALIZE=true only on feast-server, keeping MATERIALIZE=false on feast-ui.")
add_p("Error: Bind mount permission denied on Linux hosts\nCause: Docker runs container processes as root by default, creating root-owned files on host directories.\nSolution: Pass user identifier to compose or run chmod -R 777 feature_repo/data during local setup.")
add_p("Error: Missing Parquet dataset\nCause: Container started before data/driver_stats.parquet was generated.\nSolution: The entrypoint.sh automatically checks for driver_stats.parquet and runs python3 generate_data.py if the file does not exist.")

# Epilogue
add_h2("Epilogue: The Complete System")
add_p("Your containerized Feast architecture is running and functional:")
t_epilogue = doc.add_table(rows=1, cols=4)
style_table(t_epilogue, [1.5, 1.0, 2.5, 1.5], ["Service", "Port", "Endpoint / Role", "Engine"], [
    ["feast-server", "6566", "POST /get-online-features (Serving API)", "FastAPI / SQLite"],
    ["feast-ui", "8888", "GET / (Web Catalog Dashboard)", "Feast UI"]
])

add_p("Complete End-to-End Verification Sequence:")
add_code_block(doc, "docker compose ps\ncurl http://localhost:6566/get-online-features -H \"Content-Type: application/json\" -d '{\"features\": [\"driver_hourly_stats:conv_rate\"], \"entities\": {\"driver_id\": [1001]}}'\ncurl -I http://localhost:8888/")

# The Principles
add_h2("The Principles")
principles = [
    "Decouple Offline Processing from Online Serving: Use column-oriented storage formats (Parquet) for batch model training and low-latency structured stores (SQLite or Redis) for online inference.",
    "Treat Features as Code: Maintain entity and feature view definitions in version-controlled repositories to prevent training-serving skew.",
    "Synchronize via Deterministic Materialization: Ingest historical metrics into online storage using explicit timestamp watermarks to avoid serving future observations.",
    "Guarantee Host Persistence with Bind Mounts: Mount host repository directories into containers to retain database schemas and materialized features across rebuild cycles."
]
for idx, pr in enumerate(principles, 1):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after = Pt(2)
    p.paragraph_format.left_indent = Inches(0.25)
    r = p.add_run(f"{idx}. {pr}")
    r.font.name = 'Calibri'
    r.font.size = Pt(10)

# Conclusion
add_h2("Conclusion")
add_p("In this lab, you containerized Feast to construct a local, production-grade feature store architecture using Docker, SQLite, and host bind mounts. By pairing a local Parquet offline store with an embedded SQLite online store, you established a complete dual-tier feature store pattern with zero external daemon dependencies.")
conclusion_pts = [
    "Unified Feature Definitions: Declared immutable entities, sources, and feature views as version-controlled Python code, preventing training-serving skew across teams.",
    "Host Storage Persistence: Persisted historical Parquet files, metadata registry tables, and SQLite online feature records directly on the host machine using Docker bind mounts.",
    "Automated Lifecycle Management: Built a custom Docker image and orchestrated services using Docker Compose and an automated entrypoint script.",
    "Deterministic Materialization: Synchronized historical batch observations from Parquet files into SQLite using explicit timestamp watermarks.",
    "Low-Latency Feature Serving: Queried the Feast HTTP REST API and direct SQLite tables to retrieve online feature vectors for live model inference.",
    "Metadata Governance: Inspected registered entities, feature schemas, and storage backends using the interactive Feast Web UI catalog and Feast CLI tools."
]
for idx, pt in enumerate(conclusion_pts, 1):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after = Pt(2)
    p.paragraph_format.left_indent = Inches(0.25)
    r = p.add_run(f"• {pt}")
    r.font.name = 'Calibri'
    r.font.size = Pt(10)

add_p("This containerized setup provides a reproducible, lightweight, and portable foundation that can be transitioned to cloud-scale MLOps deployments utilizing managed databases, object stores, and Kubernetes clusters.")

# Save document
out_path = "Dockerizing_Feast_Local_Feature_Store_Lab.docx"
doc.save(out_path)
print(f"Document successfully created at: {out_path}")
