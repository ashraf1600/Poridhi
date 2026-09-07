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
run_title = title_p.add_run("Dockerizing Feast: Building a Local Feature Store with Docker and Redis")
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
add_p("This lab teaches you how to containerize Feast, an open-source feature store, using Docker and Docker Compose. You will construct a local feature store architecture that pairs a file-based Parquet offline store with an in-memory Redis online store, exposing feature vectors through an HTTP REST endpoint and visual catalog.")
add_image(doc, "images/feast_architecture.png", "Figure 1: Feast Local Feature Store Containerized Architecture", width=Inches(6.0))

ascii_arch = """+-----------------------------------------------------------------------+
| Docker Host                                                           |
|                                                                       |
|  +-------------------+        +------------------------------------+  |
|  | Client / ML Model |------->| Container: feast-server            |  |
|  | (HTTP Requests)   | :6566  | (Serves online features via REST)  |  |
|  +-------------------+        +------------------+-----------------+  |
|                                                  |                    |
|  +-------------------+                           v                    |
|  | Web Browser       | :8888  +------------------------------------+  |
|  | (Catalog UI)      |------->| Container: redis                   |  |
|  +-------------------+        | (In-memory online feature store)   |  |
|                               +------------------------------------+  |
|                                                  ^                    |
|  +--------------------------------------------+  | Materialization    |
|  | Mounted Repository Directory (/app)        |--+ (Batch to Online)  |
|  | - feature_store.yaml   - features.py       |                       |
|  | - data/driver_stats.parquet (Offline Store)|                       |
|  +--------------------------------------------+                       |
+-----------------------------------------------------------------------+"""
add_code_block(doc, ascii_arch)

# Learning Objectives
add_h2("Learning Objectives")
add_p("By the end of this lab, you will be able to:")
objs = [
    "Configure a Feast repository targeting local file storage and containerized Redis instances.",
    "Build an immutable Docker runtime image with Feast and required database drivers.",
    "Orchestrate multi-container systems using Docker Compose health checks and network definitions.",
    "Materialize historical feature data from an offline store to an online store.",
    "Retrieve online feature vectors via the Feast HTTP REST API for real-time model inference.",
    "Validate feature definitions and metadata through the Feast Web UI dashboard."
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
add_p("Your task is to build a containerized local feature store using Feast, Parquet, and Redis. This system will serve as a reproducible foundation for feature management across development and production environments.")

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
├── docker-compose.yml          # Multi-container orchestration (Redis, Feast Server, Feast UI)
├── Dockerfile                  # Feast custom runtime container definition
├── requirements.txt            # Python package dependencies
├── entrypoint.sh               # Container startup and feature materialization script
├── test_client.py              # Script to query real-time online features from Redis
└── feature_repo/
    ├── feature_store.yaml      # Central Feast storage configuration (Redis + File)
    ├── features.py             # Feature definitions (Entity, FileSource, FeatureView)
    ├── generate_data.py        # Python script to generate sample Parquet data
    └── data/
        ├── driver_stats.parquet # Historical batch dataset (Offline store)
        └── registry.db         # Metadata registry database tracking schemas"""
add_code_block(doc, dir_structure)

add_h3("1.2 What You Will Build")
add_p("You will configure Feast to persist metadata in a SQLite registry, read historical data from local Parquet files, and write online features to a containerized Redis instance.")
add_h3("1.3 Think First: Container Network Resolution")
add_callout(doc, "Think First: Network Addressing", "Question: When Feast runs in a Docker container alongside a Redis container, what hostname should Feast use to connect to Redis?\n\nAnswer: Containers running in the same Docker bridge network communicate using service names defined in docker-compose.yml. Feast must connect to redis:6379, not localhost:6379, because localhost inside a container refers to the container itself.")
add_h3("1.4 Implementation: Configuration File")
add_p("Create feature_repo/feature_store.yaml:")
cfg_code = """project: driver_ranking
registry: data/registry.db
provider: local
online_store:
  type: redis
  connection_string: redis:6379
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
add_callout(doc, "Self-Assessment Checklist", "[X] File feature_repo/feature_store.yaml is created.\n[X] The connection_string points to redis:6379.\n[X] You can explain why localhost will fail inside a containerized setup.")

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
add_callout(doc, "Think First: Startup Automation", "Question: Why should registry updates (feast apply) occur inside the container entrypoint rather than during image build?\n\nAnswer: During image build time, external dependencies like the Redis container and mounted volumes are unavailable. Executing feast apply and materialization at runtime ensures network connectivity to Redis and access to host-mounted configuration files.")

add_h3("3.3 Implementation: Dependencies")
add_p("Create requirements.txt:")
add_code_block(doc, "feast[redis]==0.38.0\npandas>=2.0.0\npyarrow>=12.0.0\nfastapi>=0.100.0\nuvicorn>=0.22.0\nrequests>=2.31.0")

add_h3("3.4 Implementation: Entrypoint Script")
add_p("Create entrypoint.sh:")
ep_code = """#!/usr/bin/env bash
set -eo pipefail

cd /app

if [ ! -f "data/driver_stats.parquet" ]; then
    echo "Dataset not found. Generating sample data..."
    python3 generate_data.py
fi

echo "Applying feature definitions to registry..."
feast apply

if [ "${MATERIALIZE:-false}" = "true" ]; then
    echo "Materializing features to Redis online store..."
    feast materialize-incremental "$(date -u +"%Y-%m-%dT%H:%M:%S")"
fi

case "$1" in
    "serve")
        exec feast serve -h 0.0.0.0 -p 6566
        ;;
    "ui")
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
RUN pip install --no-cache-dir -r requirements.txt

