# app/routes/vocab.py

from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
from app.models.user_model import VocabCard, VocabProficiency
from app.services.vocab_service import (
    list_vocab_cards,
    add_vocab_card,
    update_vocab_card,
    delete_vocab_card,
    fetch_words_from_external_api,
    get_practice_batch,
    process_practice_result,
)
from app.utils.supabase_auth import get_current_user_data

router = APIRouter()


# ----------------------------
# Request / Response Models
# ----------------------------

class AddCardRequest(BaseModel):
    word: str
    meaning: Optional[str] = None
    example: Optional[str] = None


class UpdateCardRequest(BaseModel):
    meaning: Optional[str] = None
    example: Optional[str] = None
    level: Optional[int] = None


class PracticeAnswer(BaseModel):
    word: str
    correct: bool
    time_ms: Optional[int] = None


# ----------------------------
# CRUD Endpoints
# ----------------------------

@router.get("/cards", response_model=List[VocabCard])
async def get_cards(current_user: dict = Depends(get_current_user_data)):
    try:
        return list_vocab_cards(current_user["username"])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/cards", response_model=VocabCard, status_code=status.HTTP_201_CREATED)
async def create_card(req: AddCardRequest, current_user: dict = Depends(get_current_user_data)):
    card = VocabCard(
        word=req.word,
        meaning=req.meaning,
        example=req.example,
        added_at=datetime.utcnow(),
    )
    try:
        return add_vocab_card(current_user["username"], card)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/cards/{word}", response_model=dict)
async def patch_card(word: str, req: UpdateCardRequest, current_user: dict = Depends(get_current_user_data)):
    patch = {k: v for k, v in req.model_dump().items() if v is not None}
    try:
        return update_vocab_card(current_user["username"], word, patch)
    except KeyError:
        raise HTTPException(status_code=404, detail="Card not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/cards/{word}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_card(word: str, current_user: dict = Depends(get_current_user_data)):
    try:
        delete_vocab_card(current_user["username"], word)
        return {"detail": "deleted"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ----------------------------
# Practice Endpoints
# ----------------------------

@router.get("/recommendations", response_model=List[dict])
async def recommendations(
    count: int = Query(20, ge=1, le=100),
    proficiency: VocabProficiency = VocabProficiency.BEGINNER,
    current_user: dict = Depends(get_current_user_data),
):
    words = await fetch_words_from_external_api(count=count, proficiency=proficiency.value)
    return words


@router.get("/practice", response_model=List[dict])
async def practice_batch(
    batch_size: int = Query(10, ge=1, le=50),
    current_user: dict = Depends(get_current_user_data),
):
    return get_practice_batch(current_user["username"], batch_size)


@router.post("/practice/answer", response_model=dict)
async def practice_answer(payload: PracticeAnswer, current_user: dict = Depends(get_current_user_data)):
    try:
        res = process_practice_result(
            current_user["username"], payload.word, payload.correct, payload.time_ms
        )
        return res
    except KeyError:
        raise HTTPException(status_code=404, detail="Card not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
