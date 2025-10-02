from __future__ import annotations

from typing import Any, Dict, List


def filter_researcher_evidence_for_ssot(
    personas_ssot: List[Dict[str, Any]],
    transcript: Any = None,
    original_text: Any = None,
) -> List[Dict[str, Any]]:
    """Remove Researcher/Interviewer quotes from persona evidence (pure).

    Mirrors legacy ResultsService._filter_researcher_evidence_for_ssot behavior.
    """
    if not personas_ssot:
        return personas_ssot
    try:
        from backend.services.validation.persona_evidence_validator import (
            PersonaEvidenceValidator,
        )
        import re  # local import to avoid global dependency when unused

        validator = PersonaEvidenceValidator()

        # Build normalized corpus of Researcher/Interviewer dialogues
        researcher_texts_norm: List[str] = []
        if isinstance(transcript, list):
            for seg in transcript:
                sp = (
                    (seg.get("speaker") or "").strip().lower()
                    if isinstance(seg, dict)
                    else ""
                )
                if sp in {"researcher", "interviewer", "moderator"}:
                    dialogue = (
                        (seg.get("dialogue") if isinstance(seg, dict) else None)
                        or (seg.get("text") if isinstance(seg, dict) else None)
                        or ""
                    )
                    researcher_texts_norm.append(validator._normalize(dialogue))
        elif isinstance(original_text, str) and original_text.strip():
            for line in original_text.splitlines():
                if re.match(
                    r"^(researcher|interviewer|moderator)\s*:\s*",
                    line.strip(),
                    re.IGNORECASE,
                ):
                    content = re.sub(
                        r"^(researcher|interviewer|moderator)\s*:\s*",
                        "",
                        line.strip(),
                        flags=re.IGNORECASE,
                    )
                    researcher_texts_norm.append(validator._normalize(content))

        def is_researcher_quote(q: str) -> bool:
            if not q:
                return False
            qn = validator._normalize(q)
            return any(qn in d for d in researcher_texts_norm)

        cleaned: List[Dict[str, Any]] = []
        fields = [
            "demographics",
            "goals_and_motivations",
            "challenges_and_frustrations",
            "key_quotes",
        ]
        for p in personas_ssot:
            p2 = dict(p) if isinstance(p, dict) else p
            for f in fields:
                trait = p2.get(f)
                if isinstance(trait, dict) and "evidence" in trait:
                    ev = trait.get("evidence") or []
                    new_ev = []
                    for item in ev:
                        quote = (
                            item.get("quote")
                            if isinstance(item, dict)
                            else (item if isinstance(item, str) else None)
                        )
                        if quote is None:
                            continue
                        if not is_researcher_quote(quote):
                            new_ev.append(item)
                    trait["evidence"] = new_ev
            cleaned.append(p2)
        return cleaned
    except Exception:
        # Be conservative and return original if anything fails
        return personas_ssot


def inject_age_ranges_from_source(
    personas_ssot: List[Dict[str, Any]],
    transcript: Any = None,
    original_text: Any = None,
) -> List[Dict[str, Any]]:
    """Inject demographics.age_range.value based on simple age parsing from source.

    Mirrors legacy ResultsService._inject_age_ranges_from_source behavior.
    """
    try:
        import re

        ages: List[int] = []

        def extract_ages_from_text(s: str) -> List[int]:
            if not isinstance(s, str):
                return []
            found: List[int] = []
            for m in re.finditer(
                r"\b(?:age\s*[:=]\s*(\d{2})|(\d{2})\s*years?\s*old|(\d{2})\s*yo|(?:\(|,)\s*(\d{2})\s*(?:\)|,))\b",
                s,
                re.IGNORECASE,
            ):
                age = next((int(g) for g in m.groups() if g), None)
                if age and 15 <= age <= 100:
                    found.append(age)
            return found

        if isinstance(transcript, list):
            for seg in transcript:
                text = (
                    (seg.get("dialogue") if isinstance(seg, dict) else None)
                    or (seg.get("text") if isinstance(seg, dict) else None)
                    or ""
                ).strip()
                if text:
                    ages.extend(extract_ages_from_text(text))
        if not ages and isinstance(original_text, str):
            ages.extend(extract_ages_from_text(original_text))

        ages = [a for a in ages if 15 <= a <= 100]
        if not ages:
            return personas_ssot

        ages.sort()
        min_age, max_age = ages[0], ages[-1]
        if len(ages) == 1:
            center = ages[0]
            label = f"{max(center-2,15)}–{min(center+2,100)}"
        else:
            if max_age - min_age <= 4:
                label = f"{min_age}–{max_age}"
            else:
                mid = ages[len(ages) // 2]
                low = max(mid - 2, 15)
                high = min(mid + 2, 100)
                label = f"{low}–{high}"

        for p in personas_ssot:
            if not isinstance(p, dict):
                continue
            demo = p.get("demographics")
            if not isinstance(demo, dict):
                continue
            age_field = demo.get("age_range") or {}
            current_val = (
                age_field.get("value") if isinstance(age_field, dict) else None
            ) or ""
            if str(current_val).strip().lower() in {
                "",
                "n/a",
                "undisclosed",
                "not specified",
                "unknown",
            }:
                if not isinstance(age_field, dict):
                    age_field = {}
                age_field["value"] = label
                demo["age_range"] = age_field
        return personas_ssot
    except Exception:
        return personas_ssot

