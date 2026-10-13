# Cross-Insurer Fraud Detection & Claim Deduplication Framework

A privacy-preserving, distributed framework for detecting exact duplicate claims and near-duplicate fraud across multiple competing insurance providers (consortium) without leaking PII or raw claim details.

---

## 🏛 Architecture Overview

```
                                 [ Insurer Nodes ]
                                        │
                                        ▼
                        ┌───────────────────────────────┐
                        │   API Gateway (Port 8000)     │
                        │   - Reverse Proxy & Routing   │
                        │   - Dashboard Static Host     │
                        └───────┬───────────────┬───────┘
                                │               │
                ┌───────────────┘               └───────────────┐
                ▼                                               ▼
   ┌─────────────────────────┐                     ┌─────────────────────────┐
   │ Ingestion Service (8004)│                     │ Decision Service (8003) │
   │ - Batch Claim JSON      │                     │ - Pipeline Orchestrator │
   │ - Bulk CSV Upload       │                     │ - Postgres & Storage    │
   └────────────┬────────────┘                     └────────────┬────────────┘
                │                                               │
                └───────────────────────┬───────────────────────┘
                                        │
                     ┌──────────────────┴──────────────────┐
                     ▼                                     ▼
        ┌─────────────────────────┐           ┌─────────────────────────┐
        │Fingerprint Service(8001)│           │ Similarity Service(8002)│
        │- Deterministic Normaliz.│           │ - Amount diff heuristic │
        │- SHA-256 Consortium Salt│           │ - Date delta distance   │
        │- PII Hashing (SSN, etc) │           │ - Text fuzzy matching   │
        └─────────────────────────┘           └─────────────────────────┘
                     │                                     │
                     ▼                                     ▼
        ┌─────────────────────────┐           ┌─────────────────────────┐
        │   ClaimRegistry.sol     │           │   PostgreSQL Database   │
        │ - Blockchain Registry   │           │ - Historical Claims DB  │
        │ - DuplicateAlert events │           │ - pgdata persistent vol │
        └─────────────────────────┘           └─────────────────────────┘
```

---

## 🚀 Microservices Breakdown

| Service | Port | Description |
| :--- | :--- | :--- |
| **Gateway** | `8000` | Unified API entrypoint, health diagnostics, and dashboard host. |
| **Fingerprint Service** | `8001` | Canonicalizes claim attributes, hashes PII (SSN), and generates deterministic salted SHA-256 hashes. |
| **Similarity Service** | `8002` | Computes fuzzy similarity scores across amounts, incident dates, and descriptions. |
| **Decision Service** | `8003` | Orchestrates the deduplication pipeline, checks exact registry, runs near-duplicate matching, and registers claims. |
| **Ingestion Service** | `8004` | Batch processing and bulk CSV upload support. |
| **PostgreSQL** | `5432` | Durable database for claim history and exact hash registry. |

---

## ⚙️ Quick Start

### Option A: Run with Docker Compose (Recommended)

Start all services, database, and the web dashboard with a single command:

```bash
docker compose up --build
```

- Open the Dashboard: **[http://localhost:8000](http://localhost:8000)**
- Health check: **[http://localhost:8000/health](http://localhost:8000/health)**

---

### Option B: Run Locally with Virtualenv

1. Create and activate a Python virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

2. Run the end-to-end pipeline test script:
   ```bash
   chmod +x run_all.sh
   ./run_all.sh
   ```

3. Open `dashboard/index.html` in your web browser.

---

## 🧪 Synthetic Dataset Generation & Testing

Generate synthetic claims with Faker:
```bash
python scripts/generate_synthetic_dataset.py --count 1000 --output claims.csv
```

Inject exact and near duplicates with configurable perturbation rates:
```bash
python scripts/inject_duplicates.py --input claims.csv --output final_claims.csv --ground_truth truth.csv --rate 0.15
```

You can then drag and drop `final_claims.csv` directly into the Dashboard's **Batch Ingestion** panel or post to `/ingest/csv`.

---

## 📜 Smart Contract Deployment

To deploy `contracts/ClaimRegistry.sol` to a local test network (e.g., Hardhat, Ganache, Anvil):

```bash
pip install web3
python scripts/deploy_contract.py
```

---

## 🛣 Future Roadmap

- [ ] Sentence-Transformers / Vector Embeddings for semantic incident description matching.
- [ ] Multimodal photo verification (perceptual hashing & EXIF metadata on damage images).
- [ ] Zero-Knowledge Proofs (ZK-SNARKs) for cross-insurer verification without data exposure.
- [ ] Neo4j Graph Neural Networks for cross-insurer fraud ring detection.
