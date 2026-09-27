import requests
import os
from .models import Claim, EvaluationResponse

# Service URLs from docker-compose network, fallback to localhost for direct testing
FINGERPRINT_SERVICE_URL = os.getenv("FINGERPRINT_SERVICE_URL", "http://fingerprint_service:8000/fingerprint")
SIMILARITY_SERVICE_URL = os.getenv("SIMILARITY_SERVICE_URL", "http://similarity_service:8000/similarity")

# In-memory mock databases for testing
# Mocks the blockchain registry
mock_blockchain_registry = set()
# Mocks the local operational database of claims
mock_claims_db = []

def evaluate(claim: Claim) -> EvaluationResponse:
    # 1. Fingerprint the claim
    try:
        resp = requests.post(FINGERPRINT_SERVICE_URL, json=claim.dict(), timeout=5)
        resp.raise_for_status()
        exact_hash = resp.json()["exact_hash"]
    except Exception as e:
        print(f"Error calling fingerprint service: {e}")
        return EvaluationResponse(claim_id=claim.claim_id, status="ERROR", confidence=0.0)

    # 2. Check exact match on blockchain registry
    if exact_hash in mock_blockchain_registry:
        return EvaluationResponse(
            claim_id=claim.claim_id,
            status="EXACT_DUPLICATE",
            confidence=1.0,
            exact_hash=exact_hash
        )

    # 3. Check near duplicates against local database
    max_similarity = 0.0
    for past_claim in mock_claims_db:
        # Don't compare with self if it's the same exact claim ID from same insurer
        if past_claim.claim_id == claim.claim_id and past_claim.insurer_id == claim.insurer_id:
            continue
            
        try:
            payload = {
                "claim1": claim.dict(),
                "claim2": past_claim.dict()
            }
            resp = requests.post(SIMILARITY_SERVICE_URL, json=payload, timeout=5)
            resp.raise_for_status()
            sim_score = resp.json()["similarity_score"]
            if sim_score > max_similarity:
                max_similarity = sim_score
        except Exception as e:
            print(f"Error calling similarity service: {e}")
            pass
            
    if max_similarity > 0.85:
        return EvaluationResponse(
            claim_id=claim.claim_id,
            status="NEAR_DUPLICATE",
            confidence=max_similarity,
            exact_hash=exact_hash,
            similarity_score=max_similarity
        )

    # 4. If unique, register hash on blockchain and save to local DB
    mock_blockchain_registry.add(exact_hash)
    mock_claims_db.append(claim)
    
    return EvaluationResponse(
        claim_id=claim.claim_id,
        status="UNIQUE",
        confidence=1.0,
        exact_hash=exact_hash,
        similarity_score=max_similarity
    )
