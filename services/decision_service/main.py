from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .models import Claim, EvaluationResponse
from .orchestrator import evaluate, mock_blockchain_registry, mock_claims_db

app = FastAPI(title="Decision Service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/evaluate_claim", response_model=EvaluationResponse)
def evaluate_claim(claim: Claim):
    return evaluate(claim)

@app.get("/debug/registry")
def get_registry():
    return {"registered_hashes": list(mock_blockchain_registry)}

@app.get("/debug/db")
def get_db():
    return {"stored_claims": [c.dict() for c in mock_claims_db]}

@app.delete("/debug/reset")
def reset_mocks():
    mock_blockchain_registry.clear()
    mock_claims_db.clear()
    return {"status": "reset"}
