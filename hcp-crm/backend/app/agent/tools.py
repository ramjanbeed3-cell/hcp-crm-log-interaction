"""
Five LangGraph tools for the HCP Log Interaction agent:

1. log_interaction      - captures a new interaction (structured or free-text),
                           using the LLM to summarize + extract entities.
2. edit_interaction      - modifies a previously logged interaction.
3. fetch_hcp_profile     - retrieves an HCP's profile + recent interaction history,
                           used to ground the agent with context before logging/editing.
4. schedule_followup     - creates a follow-up task tied to an interaction.
5. generate_summary_report - aggregates an HCP's interaction history into a
                           rep-facing summary report (e.g. before a QBR or next visit).
"""

import json
from datetime import datetime, timedelta

from langchain_core.tools import tool
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import HCP, Interaction, FollowUp
from app.llm import get_primary_llm, get_fallback_llm


def _db() -> Session:
    return SessionLocal()


@tool
def log_interaction(
    hcp_id: int,
    raw_text: str,
    interaction_type: str = "visit",
    rep_id: str = "rep_demo",
) -> str:
    """Log a new HCP interaction. `raw_text` is either the free-text/chat description
    of the interaction, or a concatenation of structured form fields. The tool uses the
    LLM to produce a short clinical-sales summary, extract key entities (products
    discussed, sentiment, next steps), and persists everything as a new Interaction row.
    Returns the new interaction_id and the generated summary as a JSON string.
    """
    db = _db()
    try:
        hcp = db.query(HCP).filter(HCP.id == hcp_id).first()
        if not hcp:
            return json.dumps({"error": f"No HCP found with id {hcp_id}"})

        llm = get_primary_llm()
        extraction_prompt = (
            "You are a life-sciences CRM assistant. Given the field rep's raw notes "
            "about a visit/call with a healthcare professional, return a JSON object "
            "with keys: summary (1-2 sentences), products_discussed (comma separated "
            "string), sentiment (positive|neutral|negative), entities (short JSON dict "
            "of any drug names, dosages, objections, or commitments mentioned).\n\n"
            f"HCP: {hcp.name} ({hcp.specialty})\n"
            f"Raw notes: {raw_text}\n\n"
            "Respond ONLY with valid JSON, no markdown fences."
        )
        result = llm.invoke(extraction_prompt)
        try:
            parsed = json.loads(result.content)
        except Exception:
            # Fall back to the heavier model if the small model returns malformed JSON
            result = get_fallback_llm().invoke(extraction_prompt)
            parsed = json.loads(result.content)

        interaction = Interaction(
            hcp_id=hcp_id,
            rep_id=rep_id,
            interaction_type=interaction_type,
            products_discussed=parsed.get("products_discussed", ""),
            notes=raw_text,
            ai_summary=parsed.get("summary", ""),
            ai_entities=json.dumps(parsed.get("entities", {})),
            sentiment=parsed.get("sentiment", "neutral"),
            raw_transcript=raw_text,
            logged_via_chat=True,
        )
        db.add(interaction)
        db.commit()
        db.refresh(interaction)

        return json.dumps(
            {
                "interaction_id": interaction.id,
                "summary": interaction.ai_summary,
                "sentiment": interaction.sentiment,
                "products_discussed": interaction.products_discussed,
            }
        )
    finally:
        db.close()


@tool
def edit_interaction(interaction_id: int, updates: str) -> str:
    """Edit a previously logged interaction. `updates` is a JSON string with any of
    the fields: interaction_type, products_discussed, notes, sentiment. If `notes` is
    updated, the summary is regenerated via the LLM. Returns the updated interaction
    as a JSON string.
    """
    db = _db()
    try:
        interaction = db.query(Interaction).filter(Interaction.id == interaction_id).first()
        if not interaction:
            return json.dumps({"error": f"No interaction found with id {interaction_id}"})

        try:
            fields = json.loads(updates)
        except Exception:
            return json.dumps({"error": "updates must be a valid JSON string"})

        for field in ("interaction_type", "products_discussed", "notes", "sentiment"):
            if field in fields and fields[field] is not None:
                setattr(interaction, field, fields[field])

        if "notes" in fields:
            llm = get_primary_llm()
            resummarize_prompt = (
                "Rewrite this HCP interaction note into a 1-2 sentence sales-CRM "
                f"summary:\n\n{interaction.notes}\n\nRespond with plain text only."
            )
            interaction.ai_summary = llm.invoke(resummarize_prompt).content.strip()

        interaction.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(interaction)

        return json.dumps(
            {
                "interaction_id": interaction.id,
                "interaction_type": interaction.interaction_type,
                "products_discussed": interaction.products_discussed,
                "notes": interaction.notes,
                "ai_summary": interaction.ai_summary,
                "sentiment": interaction.sentiment,
            }
        )
    finally:
        db.close()


