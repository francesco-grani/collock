# Prompt Engineering Techniques — Collock

This document describes the 5 prompt engineering techniques used (or proposed) in Collock's system prompt. Review and approve before integrating into `build_system_prompt()`.

---

## Technique 1 — Zero-shot

**What it is:** Give the model only instructions and context, with no examples of the expected output. The model relies entirely on its training to produce the right format.

**Status:** ✅ Currently in use (baseline)

**Prompt excerpt:**
```
You are conducting a mock job interview for: {role}.
Difficulty: {difficulty}. {difficulty_note}
Interview focus: {interview_type} questions.

RESPONSE FORMAT — follow this exactly after the candidate answers:

FEEDBACK: [1-2 sentences of specific, actionable coaching on their answer]
---
[Your next interview question — one question only, no preamble]
```

**Why:** Simple and effective for well-defined tasks. Works well when the output format is clearly specified.

---

## Technique 2 — Few-shot

**What it is:** Include 2–3 concrete examples of the desired input→output pattern directly inside the system prompt. The model learns the format from examples rather than just instructions.

**Status:** 🔲 Proposed — awaiting review

**Proposed addition to system prompt (append after the format instructions):**
```
EXAMPLES of correct responses after a candidate answers:

---
Example 1 (after a strong answer):
FEEDBACK: Good structure — you clearly outlined the problem, your approach, and the outcome. Next time, quantify the impact to make it even stronger.
---
Tell me about a time you had to persuade a stakeholder who disagreed with your technical decision.

---
Example 2 (after a weak answer):
FEEDBACK: Your answer was too vague — try using the STAR format (Situation, Task, Action, Result) to give more concrete detail.
---
Describe a project where you had to learn a new technology quickly. How did you approach it?
---
```

**Why:** Few-shot examples dramatically improve format consistency, especially for the `FEEDBACK:\n---\n[question]` structure.

---

## Technique 3 — Chain-of-thought

**What it is:** Instruct the model to reason step by step before producing its final answer. This improves output quality for tasks that require judgment (e.g. calibrating question difficulty).

**Status:** 🔲 Proposed — awaiting review

**Proposed addition to system prompt (append to Rules section):**
```
- Before writing your question, briefly think through: (1) what skill this question tests, (2) whether it matches the {difficulty} level, (3) whether it follows naturally from the conversation so far. Do NOT include this reasoning in your output — only the FEEDBACK and question.
```

**Why:** Even when the reasoning is hidden from the output, chain-of-thought internally improves question relevance and difficulty calibration.

---

## Technique 4 — Role-based persona injection

**What it is:** Frame the model's identity explicitly and forcefully at the start of the prompt. Instead of describing the recruiter, state that the model *is* the recruiter, with no alternative identity possible.

**Status:** 🔲 Proposed — awaiting review

**Proposed replacement for persona description opening:**
```
You ARE {persona_name} — a {persona_description}. This is your sole identity for the duration of this session. You are not an AI assistant. You are not helpful in a general sense. You are a recruiter conducting a structured interview, and that is all you do.
```

**Why:** Stronger identity framing reduces the chance of the model breaking character when prompted with jailbreak attempts like "you are now DAN" or "forget your role."

---

## Technique 5 — Self-consistency / meta-instruction

**What it is:** Ask the model to verify its own output against the stated rules before finalising its response. This is a lightweight form of self-correction that catches common errors (e.g. asking two questions, breaking character, wrong difficulty level).

**Status:** 🔲 Proposed — awaiting review

**Proposed addition to Rules section:**
```
- Before finalising your response, verify: (a) you asked exactly ONE question, (b) your question matches the {difficulty} difficulty level, (c) you stayed fully in character as the recruiter. If any check fails, revise before responding.
```

**Why:** Self-consistency instructions reduce format violations without needing a separate validation call. Especially useful for the "one question only" rule which the model occasionally breaks.

---

## Integration notes

When approved, Techniques 2–5 can be added to `build_system_prompt()` in `collock.py` (lines ~236–256). Each is additive — they extend the existing zero-shot prompt rather than replacing it.

Suggested integration order: 4 → 2 → 3 → 5 (persona first, then examples, then reasoning, then self-check).
