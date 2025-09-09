from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Any
from agents.llm_utils import moderate_message_with_llm

@dataclass
class ChatModerator:
    def moderate(self, message: str) -> Dict[str, Any]:
        explanation= moderate_message_with_llm(message)
        if "Status:" in explanation and "Reason:" in explanation:
            try:
                status_part, reason_part = explanation.split("|", 1)
                status = status_part.replace("Status:", "").strip()
                reason = reason_part.replace("Reason:", "").strip()
                return {"status": status, "reason": reason}
            except Exception:
                # fallback: just treat as safe
                return {"status": "safe", "reason": explanation}
        else:
            return {"status": "safe", "reason": explanation}