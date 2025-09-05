# Conversation Routines (2025 Framework)

Last Updated: 2025-09-05

This service provides an interactive research chat that follows the 2025 Conversation Routines framework.

- Endpoint prefix: `/api/research/conversation-routines`
- Primary endpoints:
  - `POST /chat` – Interactive research chat
  - `GET /health` – Service health check

## Design

- Single-LLM call with embedded workflow logic (no multi-step orchestration)
- Proactive transition to question generation with fatigue detection
- Stakeholder-aware suggestions

## Auth

- Uses the standard authentication middleware (Clerk)

## See also

- Router: `router.py`
- Service: `service.py`
