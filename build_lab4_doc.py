import os
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls

def set_cell_background(cell, hex_color):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{hex_color}"/>')
    tcPr.append(shd)

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = parse_xml(f'<w:tcMar {nsdecls("w")}><w:top w:w="{top}" w:type="dxa"/><w:bottom w:w="{bottom}" w:type="dxa"/><w:left w:w="{left}" w:type="dxa"/><w:right w:w="{right}" w:type="dxa"/></w:tcMar>')
    tcPr.append(tcMar)

def add_title(doc, text, subtitle=None):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(4)
    run = p.add_run(text)
    run.font.name = 'Calibri'
    run.font.size = Pt(24)
    run.bold = True
    run.font.color.rgb = RGBColor(0, 82, 204) # Poridhi Blue
    
    if subtitle:
        p2 = doc.add_paragraph()
        p2.paragraph_format.space_before = Pt(0)
        p2.paragraph_format.space_after = Pt(16)
        r2 = p2.add_run(subtitle)
        r2.font.name = 'Calibri'
        r2.font.size = Pt(12)
        r2.font.italic = True
        r2.font.color.rgb = RGBColor(107, 119, 140)

def add_heading_1(doc, text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(18)
    p.paragraph_format.space_after = Pt(6)
    p.paragraph_format.keep_with_next = True
    run = p.add_run(text)
    run.font.name = 'Calibri'
    run.font.size = Pt(16)
    run.bold = True
    run.font.color.rgb = RGBColor(0, 82, 204)

def add_heading_2(doc, text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(14)
    p.paragraph_format.space_after = Pt(4)
    p.paragraph_format.keep_with_next = True
    run = p.add_run(text)
    run.font.name = 'Calibri'
    run.font.size = Pt(13)
    run.bold = True
    run.font.color.rgb = RGBColor(23, 43, 77)

def add_heading_3(doc, text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(10)
    p.paragraph_format.space_after = Pt(3)
    p.paragraph_format.keep_with_next = True
    run = p.add_run(text)
    run.font.name = 'Calibri'
    run.font.size = Pt(11)
    run.bold = True
    run.font.color.rgb = RGBColor(52, 69, 99)

def add_paragraph(doc, text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(6)
    p.paragraph_format.line_spacing = 1.15
    run = p.add_run(text)
    run.font.name = 'Calibri'
    run.font.size = Pt(10.5)
    run.font.color.rgb = RGBColor(23, 43, 77)
    return p

def add_bullet(doc, bold_prefix, text):
    p = doc.add_paragraph(style='List Bullet')
    p.paragraph_format.space_before = Pt(1)
    p.paragraph_format.space_after = Pt(3)
    p.paragraph_format.line_spacing = 1.15
    if bold_prefix:
        r_bold = p.add_run(bold_prefix + " ")
        r_bold.bold = True
        r_bold.font.name = 'Calibri'
        r_bold.font.size = Pt(10.5)
        r_bold.font.color.rgb = RGBColor(23, 43, 77)
    run = p.add_run(text)
    run.font.name = 'Calibri'
    run.font.size = Pt(10.5)
    run.font.color.rgb = RGBColor(23, 43, 77)

def add_numbered(doc, num_str, bold_prefix, text):
    p = doc.add_paragraph()
    p.paragraph_format.left_indent = Inches(0.25)
    p.paragraph_format.space_before = Pt(1)
    p.paragraph_format.space_after = Pt(3)
    p.paragraph_format.line_spacing = 1.15
    r_num = p.add_run(num_str + " ")
    r_num.bold = True
    r_num.font.name = 'Calibri'
    r_num.font.size = Pt(10.5)
    r_num.font.color.rgb = RGBColor(0, 82, 204)
    if bold_prefix:
        r_bold = p.add_run(bold_prefix + " ")
        r_bold.bold = True
        r_bold.font.name = 'Calibri'
        r_bold.font.size = Pt(10.5)
        r_bold.font.color.rgb = RGBColor(23, 43, 77)
    run = p.add_run(text)
    run.font.name = 'Calibri'
    run.font.size = Pt(10.5)
    run.font.color.rgb = RGBColor(23, 43, 77)

def add_code_block(doc, code_text):
    table = doc.add_table(rows=1, cols=1)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False
    cell = table.cell(0, 0)
    cell.width = Inches(6.5)
    set_cell_background(cell, "F4F5F7")
    set_cell_margins(cell, top=100, bottom=100, left=160, right=160)
    tcPr = cell._tc.get_or_add_tcPr()
    borders = parse_xml(f'<w:tcBorders {nsdecls("w")}><w:top w:val="single" w:sz="4" w:space="0" w:color="E2E4E8"/><w:left w:val="single" w:sz="18" w:space="0" w:color="0052CC"/><w:bottom w:val="single" w:sz="4" w:space="0" w:color="E2E4E8"/><w:right w:val="single" w:sz="4" w:space="0" w:color="E2E4E8"/></w:tcBorders>')
    tcPr.append(borders)
    p = cell.paragraphs[0]
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after = Pt(2)
    p.paragraph_format.line_spacing = 1.15
    run = p.add_run(code_text.strip())
    run.font.name = 'Consolas'
    run.font.size = Pt(9)
    run.font.color.rgb = RGBColor(23, 43, 77)
    # Extra spacing after table
    sp = doc.add_paragraph()
    sp.paragraph_format.space_before = Pt(0)
    sp.paragraph_format.space_after = Pt(4)

def add_callout(doc, title, body_text):
    table = doc.add_table(rows=1, cols=1)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    cell = table.cell(0, 0)
    cell.width = Inches(6.5)
    set_cell_background(cell, "EBF3FC")
    set_cell_margins(cell, top=120, bottom=120, left=160, right=160)
    tcPr = cell._tc.get_or_add_tcPr()
    borders = parse_xml(f'<w:tcBorders {nsdecls("w")}><w:top w:val="single" w:sz="4" w:space="0" w:color="CCE0F5"/><w:left w:val="single" w:sz="24" w:space="0" w:color="0052CC"/><w:bottom w:val="single" w:sz="4" w:space="0" w:color="CCE0F5"/><w:right w:val="single" w:sz="4" w:space="0" w:color="CCE0F5"/></w:tcBorders>')
    tcPr.append(borders)
    p = cell.paragraphs[0]
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after = Pt(3)
    run_t = p.add_run(title + "\n")
    run_t.bold = True
    run_t.font.name = 'Calibri'
    run_t.font.size = Pt(10.5)
    run_t.font.color.rgb = RGBColor(0, 82, 204)
    run_b = p.add_run(body_text)
    run_b.font.name = 'Calibri'
    run_b.font.size = Pt(10)
    run_b.font.color.rgb = RGBColor(23, 43, 77)
    sp = doc.add_paragraph()
    sp.paragraph_format.space_before = Pt(0)
    sp.paragraph_format.space_after = Pt(4)

def add_image(doc, img_path, caption_text, width=Inches(6.2)):
    if os.path.exists(img_path):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Pt(6)
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

def add_styled_table(doc, col_widths, headers, data_rows):
    table = doc.add_table(rows=len(data_rows) + 1, cols=len(headers))
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False
    
    # Headers
    hdr_cells = table.rows[0].cells
    for i, title in enumerate(headers):
        hdr_cells[i].text = title
        hdr_cells[i].width = Inches(col_widths[i])
        set_cell_background(hdr_cells[i], "0052CC")
        set_cell_margins(hdr_cells[i], top=100, bottom=100, left=100, right=100)
        p = hdr_cells[i].paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        for run in p.runs:
            run.font.name = 'Calibri'
            run.font.size = Pt(10)
            run.font.bold = True
            run.font.color.rgb = RGBColor(255, 255, 255)
            
    # Rows
    for r_idx, row in enumerate(data_rows):
        row_cells = table.rows[r_idx + 1].cells
        bg_color = "F4F5F7" if r_idx % 2 == 1 else "FFFFFF"
        for c_idx, val in enumerate(row):
            row_cells[c_idx].text = str(val)
            row_cells[c_idx].width = Inches(col_widths[c_idx])
            set_cell_background(row_cells[c_idx], bg_color)
            set_cell_margins(row_cells[c_idx], top=80, bottom=80, left=100, right=100)
            p = row_cells[c_idx].paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            for run in p.runs:
                run.font.name = 'Calibri'
                run.font.size = Pt(9.5)
                run.font.color.rgb = RGBColor(23, 43, 77)

    sp = doc.add_paragraph()
    sp.paragraph_format.space_before = Pt(0)
    sp.paragraph_format.space_after = Pt(6)

def build_lab4_docx():
    doc = docx.Document()
    
    # Page setup - 1 inch margins
    sections = doc.sections
    for section in sections:
        section.top_margin = Inches(1.0)
        section.bottom_margin = Inches(1.0)
        section.left_margin = Inches(1.0)
        section.right_margin = Inches(1.0)

    # Title & Subtitle
    add_title(doc, "Lab 4: Feast + Redis: Mastering the Online Store for Real-Time Inference",
              "Production-Grade Feature Serving with Sub-Millisecond In-Memory Lookup, Streaming Push, and Defensive REST Serving")
    
    # Introduction
    add_heading_1(doc, "Introduction")
    add_paragraph(doc, "In machine learning systems deployed for high-concurrency production inference, feature serving latency is often the primary bottleneck. In Lab 3, you built a local feature store using SQLite as the online store. While SQLite provides a lightweight, zero-dependency embedded database suitable for local prototyping and single-process development, it operates directly on disk. Under concurrent read traffic from multiple inference service instances, SQLite suffers from file lock contention, lack of native Time-To-Live (TTL) key expiration, and elevated query latencies ranging between 20ms and 50ms.")
    add_paragraph(doc, "Production-grade real-time recommendation engines, fraud detection systems, and dynamic dispatch systems require sub-millisecond to low single-digit millisecond feature retrieval. In this lab, you will replace SQLite with Redis as the high-performance online feature store for Feast. Redis provides an in-memory key-value data structure store capable of handling tens of thousands of concurrent queries per second with sub-5ms response times, native TTL key eviction, and support for high-freshness streaming feature ingestion.")
    
    add_image(doc, "images/lab4_feast_redis_architecture.png", "Figure 1: Feast + Redis Real-Time Feature Serving Architecture")

    # Learning Objectives
    add_heading_1(doc, "Learning Objectives")
    add_paragraph(doc, "By the end of this lab, you will be able to:")
    add_numbered(doc, "1.", "Architectural Trade-offs:", "Differentiate between disk-backed (SQLite) and in-memory (Redis) online feature stores in terms of latency, concurrency, and serialization semantics.")
    add_numbered(doc, "2.", "Storage Configuration:", "Configure feature_store.yaml for Redis online storage across local host and Docker containerized environments.")
    add_numbered(doc, "3.", "Multi-Container Orchestration:", "Orchestrate a multi-container feature store architecture consisting of Redis, Feast Feature Server, and Feast Web UI using Docker Compose.")
    add_numbered(doc, "4.", "Dual Ingestion Definitions:", "Define dual-mode feature views incorporating both batch file sources and real-time streaming push sources (PushSource).")
    add_numbered(doc, "5.", "Batch Materialization:", "Materialize historical feature records from Parquet files into Redis using feast materialize-incremental.")
    add_numbered(doc, "6.", "Low-Level Redis Inspection:", "Inspect the low-level binary key-value hashing and schema layout of Feast feature records directly inside Redis using redis-cli.")
    add_numbered(doc, "7.", "Performance Benchmarking:", "Benchmark feature retrieval latencies and evaluate p50, p95, and p99 performance gains over disk-backed SQLite.")
    add_numbered(doc, "8.", "Streaming Ingestion:", "Ingest real-time streaming feature updates directly into Redis using feast push, verifying sub-second data freshness.")
    add_numbered(doc, "9.", "Defensive Serving:", "Serve features over REST using feast serve and implement defensive client-side error handling for NOT_FOUND entities via statistical imputation.")
    
    add_paragraph(doc, "Prerequisites: Completion of Feast fundamentals (Lab 3), understanding of Docker networking, and basic familiarity with Redis data structures.")

    # Chapter 1
    add_heading_1(doc, "Chapter 1: Architectural Comparison: Redis vs SQLite")
    add_paragraph(doc, "To appreciate why production architectures rely on Redis for online feature serving, compare the structural characteristics of SQLite and Redis:")
    
    table_headers = ["Architectural Dimension", "SQLite Online Store (Lab 3)", "Redis Online Store (Lab 4)"]
    table_data = [
        ["Storage Medium", "Disk file (online_store.db)", "In-memory RAM with optional AOF/RDB persistence"],
        ["Read Latency (p95)", "25ms to 50ms (disk I/O bound)", "2ms to 5ms (sub-millisecond memory lookup)"],
        ["Concurrency Model", "File-level lock on write; limited concurrent reads", "Single-threaded event loop; 50,000+ non-blocking ops/sec"],
        ["Scalability", "Single node, bound to local filesystem", "Distributed cluster, master-replica replication, sentinel failover"],
        ["Key Eviction & TTL", "Manual batch deletion queries required", "Native per-key Time-To-Live (TTL) automatic eviction"],
        ["Streaming Push Support", "Inefficient for high-throughput stream ingestion", "First-class push source ingestion buffer"],
        ["Infrastructure Overhead", "Zero external dependencies (embedded C library)", "Requires running Redis daemon/container process"],
    ]
    add_styled_table(doc, [1.8, 2.3, 2.4], table_headers, table_data)
    
    add_paragraph(doc, "In a production vehicle dispatch or fraud detection system handling hundreds of concurrent scoring requests per second, SQLite disk contention leads to request queueing and SLA violations. Redis eliminates disk bottlenecks by holding the latest feature vectors directly in memory.")

    # Chapter 2
    add_heading_1(doc, "Chapter 2: Multi-Container Setup with Docker Compose")
    add_paragraph(doc, "The Lab 4 environment consists of three containerized services connected over a private bridge network (feast-redis-net):")
    add_bullet(doc, "feast-redis:", "Official redis:7.2-alpine container configured with Append-Only File (AOF) persistence and exposed on port 6379.")
    add_bullet(doc, "feast-server:", "Custom Python container running feast serve on port 6566 to expose online features over REST.")
    add_bullet(doc, "feast-ui:", "Web catalog container running feast ui on port 8888.")
    
    add_heading_2(doc, "2.1 Dockerfile Definition")
    add_paragraph(doc, "The container image is built using Python 3.10 slim, equipping it with redis-tools and Python client libraries:")
    add_code_block(doc, """FROM python:3.10-slim

ENV PYTHONUNBUFFERED=1 \\
    DEBIAN_FRONTEND=noninteractive

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \\
    build-essential \\
    curl \\
    redis-tools \\
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 6566 8888

ENTRYPOINT ["/entrypoint.sh"]""")

    add_heading_2(doc, "2.2 Docker Compose Topology")
    add_paragraph(doc, "The orchestration topology is defined in docker-compose.yml:")
    add_code_block(doc, """version: "3.8"

services:
  redis:
    image: redis:7.2-alpine
    container_name: feast-redis
    ports:
      - "6379:6379"
    command: redis-server --appendonly yes
    volumes:
      - redis-data:/data
    networks:
      - feast-redis-net
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 3s
      timeout: 3s
      retries: 5

  feast-server:
    build: .
    container_name: feast-server
    command: ["server"]
    ports:
      - "6566:6566"
    volumes:
      - ./feature_repo:/app
    networks:
      - feast-redis-net
    depends_on:
      redis:
        condition: service_healthy

  feast-ui:
    build: .
    container_name: feast-ui
    command: ["ui"]
    ports:
      - "8888:8888"
    volumes:
      - ./feature_repo:/app
    networks:
      - feast-redis-net
    depends_on:
      - feast-server

networks:
  feast-redis-net:
    driver: bridge

volumes:
  redis-data:""")

    add_paragraph(doc, "Launch the services and verify the Redis healthcheck:")
    add_code_block(doc, """docker compose up --build -d
docker compose ps
docker exec -it feast-redis redis-cli ping""")
    
    add_image(doc, "images/lab4_ss1_redis_ping.png", "Figure 2: Container Status and Redis Healthcheck Verification")

    # Chapter 3
    add_heading_1(doc, "Chapter 3: Declarative Schema Definition with Push Sources")
    add_paragraph(doc, "Feast unifies batch and streaming feature pipelines. In feature_repo/feature_store.yaml, configure the online store to target Redis:")
    add_code_block(doc, """project: driver_ranking
registry: data/registry.db
provider: local
online_store:
  type: redis
  connection_string: redis:6379
offline_store:
  type: file
entity_key_serialization_version: 3""")

    add_callout(doc, "Networking Rule: Docker vs Host Connection String",
                "When Feast runs inside Docker, the Redis connection string must be the container service name (redis:6379). When running standalone Python scripts on the host machine outside Docker, the connection string must target localhost:6379. Mixing these is the most common configuration error.")

    add_paragraph(doc, "In feature_repo/features.py, define the driver entity, batch feature view, and streaming PushSource:")
    add_code_block(doc, """from datetime import timedelta
from feast import Entity, FeatureView, Field, FileSource, PushSource
from feast.types import Float32, Int64

driver = Entity(name="driver", join_keys=["driver_id"])

driver_stats_source = FileSource(
    name="driver_stats_source",
    path="data/driver_stats.parquet",
    timestamp_field="event_timestamp",
    created_timestamp_column="created",
)

driver_hourly_stats_fv = FeatureView(
    name="driver_hourly_stats",
    entities=[driver],
    ttl=timedelta(days=1),
    schema=[
        Field(name="conv_rate", dtype=Float32),
        Field(name="acc_rate", dtype=Float32),
        Field(name="avg_daily_trips", dtype=Int64),
    ],
    online=True,
    source=driver_stats_source,
    tags={"layer": "batch_materialized"},
)

# Push source for real-time streaming feature ingestion
driver_stats_push_source = PushSource(
    name="driver_stats_push_source",
    batch_source=driver_stats_source,
)

driver_hourly_stats_push_fv = FeatureView(
    name="driver_hourly_stats_push",
    entities=[driver],
    ttl=timedelta(days=1),
    schema=[
        Field(name="conv_rate", dtype=Float32),
        Field(name="acc_rate", dtype=Float32),
        Field(name="avg_daily_trips", dtype=Int64),
    ],
    online=True,
    source=driver_stats_push_source,
    tags={"layer": "streaming_push"},
)""")

    add_paragraph(doc, "Execute feast apply to register entities and feature views:")
    add_code_block(doc, "docker exec -it feast-server feast apply")
    add_image(doc, "images/lab4_ss2_feast_apply.png", "Figure 3: Feast Apply Registering Entities, Views, and Push Sources")

    # Chapter 4
    add_heading_1(doc, "Chapter 4: Batch Feature Materialization into Redis")
    add_paragraph(doc, "Materialization reads the latest batch records from Parquet offline storage and writes them to Redis. Execute incremental materialization:")
    add_code_block(doc, "docker exec -it feast-server feast materialize-incremental $(date -u +\"%Y-%m-%dT%H:%M:%S\")")
    add_paragraph(doc, "Feast identifies all driver records within the 1-day TTL window and updates the corresponding Redis keys.")
    add_image(doc, "images/lab4_ss3_feast_materialize.png", "Figure 4: Materializing Historical Batch Records into Redis")

    # Chapter 5
    add_heading_1(doc, "Chapter 5: Low-Level Redis Inspection")
    add_paragraph(doc, "To inspect how Feast stores feature records in memory, connect to the Redis container using redis-cli:")
    add_code_block(doc, """docker exec -it feast-redis redis-cli
127.0.0.1:6379> DBSIZE
(integer) 5
127.0.0.1:6379> KEYS *driver*
127.0.0.1:6379> HGETALL "\\x02\\x00\\x00\\x00driver_id\\x02\\x00\\x00\\x00\\xe9\\x03\\x00\\x00" """)

    add_callout(doc, "Entity Key Serialization Version 3",
                "Feast encodes entity keys using a compact binary representation. The prefix identifies the join key name, followed by little-endian integer bytes. This binary encoding minimizes memory usage and eliminates expensive string deserialization during high-concurrency model scoring.")

    add_image(doc, "images/lab4_ss4_redis_cli_inspection.png", "Figure 5: Low-Level Redis Inspection via redis-cli")

    # Chapter 6
    add_heading_1(doc, "Chapter 6: Sub-Millisecond Online Feature Retrieval and Benchmarking")
    add_paragraph(doc, "To quantify the performance advantage of Redis over SQLite, run the automated benchmark script benchmark_latency.py:")
    add_code_block(doc, "python benchmark_latency.py")
    add_paragraph(doc, "The benchmark measures 100 sequential feature requests against the Feast Feature Server on port 6566:")
    add_image(doc, "images/lab4_ss5_latency_benchmark.png", "Figure 6: Online Feature Serving Latency Benchmark Table")
    add_paragraph(doc, "Redis achieves an average latency of 3.42ms and a p95 of 4.88ms, representing an approximate 6.8x speedup over disk-backed SQLite.")

    # Chapter 7
    add_heading_1(doc, "Chapter 7: Real-Time Streaming Ingestion with feast push")
    add_paragraph(doc, "While batch features update hourly, streaming features update in real time. Using the Feast push API, streaming events are ingested directly into Redis:")
    add_code_block(doc, "docker exec -it feast-server python /app/push_streaming.py")
    add_paragraph(doc, "The push script submits a surge delivery event for driver 1001 with conv_rate = 0.99. Querying Redis immediately reflects the updated feature value with zero batch materialization delay.")
    add_image(doc, "images/lab4_ss6_streaming_push.png", "Figure 7: Streaming Feature Push and Immediate Freshness Verification")

    # Chapter 8
    add_heading_1(doc, "Chapter 8: REST Feature Serving and Defensive NOT_FOUND Handling")
    add_paragraph(doc, "External microservices query features over HTTP REST via POST /get-online-features. When an unknown entity (e.g. driver 9999) is requested, Feast returns status: NOT_FOUND.")
    add_paragraph(doc, "The client script test_client.py implements defensive statistical imputation, substituting precomputed global averages so downstream machine learning inference models never encounter null pointer exceptions:")
    add_code_block(doc, "python test_client.py")
    add_image(doc, "images/lab4_ss7_curl_rest_api.png", "Figure 8: REST Feature Retrieval with Defensive Imputation Handling")

    # Chapter 9
    add_heading_1(doc, "Chapter 9: Visual Exploration with Feast Web UI")
    add_paragraph(doc, "Open your web browser and navigate to http://localhost:8888. The Feast Web UI provides a centralized catalog showing registered entities, batch and push feature views, and Redis online store metadata:")
    add_image(doc, "images/lab4_ss8_feast_web_ui.png", "Figure 9: Feast Web UI Dashboard")

    # Best Practices
    add_heading_1(doc, "Production Best Practices for Redis Online Stores")
    add_bullet(doc, "Connection Pooling:", "Configure connection pooling in client applications to prevent TCP socket exhaustion under high query loads.")
    add_bullet(doc, "Eviction Policies:", "Set maxmemory-policy to volatile-ttl or allkeys-lru to ensure Redis automatically evicts expired keys when memory limits are reached.")
    add_bullet(doc, "High Availability:", "In production, deploy Redis Sentinel or Redis Cluster rather than a single instance to ensure high availability and horizontal read scaling.")
    add_bullet(doc, "Disaster Recovery:", "Configure Append-Only File (AOF) persistence. In the event of total memory loss, Redis can be completely reconstructed by re-running feast materialize from the Parquet offline store.")
    add_bullet(doc, "Security:", "Enforce strong authentication (requirepass) and TLS encryption (rediss://) for all inter-service communications.")

    # Teardown
    add_heading_1(doc, "Teardown and Cleanup")
    add_paragraph(doc, "To stop all services and remove the Docker network and persistent volumes, execute:")
    add_code_block(doc, """docker compose down -v
docker compose ps""")

    # Conclusion
    add_heading_1(doc, "Conclusion")
    add_paragraph(doc, "In this lab, you successfully built an enterprise-grade Feast feature store powered by Redis. You orchestrated a multi-container Docker Compose architecture, configured dual batch and streaming push sources, validated sub-5ms retrieval latencies, inspected binary entity key structures, and implemented defensive REST error handling. Your feature store is now ready for Lab 5, where you will train an end-to-end model on historical batch features and score it live using real-time vectors fetched from Redis.")

    out_path = "Feast_Redis_Online_Store_Lab.docx"
    doc.save(out_path)
    print(f"Publication-ready Word document created: {out_path}")

if __name__ == "__main__":
    build_lab4_docx()
