from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import os
from supabase import create_client, Client
import json

app = FastAPI()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Supabase setup
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise Exception("Missing Supabase credentials")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

class MatchState(BaseModel):
    team_a_score: int = 0
    team_b_score: int = 0
    team_a_selected: List[int] = []
    team_b_selected: List[int] = []
    team_a_history: List[int] = []
    team_b_history: List[int] = []
    winner: Optional[str] = None

class ScoreRequest(BaseModel):
    team: str  # 'A' or 'B'
    number: int

class UndoRequest(BaseModel):
    team: str  # 'A' or 'B'

class ResetRequest(BaseModel):
    pass

@app.get("/")
async def root():
    return {"message": "Billiards Scoring API"}

@app.get("/api/match")
async def get_match():
    try:
        response = supabase.table("matches").select("*").eq("id", 1).execute()
        
        if response.data:
            match_data = response.data[0]
            return {
                "team_a_score": match_data.get("team_a_score", 0),
                "team_b_score": match_data.get("team_b_score", 0),
                "team_a_selected": match_data.get("team_a_selected", []),
                "team_b_selected": match_data.get("team_b_selected", []),
                "team_a_history": match_data.get("team_a_history", []),
                "team_b_history": match_data.get("team_b_history", []),
                "winner": match_data.get("winner")
            }
        else:
            # Create initial match state
            initial_state = {
                "team_a_score": 0,
                "team_b_score": 0,
                "team_a_selected": [],
                "team_b_selected": [],
                "team_a_history": [],
                "team_b_history": [],
                "winner": None
            }
            supabase.table("matches").insert(initial_state).execute()
            return initial_state
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/score")
async def add_score(request: ScoreRequest):
    try:
        # Get current match state
        response = supabase.table("matches").select("*").eq("id", 1).execute()
        if not response.data:
            raise HTTPException(status_code=404, detail="Match not found")
        
        match = response.data[0]
        
        # Check if there's already a winner
        if match.get("winner"):
            raise HTTPException(status_code=400, detail="Match already finished")
        
        # Update based on team
        if request.team == "A":
            if request.number in match.get("team_a_selected", []):
                raise HTTPException(status_code=400, detail="Number already selected")
            
            new_score = match.get("team_a_score", 0) + request.number
            new_selected = match.get("team_a_selected", []) + [request.number]
            new_history = match.get("team_a_history", []) + [request.number]
            
            # Check for winner
            winner = "A" if new_score >= 60 else None
            
            # Update match
            supabase.table("matches").update({
                "team_a_score": new_score,
                "team_a_selected": new_selected,
                "team_a_history": new_history,
                "winner": winner
            }).eq("id", 1).execute()
            
            return {
                "team_a_score": new_score,
                "team_b_score": match.get("team_b_score", 0),
                "team_a_selected": new_selected,
                "team_b_selected": match.get("team_b_selected", []),
                "team_a_history": new_history,
                "team_b_history": match.get("team_b_history", []),
                "winner": winner
            }
            
        elif request.team == "B":
            if request.number in match.get("team_b_selected", []):
                raise HTTPException(status_code=400, detail="Number already selected")
            
            new_score = match.get("team_b_score", 0) + request.number
            new_selected = match.get("team_b_selected", []) + [request.number]
            new_history = match.get("team_b_history", []) + [request.number]
            
            # Check for winner
            winner = "B" if new_score >= 60 else None
            
            # Update match
            supabase.table("matches").update({
                "team_b_score": new_score,
                "team_b_selected": new_selected,
                "team_b_history": new_history,
                "winner": winner
            }).eq("id", 1).execute()
            
            return {
                "team_a_score": match.get("team_a_score", 0),
                "team_b_score": new_score,
                "team_a_selected": match.get("team_a_selected", []),
                "team_b_selected": new_selected,
                "team_a_history": match.get("team_a_history", []),
                "team_b_history": new_history,
                "winner": winner
            }
        else:
            raise HTTPException(status_code=400, detail="Invalid team")
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/undo")
async def undo_score(request: UndoRequest):
    try:
        # Get current match state
        response = supabase.table("matches").select("*").eq("id", 1).execute()
        if not response.data:
            raise HTTPException(status_code=404, detail="Match not found")
        
        match = response.data[0]
        
        # Update based on team
        if request.team == "A":
            history = match.get("team_a_history", [])
            if not history:
                raise HTTPException(status_code=400, detail="No moves to undo")
            
            last_number = history[-1]
            new_history = history[:-1]
            new_score = match.get("team_a_score", 0) - last_number
            new_selected = match.get("team_a_selected", [])[:-1]
            
            # Remove winner if score goes below 60
            winner = None if new_score < 60 else match.get("winner")
            
            # Update match
            supabase.table("matches").update({
                "team_a_score": new_score,
                "team_a_selected": new_selected,
                "team_a_history": new_history,
                "winner": winner
            }).eq("id", 1).execute()
            
            return {
                "team_a_score": new_score,
                "team_b_score": match.get("team_b_score", 0),
                "team_a_selected": new_selected,
                "team_b_selected": match.get("team_b_selected", []),
                "team_a_history": new_history,
                "team_b_history": match.get("team_b_history", []),
                "winner": winner
            }
            
        elif request.team == "B":
            history = match.get("team_b_history", [])
            if not history:
                raise HTTPException(status_code=400, detail="No moves to undo")
            
            last_number = history[-1]
            new_history = history[:-1]
            new_score = match.get("team_b_score", 0) - last_number
            new_selected = match.get("team_b_selected", [])[:-1]
            
            # Remove winner if score goes below 60
            winner = None if new_score < 60 else match.get("winner")
            
            # Update match
            supabase.table("matches").update({
                "team_b_score": new_score,
                "team_b_selected": new_selected,
                "team_b_history": new_history,
                "winner": winner
            }).eq("id", 1).execute()
            
            return {
                "team_a_score": match.get("team_a_score", 0),
                "team_b_score": new_score,
                "team_a_selected": match.get("team_a_selected", []),
                "team_b_selected": new_selected,
                "team_a_history": match.get("team_a_history", []),
                "team_b_history": new_history,
                "winner": winner
            }
        else:
            raise HTTPException(status_code=400, detail="Invalid team")
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/reset")
async def reset_match():
    try:
        # Reset match state
        reset_state = {
            "team_a_score": 0,
            "team_b_score": 0,
            "team_a_selected": [],
            "team_b_selected": [],
            "team_a_history": [],
            "team_b_history": [],
            "winner": None
        }
        
        supabase.table("matches").update(reset_state).eq("id", 1).execute()
        
        return reset_state
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
