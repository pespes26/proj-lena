from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Optional
from auth import get_current_user
from services.ai_agents import chat_stream, _build_projects_context, SYSTEM_PROMPT
from services.calculator_agent import run_whatif, calc_risk_score, calc_all_risk_scores, calc_budget_vs_actual

router = APIRouter(dependencies=[Depends(get_current_user)])


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    messages: List[ChatMessage] = []
    message: str


@router.post("/api/ai/chat")
def ai_chat(req: ChatRequest):
    history = [{"role": m.role, "content": m.content} for m in req.messages]
    return StreamingResponse(
        chat_stream(history, req.message),
        media_type="text/event-stream",
    )


class WhatIfRequest(BaseModel):
    project_name: str
    modifications: dict = {}


@router.post("/api/ai/whatif")
def whatif_simulation(req: WhatIfRequest):
    result = run_whatif(req.project_name, req.modifications)
    if not result:
        raise HTTPException(status_code=404, detail="פרויקט לא נמצא")
    return result


@router.get("/api/ai/risk-scores")
def get_all_risk_scores_endpoint():
    return {"scores": calc_all_risk_scores()}


@router.get("/api/ai/risk-score/{project}")
def get_risk_score_endpoint(project: str):
    result = calc_risk_score(project)
    if not result:
        raise HTTPException(status_code=404, detail="פרויקט לא נמצא")
    return result


@router.get("/api/ai/budget-vs-actual/{project}")
def get_budget_vs_actual_endpoint(project: str):
    result = calc_budget_vs_actual(project)
    if not result:
        raise HTTPException(status_code=404, detail="פרויקט לא נמצא")
    return result