COPY feature_repo/ /app/
COPY entrypoint.sh /usr/local/bin/entrypoint.sh
RUN dos2unix /usr/local/bin/entrypoint.sh && chmod +x /usr/local/bin/entrypoint.sh

EXPOSE 6566 8888

ENTRYPOINT ["entrypoint.sh"]"""
add_code_block(doc, df_code)

# Chapter 4
add_h2("Chapter 4: Multi-Service Orchestration with Docker Compose")
add_p("Running a feature store requires multiple decoupled components: a database for the online store, an API server for inference queries, and an administrative user interface.")
add_h3("4.1 What You Will Build")
add_p("You will construct a docker-compose.yml file defining services for redis, feast-server, and feast-ui using shared networks and container health checks.")
add_h3("4.2 Think First: Container Dependencies")
add_callout(doc, "Think First: Health Checks", "Question: Why is a simple depends_on: [redis] block insufficient for the feast-server container?\n\nAnswer: Standard depends_on only waits until the target container starts, not until the database process inside is ready to accept connections. Using condition: service_healthy ensures Redis is answering PING requests before Feast begins materialization.")

add_h3("4.3 Implementation: Docker Compose Configuration")
add_p("Create docker-compose.yml:")
dc_code = """services:
  redis:
    image: redis:7.2-alpine
    container_name: feast-redis
    ports:
      - "6379:6379"
    volumes:
      - redis-storage:/data
    networks:
      - feast-net
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 3s
      timeout: 2s
      retries: 5
    restart: unless-stopped

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
    depends_on:
      redis:
        condition: service_healthy
    networks:
      - feast-net
    restart: unless-stopped

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
    depends_on:
      redis:
        condition: service_healthy
    networks:
      - feast-net
    restart: unless-stopped

networks:
  feast-net:
    driver: bridge

