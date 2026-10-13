import requests
import os
try:
    from .models import Claim, EvaluationResponse
    from .storage import claim_store
except (ImportError, ValueError):
    from models import Claim, EvaluationResponse
    from storage import claim_store

# Service URLs from docker-compose network, fallback to localhost for direct testing
FINGERPRINT_SERVICE_URL = os.getenv("FINGERPRINT_SERVICE_URL", "http://fingerprint_service:8000/fingerprint")
SIMILARITY_SERVICE_URL = os.getenv("SIMILARITY_SERVICE_URL", "http://similarity_service:8000/similarity")

# Expose for backward compatibility
mock_blockchain_registry = claim_store.mock_registry
mock_claims_db = claim_store.mock_claims

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
    if claim_store.has_hash(exact_hash):
        return EvaluationResponse(
            claim_id=claim.claim_id,
            status="EXACT_DUPLICATE",
            confidence=1.0,
            exact_hash=exact_hash
        )

    # 3. Check near duplicates against local database
    max_similarity = 0.0
    past_claims = claim_store.get_all_claims()
    for past_claim in past_claims:
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
    claim_store.add_hash(exact_hash)
    claim_store.add_claim(claim)
    
    return EvaluationResponse(
        claim_id=claim.claim_id,
        status="UNIQUE",
        confidence=1.0,
        exact_hash=exact_hash,
        similarity_score=max_similarity
    )
