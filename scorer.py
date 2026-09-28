"""
Unit 2: deciding what counts as a correct answer.

`judge(question, expects, answer, results) -> bool` is what run_eval.py looks
for. Each of my five questions fails in its own specific way, so this isn't
one generic check against `expects` — it's five small, question-specific
rules, one per `_judge_*` function below, decided by working through what a
wrong answer would actually look like for each question before writing any
code.

`expects` is kept as a parameter (matching the signature run_eval.py expects)
but isn't used directly here — the real "expected answer" logic is baked into
each per-question rule instead, since none of my five `expects` strings are
safe to substring-match on their own.
"""

import re

from gate import REFUSAL


def _is_refusal(answer: str) -> bool:
    return REFUSAL.lower() in answer.lower()


def _judge_dining_dollars(answer: str) -> bool:
    if _is_refusal(answer):
        return False
    text = answer.lower()
    if "dining dollars" not in text and "roll over" not in text and "rollover" not in text:
        return False
    # affirms rollover -> wrong, unless it's actually negated right there
    affirms = re.search(r"\b(does|do|can|will)\s+roll\s*over\b", text) or "carries over" in text
    negated = re.search(r"\b(no|not|doesn't|does not|don't|do not|won't)\b", text)
    if affirms and not negated:
        return False
    return bool(negated)


def _judge_grade_appeal(answer: str) -> bool:
    if _is_refusal(answer):
        return False
    text = answer.lower()
    if re.search(r"\byes\b", text):
        return False
    # the answer doesn't have to literally say "no" -- stating the real
    # process (instructor first) is itself a correct "no" to "can I go
    # straight to the chair". What it can't do is say the chair/department
    # is a valid first step.
    if not re.search(r"\binstructor\b", text):
        return False
    if re.search(r"\b(chair|department)\b.*\bfirst\b", text):
        return False
    return True


def _judge_laundry(answer: str) -> bool:
    if _is_refusal(answer):
        return False
    text = answer.lower()
    has_day = "tuesday" in text or "wednesday" in text
    has_morning = "morning" in text
    return has_day and has_morning


def _judge_meal_plan(answer: str) -> bool:
    if _is_refusal(answer):
        return False
    text = answer.lower()
    affirms_free = re.search(r"\b(is|are)\s+free\b", text) or "for free" in text or "at no cost" in text
    if affirms_free:
        return False
    # doesn't have to name "free"/"cost"/"fee" explicitly -- a plain "no" to
    # the question, or any language implying a charge, counts as correctly
    # negating "for free".
    negates = (
        re.search(r"^\s*no\b", text) or re.search(r"\bno\b", text)
        or any(w in text for w in ("not free", "isn't free", "cost", "fee", "charge", "bill"))
    )
    return bool(negates)


def _judge_counseling(answer: str) -> bool:
    if _is_refusal(answer):
        return False
    text = answer.lower()
    has_range = any(
        phrase in text
        for phrase in ("three to four", "three or four", "3 to 4", "3 or 4", "3-4")
    )
    has_hedge = any(word in text for word in ("usually", "typically", "on average", "generally"))
    return has_range and has_hedge


_RULES = [
    ("dining dollars", _judge_dining_dollars),
    ("chair", _judge_grade_appeal),
    ("laundry", _judge_laundry),
    ("meal plan", _judge_meal_plan),
    ("counsel", _judge_counseling),  # matches counseling/counselling
]


def judge(question: str, expects: str, answer: str, results) -> bool:
    q = question.lower()
    for keyword, rule in _RULES:
        if keyword in q:
            return rule(answer)
    raise ValueError(f"No scoring rule for question: {question!r}")
