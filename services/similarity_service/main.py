try:
    from .models import SimilarityRequest, SimilarityResponse
    from .matcher import calculate_similarity
except (ImportError, ValueError):
    from models import SimilarityRequest, SimilarityResponse
    from matcher import calculate_similarity

app = FastAPI(title="Similarity Service")

@app.post("/similarity", response_model=SimilarityResponse)
def evaluate_similarity(payload: SimilarityRequest):
    score = calculate_similarity(payload.claim1, payload.claim2)
    # Threshold for near duplicate is arbitrarily set to 0.85
    is_near_duplicate = score > 0.85
    return SimilarityResponse(
        similarity_score=score,
        is_near_duplicate=is_near_duplicate
    )
