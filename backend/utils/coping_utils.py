# backend/utils/coping_utils.py
"""
Coping Toolkit utilities.
Maps detected emotions to appropriate coping exercises.
"""

COPING_MAP = {
    "anxious":      {
        "exercise_type": "breathing",
        "title":    "4-7-8 Breathing",
        "subtitle": "Takes 2 minutes. Proven to reduce anxiety in the moment."
    },
    "overwhelmed":  {
        "exercise_type": "breathing",
        "title":    "4-7-8 Breathing",
        "subtitle": "Takes 2 minutes. Slow your nervous system right now."
    },
    "fearful":      {
        "exercise_type": "breathing",
        "title":    "4-7-8 Breathing",
        "subtitle": "Takes 2 minutes. Grounding breath for fear and panic."
    },
    "sad":          {
        "exercise_type": "gratitude",
        "title":    "Gratitude Moment",
        "subtitle": "Takes 1 minute. Three small things that are still okay."
    },
    "lonely":       {
        "exercise_type": "gratitude",
        "title":    "Gratitude Moment",
        "subtitle": "Takes 1 minute. A gentle reminder you're not invisible."
    },
    "disappointed": {
        "exercise_type": "gratitude",
        "title":    "Gratitude Moment",
        "subtitle": "Takes 1 minute. Acknowledge what's still here, even now."
    },
    "angry":        {
        "exercise_type": "bodyscan",
        "title":    "60-Second Body Scan",
        "subtitle": "60 seconds. Release where anger lives in your body."
    },
    "burnout":      {
        "exercise_type": "bodyscan",
        "title":    "60-Second Body Scan",
        "subtitle": "60 seconds. Check in with your body — it's been carrying a lot."
    },
}


def get_coping_suggestion(primary_emotion: str) -> dict:
    """Return a coping suggestion dict for the given emotion, or show=False if not applicable."""
    try:
        if primary_emotion and primary_emotion.lower() in COPING_MAP:
            return {
                "show":    True,
                "emotion": primary_emotion.lower(),
                **COPING_MAP[primary_emotion.lower()]
            }
        return {"show": False}
    except Exception:
        return {"show": False}
