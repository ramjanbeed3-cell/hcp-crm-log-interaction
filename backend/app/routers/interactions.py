from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app import models, schemas

router = APIRouter(prefix="/api", tags=["interactions"])


@router.get("/hcps", response_model=list[schemas.HCPOut])
def list_hcps(db: Session = Depends(get_db)):
    return db.query(models.HCP).all()


@router.post("/hcps", response_model=schemas.HCPOut)
def create_hcp(payload: schemas.HCPCreate, db: Session = Depends(get_db)):
    hcp = models.HCP(**payload.model_dump())
    db.add(hcp)
    db.commit()
    db.refresh(hcp)
    return hcp


@router.get("/interactions", response_model=list[schemas.InteractionOut])
def list_interactions(hcp_id: int | None = None, db: Session = Depends(get_db)):
    q = db.query(models.Interaction)
    if hcp_id:
        q = q.filter(models.Interaction.hcp_id == hcp_id)
    return q.order_by(models.Interaction.interaction_date.desc()).all()


@router.post("/interactions", response_model=schemas.InteractionOut)
def create_interaction(payload: schemas.InteractionCreate, db: Session = Depends(get_db)):
    """Structured-form submission path (non-chat). Still runs the note through the
    same LLM summarization used by the chat/log_interaction tool, for consistency."""
    from app.agent.tools import log_interaction

    hcp = db.query(models.HCP).filter(models.HCP.id == payload.hcp_id).first()
    if not hcp:
        raise HTTPException(status_code=404, detail="HCP not found")

    raw_text = payload.notes or ""
    if payload.products_discussed:
        raw_text += f"\nProducts discussed: {payload.products_discussed}"
    if payload.attendees:
        raw_text += f"\nAttendees: {payload.attendees}"
    if payload.materials_shared:
        raw_text += f"\nMaterials shared: {payload.materials_shared}"
    if payload.samples_distributed:
        raw_text += f"\nSamples distributed: {payload.samples_distributed}"
    if payload.outcomes:
        raw_text += f"\nOutcomes: {payload.outcomes}"
    if payload.follow_up_actions:
        raw_text += f"\nFollow-up actions: {payload.follow_up_actions}"

    result_json = log_interaction.invoke(
        {
            "hcp_id": payload.hcp_id,
            "raw_text": raw_text,
            "interaction_type": payload.interaction_type,
            "rep_id": payload.rep_id,
        }
    )
    import json

    result = json.loads(result_json)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])

    interaction = (
        db.query(models.Interaction).filter(models.Interaction.id == result["interaction_id"]).first()
    )

    # Persist the granular structured fields + any explicit rep sentiment override
    interaction.attendees = payload.attendees
    interaction.materials_shared = payload.materials_shared
    interaction.samples_distributed = payload.samples_distributed
    interaction.outcomes = payload.outcomes
    interaction.follow_up_actions = payload.follow_up_actions
    if payload.user_sentiment:
        interaction.user_sentiment = payload.user_sentiment
        interaction.sentiment = payload.user_sentiment  # rep's explicit choice takes priority
    db.commit()
    db.refresh(interaction)

    return interaction


@router.patch("/interactions/{interaction_id}", response_model=schemas.InteractionOut)
def update_interaction(interaction_id: int, payload: schemas.InteractionUpdate, db: Session = Depends(get_db)):
    interaction = db.query(models.Interaction).filter(models.Interaction.id == interaction_id).first()
    if not interaction:
        raise HTTPException(status_code=404, detail="Interaction not found")

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(interaction, field, value)

    db.commit()
    db.refresh(interaction)
    return interaction
