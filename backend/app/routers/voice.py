from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from .. import schemas, services
from ..database import get_db


router = APIRouter(prefix="/voice", tags=["voice"])


@router.post("/command", response_model=schemas.VoiceResponse)
async def voice_command(payload: schemas.VoiceCommand, db: Session = Depends(get_db)):
    return await services.handle_voice(db, payload.text)
