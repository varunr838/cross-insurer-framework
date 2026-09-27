from .models import Claim
from dateutil import parser
from difflib import SequenceMatcher
import math

def calculate_similarity(claim1: Claim, claim2: Claim) -> float:
    score = 0.0
    weights = {
        "amount": 0.4,
        "date": 0.3,
        "description": 0.3
    }
    
    # 1. Amount Similarity
    amt1 = claim1.claim_amount
    amt2 = claim2.claim_amount
    max_amt = max(amt1, amt2)
    if max_amt > 0:
        amt_diff = abs(amt1 - amt2)
        # If amount diff is less than 5%, it's very similar
        amt_score = max(0, 1.0 - (amt_diff / max_amt))
    else:
        amt_score = 1.0
    score += weights["amount"] * amt_score

    # 2. Date Similarity
    try:
        date1 = parser.parse(claim1.incident_date)
        date2 = parser.parse(claim2.incident_date)
        days_diff = abs((date1 - date2).days)
        # Max penalty after 7 days
        date_score = max(0, 1.0 - (days_diff / 7.0))
    except Exception:
        date_score = 0.0
    score += weights["date"] * date_score

    # 3. Description Similarity
    desc1 = claim1.description.lower().strip()
    desc2 = claim2.description.lower().strip()
    desc_score = SequenceMatcher(None, desc1, desc2).ratio()
    score += weights["description"] * desc_score

    return score
