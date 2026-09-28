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
    if not re.search(r"\bno\b", text):
        return False
    # "no" alone isn't enough -- it has to be no for the right reason
    return "instructor" in text


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
    if "free" not in text and "complimentary" not in text and "no cost" not in text and "no charge" not in text:
        # doesn't have to say "free" explicitly -- a clear no/cost mention is enough
        if not re.search(r"\b(no|not|cannot|can't|isn't|is not)\b", text):
            return False
    negates_free = re.search(r"\b(no|not|isn't|is not|cannot|can't)\b.*\bfree\b", text) or \
        re.search(r"\bfree\b.*\b(no|not|isn't|is not)\b", text) or \
        "cost" in text or "fee" in text or "charge" in text or "not free" in text or "not complimentary" in text
    affirms_free = re.search(r"\b(is|are)\s+free\b", text) or "for free" in text or "at no cost" in text
    if affirms_free and not negates_free:
        return False
    return bool(negates_free)


def _judge_counseling(answer: str) -> bool:
    if _is_refusal(answer):
        return False
    text = answer.lower()
    has_range = "three to four" in text or "3 to 4" in text or "3-4" in text
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
