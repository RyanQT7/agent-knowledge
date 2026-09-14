---
name: knowledge-query
description: Answer, teach, compare, review, and trace questions using only the accumulated Markdown knowledge base by default. Use for knowledge retrieval and learning support, not paper ingestion, batch processing, literature review, or Web research.
metadata:
  short-description: Retrieve and teach accumulated knowledge
---

# Knowledge Query

## Purpose and boundaries

Use this Skill when the user wants to learn from, review, compare, or trace questions in the current personal knowledge base. The flow is:

~~~text
Knowledge Base
→ Relevant retrieval
→ Grounded synthesis
→ Explanation or teaching
→ Source traceability
→ Learning support
~~~

This Skill is read-only by default. It does not ingest papers, create paper notes, run a learning batch, perform a Knowledge Review, search the Web, or silently update the repository.

Related workflow boundaries:

- [paper-reading](../paper-reading/SKILL.md) reads and integrates one paper.
- [knowledge-review](../knowledge-review/SKILL.md) consolidates a defined set of existing paper notes.
- [learning-batch](../learning-batch/SKILL.md) orchestrates several paper-reading tasks and a later Review.

## 1. Knowledge source policy

When the user asks for an answer based on the knowledge base, use only local Markdown knowledge by default. Do not use Web search, download sources, or fill paper-specific facts from general model memory.

Read sources in this default order, narrowing to files relevant to the question:

1. concepts/
2. notes/reviews/
3. papers/<paper-id>/notes.md
4. notes/questions.md
5. notes/learning-log.md
6. INDEX.md

Use INDEX.md for navigation and Concepts for the current synthesized definition. Use Reviews for stage-level relationships and boundaries. Use paper notes for concrete paper evidence, experiment details, and source locations.

Only inspect the matching PDF under sources/papers/ when the local notes do not support a key fact, contain an ambiguity or conflict, or the user asks for an exact experimental number or author statement. If the local knowledge base remains insufficient, say:

~~~text
当前知识库尚不足以回答这一点。
~~~

Then identify the missing evidence and suggest a focused next topic or source type. Do not silently import outside knowledge.

## 2. Evidence layers

Keep these layers visibly separate in the answer:

- **Paper-backed fact:** a claim supported by a paper note and, where available, its Section, Table, Figure, or Appendix marker.
- **Cross-paper synthesis:** a relationship or working model derived from multiple notes or a Review.
- **Current interpretation / open question:** a provisional explanation, inference, or issue not settled by the current sources.

Use natural language such as:

~~~text
论文明确支持的是……
结合当前几篇论文，可以暂时理解为……
这一点当前仍没有被充分回答……
~~~

Do not present a Review mental model as a standard architecture claimed by one paper. Do not turn an evolving Concept into a permanent definition.

For traceability, name the relevant Concept, Review, and paper note. When a claim depends on an experiment or explicit author statement, include the source location recorded in the note. Do not manufacture citations or numbers.

## 3. Select the query mode

Infer the smallest mode set that answers the request. Do not read or print the whole repository.

### Concept explanation

For questions such as “什么是 Planning”:

1. Read the matching Concept.
2. Read the most relevant Review and representative paper notes when needed.
3. Explain the current working definition, mechanism, related boundaries, examples, and unresolved questions.

For the current Agent knowledge base, preserve distinctions such as:

- reasoning trace is not hidden model internal state;
- plan-like reasoning is not automatically an explicit Planner;
- tool use is not automatically an Agent;
- trajectory context is not automatically long-term memory;
- a world-model prediction is not a real environment Observation.

### Teaching mode

When the user asks to learn, be taught, or receive a clear explanation, use:

~~~text
Intuition
→ Definition
→ Mechanism
→ Paper example
→ Comparison
→ Common misconceptions
→ Short self-test
~~~

Do not begin with a dense list of terms. Do not oversimplify away the evidence boundary. If the user did not ask for exercises, a small check question is optional rather than mandatory.

### Paper comparison

When comparing papers, compare only dimensions relevant to the question. Prefer relationships and trade-offs over four independent summaries. Useful dimensions include:

- problem and core mechanism;
- reasoning or planning style;
- tool / environment interaction;
- Observation, evidence, or feedback usage;
- execution, search, world model, and replanning;
- strengths, limitations, and suitability.

End by stating which problem or layer each method is best suited to, while marking this as current synthesis when it is not directly claimed by the papers.

### Knowledge tracing

When asked why the knowledge base believes something, provide the reasoning chain:

~~~text
Concept
→ Relevant Review
→ Representative paper notes
→ Paper-backed evidence or explicit boundary
~~~

For example, explain Tool Use versus Agent using the Agent and Tool Use Concepts, Knowledge Review v1 or v2 as applicable, and the ReAct / Toolformer / Reflexion / planning notes that support the distinction.

### Review and revision

For requests to review recent learning, read notes/reviews/ first. If a duration is specified, tailor the scope to that duration; if it is not specified, do not invent a fixed time limit.

A review may include:

- core Concepts;
- important distinctions;
- representative papers;
- common misconceptions;
- open questions;
- optional recall questions.

### Quiz mode

For “考考我” or equivalent requests, generate questions from the current sources. Mix concept explanation, true/false, paper comparison, scenario analysis, and mechanism analysis as appropriate.

By default, do not reveal answers immediately. After the user responds, evaluate each item, explain the misconception or missing reasoning, and link back to the relevant Concept, Review, or paper note. Do not reduce feedback to a score alone.

### Gap analysis

For questions about what the user is missing or should learn next, inspect:

- notes/reviews/;
- notes/questions.md;
- important Concepts marked Status: evolving;
- INDEX.md and representative paper coverage.

Recommend 3–5 priorities based on actual gaps, unresolved questions, and weak Concept coverage, not popularity. Explain why each priority follows from the current knowledge state.

## 4. Memory and other boundary-sensitive answers

When answering questions about memory, explicitly distinguish current context, trajectory history, working-memory-like context, episodic memory, semantic memory, persistent memory, and long-term memory according to the available evidence.

Do not collapse:

- context into memory;
- trajectory history into long-term memory;
- RAG into Agent memory;
- a vector database or persistent storage into a useful memory architecture;
- reflection into memory itself.

For other boundary-sensitive topics, preserve the same discipline: identify what the paper or Concept actually supports before offering a synthesis.

## 5. Read-only default and explicit write-back

An ordinary knowledge-query task must not modify:

- concepts/;
- papers/;
- notes/questions.md;
- notes/learning-log.md;
- INDEX.md;
- Reviews or Skill files.

Do not commit or push an ordinary answer, even if a correction seems obvious.

Write back only when the user explicitly asks to add the understanding, update a Concept, record a question, or save the summary. In that case:

1. State or infer the narrow files that need updating.
2. Preserve paper facts, cross-paper synthesis, and current interpretation as separate layers.
3. Keep the change concise and do not rewrite an entire source note.
4. Run relevant Markdown link and content checks plus git diff --check.
5. Confirm no PDF, credential, token, or unrelated change is staged.
6. Commit one meaningful change and push origin main only after the checks pass.

Use a concise commit message such as Add query-derived clarification to planning concepts. Never create an empty commit, force-push, or rewrite history. If grounding or scope is not sufficient, keep the query read-only and report what is missing.

## 6. Output style

Answer clearly and with enough structure for learning, but do not reproduce complete Concept, Review, or paper-note files. Include source pointers when useful:

~~~text
Concept:
Review:
Paper:
Source location:
~~~

When evidence is partial, say Partially supported and explain the boundary. When evidence is absent, use the insufficient-knowledge statement from Section 1 and name a focused next step.
