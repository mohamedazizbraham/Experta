from typing import Any, Dict, List, Optional

from fastapi import FastAPI
from pydantic import BaseModel, Field

from service import decide

app = FastAPI(title="Experta Decision API", version="1.0.0")


class DecideRequest(BaseModel):
    symptomes: List[str] = Field(..., description="Ex: ['stress', 'fatigue']")
    conditions_medicales: List[str] = Field(default_factory=list, description="Ex: ['grossesse']")


class DecideResponse(BaseModel):
    input: Dict[str, Any]
    best_decision: Optional[Dict[str, Any]]
    recommendations: List[Dict[str, Any]]
    forbidden_products: List[str]
    unknown_symptomes: List[str]
    unknown_conditions: List[str]


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/decide", response_model=DecideResponse)
def decide_endpoint(req: DecideRequest):
    return decide(req.symptomes, req.conditions_medicales)


# run directly with python api.py
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api:app", host="127.0.0.1", port=8000, reload=True)