volumes:
  redis-storage:"""
add_code_block(doc, dc_code)

add_h3("4.4 Test and Verify")
add_p("Start all containers in detached mode:")
add_code_block(doc, "docker compose up --build -d")
add_callout(doc, "Prediction Exercise", "Predict: What status will docker compose ps report for the Redis container when healthy?\n\nVerification: The status column will display Up (healthy).")
add_p("Inspect container statuses:")
add_code_block(doc, "docker compose ps")
add_image(doc, "images/ss1_docker_compose_ps.png", "Screenshot 1: Docker Compose Multi-Container Status")

add_p("Inspect server startup logs:")
add_code_block(doc, "docker compose logs feast-server")
add_image(doc, "images/ss2_feast_server_logs.png", "Screenshot 2: Feast Server Startup and Materialization Logs")

# Chapter 5
add_h2("Chapter 5: Real-Time Feature Ingestion and Serving")
add_p("With services active and features materialized into Redis, client applications can query feature vectors using the Feast REST API.")
add_h3("5.1 What You Will Build")
add_p("You will query the Feast feature server using curl, build a Python test client, and explore the Feast Web UI dashboard.")
add_h3("5.2 Think First: Query Payloads")
add_callout(doc, "Think First: Online Query Structure", "Question: What two payload attributes are mandatory when sending a POST request to /get-online-features?\n\nAnswer:\n1. features: A list of feature strings formatted as feature_view_name:feature_name.\n2. entities: A dictionary mapping entity join keys to lists of entity IDs.")

add_h3("5.3 Test with cURL")
add_p("Send an HTTP request to retrieve feature values for driver IDs 1001 and 1002:")
curl_cmd = """curl -X POST http://localhost:6566/get-online-features \\
  -H "Content-Type: application/json" \\
  -d '{
    "features": [
      "driver_hourly_stats:conv_rate",
      "driver_hourly_stats:acc_rate",
      "driver_hourly_stats:avg_daily_trips"
    ],
    "entities": {
      "driver_id": [1001, 1002]
    }
  }'"""
add_code_block(doc, curl_cmd)

add_h3("5.4 Test with Python Client")
add_p("Create test_client.py:")
py_client = """import requests

FEAST_URL = "http://localhost:6566/get-online-features"

payload = {
    "features": [
        "driver_hourly_stats:conv_rate",
        "driver_hourly_stats:acc_rate",
        "driver_hourly_stats:avg_daily_trips"
    ],
    "entities": {
        "driver_id": [1001, 1002, 1003, 1004, 1005]
    }
}

response = requests.post(FEAST_URL, json=payload)
data = response.json()
cols = [r["values"] for r in data.get("results", [])]

print(f"{'DRIVER ID':<12} | {'CONV RATE':<12} | {'ACC RATE':<12} | {'DAILY TRIPS':<12}")
print("=" * 65)
for driver_id, conv_rate, daily_trips, acc_rate in zip(*cols):
    conv_str = f"{conv_rate:<12.4f}" if conv_rate is not None else f"{'None':<12}"
    acc_str = f"{acc_rate:<12.4f}" if acc_rate is not None else f"{'None':<12}"
    trips_str = f"{daily_trips:<12}" if daily_trips is not None else f"{'None':<12}"
    print(f"{driver_id:<12} | {conv_str} | {acc_str} | {trips_str}")"""
add_code_block(doc, py_client)
add_image(doc, "images/ss3_python_client_output.png", "Screenshot 3: Online Feature Retrieval via Python Client")

add_h3("5.5 Inspect Feature Store Catalog")
add_p("Open your web browser and navigate to http://localhost:8888. Verify that the driver entity, driver_hourly_stats feature view, and data sources appear in the catalog.")
add_image(doc, "images/ss4_feast_web_ui.png", "Screenshot 4: Feast Web UI Catalog Dashboard at http://localhost:8888")

add_h3("5.6 Experiment: Handling Unseen Entities")
add_callout(doc, "Experiment: Missing Entities", "Observation: Query Feast for an entity ID that does not exist in the offline dataset (e.g. driver_id: 9999). Feast returns status NOT_FOUND with null values.\n\nResolution: Production inference pipelines must implement defensive handling for missing values, such as imputing global feature averages or executing fallback business logic.")

# Epilogue
add_h2("Epilogue: The Complete System")
add_p("Your containerized Feast architecture is running and functional:")
t2 = doc.add_table(rows=1, cols=4)
style_table(t2, [1.5, 1.0, 2.5, 1.5], ["Service", "Port", "Endpoint / Role", "Engine"], [
    ["feast-server", "6566", "POST /get-online-features (Serving API)", "FastAPI / Redis"],
    ["feast-ui", "8888", "GET / (Web Catalog Dashboard)", "Feast UI"],
    ["redis", "6379", "In-memory key-value online store", "Redis 7.2"]
])