@tool
def fetch_hcp_profile(hcp_id: int, history_limit: int = 5) -> str:
    """Fetch an HCP's profile (name, specialty, hospital) plus their most recent
    logged interactions, so the agent has context before logging or editing a new
    interaction. Returns a JSON string.
    """
    db = _db()
    try:
        hcp = db.query(HCP).filter(HCP.id == hcp_id).first()
        if not hcp:
            return json.dumps({"error": f"No HCP found with id {hcp_id}"})

        recent = (
            db.query(Interaction)
            .filter(Interaction.hcp_id == hcp_id)
            .order_by(Interaction.interaction_date.desc())
            .limit(history_limit)
            .all()
        )

        return json.dumps(
            {
                "hcp": {
                    "id": hcp.id,
                    "name": hcp.name,
                    "specialty": hcp.specialty,
                    "hospital": hcp.hospital,
                },
                "recent_interactions": [
                    {
                        "id": i.id,
                        "date": i.interaction_date.isoformat(),
                        "type": i.interaction_type,
                        "summary": i.ai_summary,
                        "sentiment": i.sentiment,
                    }
                    for i in recent
                ],
            }
        )
    finally:
        db.close()


@tool
def schedule_followup(interaction_id: int, days_from_now: int, reason: str) -> str:
    """Create a follow-up task tied to a given interaction, due `days_from_now` days
    from today, with a short `reason` (e.g. 'send updated dosing study'). Returns the
    created follow-up as a JSON string.
    """
    db = _db()
    try:
        interaction = db.query(Interaction).filter(Interaction.id == interaction_id).first()
        if not interaction:
            return json.dumps({"error": f"No interaction found with id {interaction_id}"})

        followup = FollowUp(
            interaction_id=interaction_id,
            due_date=datetime.utcnow() + timedelta(days=days_from_now),
            reason=reason,
        )
        db.add(followup)
        db.commit()
        db.refresh(followup)

        return json.dumps(
            {
                "followup_id": followup.id,
                "interaction_id": interaction_id,
                "due_date": followup.due_date.isoformat(),
                "reason": followup.reason,
            }
        )
    finally:
        db.close()


@tool
def generate_summary_report(hcp_id: int, lookback_days: int = 90) -> str:
    """Generate a rep-facing summary report of an HCP's interaction history over the
    last `lookback_days` days - useful before a next visit or a quarterly business
    review. Uses the LLM to synthesize trends, sentiment trajectory, and open
    follow-ups. Returns a JSON string with the report text.
    """
    db = _db()
    try:
        hcp = db.query(HCP).filter(HCP.id == hcp_id).first()
        if not hcp:
            return json.dumps({"error": f"No HCP found with id {hcp_id}"})

        cutoff = datetime.utcnow() - timedelta(days=lookback_days)
        interactions = (
            db.query(Interaction)
            .filter(Interaction.hcp_id == hcp_id, Interaction.interaction_date >= cutoff)
            .order_by(Interaction.interaction_date.asc())
            .all()
        )

        if not interactions:
            return json.dumps({"report": f"No interactions with {hcp.name} in the last {lookback_days} days."})

        history_text = "\n".join(
            f"- {i.interaction_date.date()} ({i.interaction_type}): {i.ai_summary} "
            f"[sentiment: {i.sentiment}, products: {i.products_discussed}]"
            for i in interactions
        )

        prompt = (
            f"Summarize the following interaction history with Dr. {hcp.name} "
            f"({hcp.specialty}) into a short report for a field rep: key products "
            "discussed, sentiment trend, open concerns, and a recommended focus for "
            f"the next visit.\n\nHistory:\n{history_text}"
        )
        report = get_fallback_llm().invoke(prompt).content.strip()

        return json.dumps({"hcp": hcp.name, "interactions_considered": len(interactions), "report": report})
    finally:
        db.close()


ALL_TOOLS = [
    log_interaction,
    edit_interaction,
    fetch_hcp_profile,
    schedule_followup,
    generate_summary_report,
]