add_p("Complete End-to-End Verification Sequence:")
add_code_block(doc, "docker compose ps\ncurl http://localhost:6566/get-online-features -H \"Content-Type: application/json\" -d '{\"features\": [\"driver_hourly_stats:conv_rate\"], \"entities\": {\"driver_id\": [1001]}}'\ncurl -I http://localhost:8888/")
add_image(doc, "images/ss5_feast_entities_list.png", "Screenshot 5: Registered Feast Entities in SQLite Metadata Registry")

# The Principles
add_h2("The Principles")
principles = [
    "Decouple Offline Processing from Online Serving: Use column-oriented storage formats (Parquet) for batch model training and in-memory key-value stores (Redis) for low-latency inference.",
    "Treat Features as Code: Maintain entity and feature view definitions in version-controlled repositories to prevent training-serving skew.",
    "Synchronize via Deterministic Materialization: Ingest historical metrics into online storage using explicit timestamps to avoid serving future observations.",
    "Enforce Container Readiness: Configure Docker health checks to prevent dependent services from starting before backing datastores are ready to accept connections."
]
for idx, pr in enumerate(principles, 1):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after = Pt(2)
    p.paragraph_format.left_indent = Inches(0.25)
    r = p.add_run(f"{idx}. {pr}")
    r.font.name = 'Calibri'
    r.font.size = Pt(10)

# Troubleshooting
add_h2("Troubleshooting")
add_p("Error: Connection refused to redis:6379\nCause: feast-server initiated materialization before Redis was ready to accept TCP traffic.\nSolution: Ensure docker-compose.yml includes depends_on.redis.condition: service_healthy.")
add_p("Error: Status NOT_FOUND for valid entities\nCause: The materialization timestamp parameter predates the event timestamps in data/driver_stats.parquet.\nSolution: Execute an explicit materialization command inside the running container:\ndocker exec -it feast-server feast materialize-incremental $(date -u +\"%Y-%m-%dT%H:%M:%S\")")
add_p("Error: entrypoint.sh: \\r: command not found\nCause: Windows carriage return (CRLF) characters present in bash script.\nSolution: Run dos2unix entrypoint.sh or configure Git to check out files with LF line endings.")

# Conclusion
add_h2("Conclusion")
add_p("In this lab, you successfully containerized Feast to construct a local, production-grade feature store architecture using Docker and Redis. By decoupling the file-based Parquet offline store from the in-memory Redis online store, you established a dual-tier storage pattern optimized for both batch training datasets and sub-millisecond real-time inference.")
conclusion_pts = [
    "Unified Feature Definitions: Declared immutable entities, sources, and feature views as version-controlled Python code, preventing training-serving skew across teams.",
    "Multi-Container Orchestration: Built a custom Docker image and orchestrated services using Docker Compose health checks and automated startup scripts.",
    "Deterministic Materialization: Synchronized historical batch observations from Parquet files into Redis using explicit timestamp watermarks.",
    "Low-Latency Feature Serving: Queried the Feast HTTP REST API to retrieve online feature vectors for live model inference and defensive validation.",
    "Metadata Governance: Inspected registered entities, feature schemas, and storage backends using the interactive Feast Web UI catalog."
]
for idx, pt in enumerate(conclusion_pts, 1):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after = Pt(2)
    p.paragraph_format.left_indent = Inches(0.25)
    r = p.add_run(f"• {pt}")
    r.font.name = 'Calibri'
    r.font.size = Pt(10)

add_p("This containerized setup provides a reproducible, portable foundation that can be transitioned to cloud-scale MLOps deployments utilizing managed databases, object stores, and Kubernetes clusters.")

# Next Steps
add_h2("Next Steps")
add_p("1. Configure an on-demand feature view to calculate dynamic ratios during feature retrieval.\n2. Integrate Feast online feature retrieval directly into an ML inference service (such as FastAPI, MLflow, or Triton).\n3. Replace local Parquet files with an Amazon S3 or Google Cloud Storage bucket source.")

# Additional Resources
add_h2("Additional Resources")
add_p("- Official Feast Documentation: https://docs.feast.dev/\n- Feast Python SDK Reference: https://docs.feast.dev/reference/python-api-reference\n- Docker Compose Specification: https://docs.docker.com/compose/")

# Save document
out_path = "Dockerizing_Feast_Local_Feature_Store_Lab.docx"
doc.save(out_path)
print(f"Document successfully created at: {out_path}")
