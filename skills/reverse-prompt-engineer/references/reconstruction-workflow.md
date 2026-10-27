# Reconstruction workflow: advanced procedures

`SKILL.md` defines the standard eight-phase workflow. This file adds procedures for the harder cases it points here for. Use only the section you need.

## 1. Several outputs, one prompt

1. **Line the outputs up.** For each one, note format, length, audience, tone, structure and content scope.
2. **Find the invariant core,** meaning the traits that every output shares. Those become the fixed body of the prompt.
3. **Classify the differences:**
   - *Parametric*: same task, different values (channel, length, language). Turn each into a variable, such as `{{CHANNEL}}`, or a labelled sub-section: "For the tweet: …; for the blog intro: …".
   - *Structural*: different tasks or incompatible formats (a 280-character post versus a JSON object). A single prompt can still request all of them as separately specified deliverables, as a "campaign kit" prompt often does.
4. **Weigh and disclose.** Say in Reasoning whether one prompt or several separate prompts more plausibly produced the outputs, cite the clues (shared facts and wording point to one brief; unrelated styles point to separate runs), and never claim certainty either way. Then give the best common prompt, unless the user asked for separate prompts.

## 2. Long conversations and source packages

1. Build a **source inventory**: source, type, accessible (yes or no), authority (user-designated, supporting, or superseded) and key facts.
2. Apply the precedence ladder from `SKILL.md` Phase 2.
3. Compress the conversation with the five-step method in `context-preservation.md`.
4. Check coverage against **every** source, not only the latest or most prominent.
5. Do not let a long history crowd the prompt. Every retained line must change the output.

| Source | Type | Accessible | Authority | Key facts carried forward |
|---|---|---|---|---|
| Turn 3 | User message | Yes | Still valid | Audience: MSME owners in Odisha |
| `brief-v2.pdf` | Attachment | No | Unknown | Not inspected; disclosed as a limitation |

## 3. Edited or post-processed outputs

A final artefact is often partly human-edited. Signs include:

- Abrupt shifts in tone, tense, spelling convention or formatting between sections.
- Leftover scaffolding: `[Insert chart here]`, `TODO`, tracked-change marks, duplicated headings, mismatched numbering.
- Personal anecdotes, typos or local references set inside otherwise uniform generated prose.

When you see these signs:

- Reconstruct the prompt for the **generated layer**, not the edits.
- Do not encode human edits as instructions unless they are clearly part of the brief.
- Name the likely editing in Reasoning, and lower the confidence where it obscures the original output.

## 4. Requirements audit mode

When the user supplies their original prompt (or a list of requirements) along with the output and asks what was followed:

1. Split the original into atomic requirements, one testable instruction each.
2. Rate each one: **Followed**, **Partly**, **Missed** or **Not verifiable** (not checkable from the output alone), citing the clue.
3. Present the result under `### Requirement audit` at the top of Reasoning:

   | # | Requirement | Status | Evidence |
   |---|---|---|---|
   | 1 | Under 300 words | Followed | 268 words |
   | 2 | Cite two sources | Missed | No citations present |

4. The reconstructed prompt **keeps every still-valid requirement, including the missed ones**. The user wants a prompt that reliably produces what they intended. Wording that makes a missed requirement harder to miss belongs under `### Optional improvements (not evidence)`, not silently in the prompt.

## 5. Low-evidence targets

When the target is short, generic or context-free:

- Keep the prompt short and conservative: state the observable task, format and tone, and nothing more.
- Use placeholders for audience, purpose and constraints rather than inventing them.
- Set `Overall confidence: Low` and say what extra context would most improve the reconstruction.

## 6. Final assembly checklist

- [ ] The mode is identified, and the mode-specific placement rules are followed.
- [ ] Every material source is accounted for, and inaccessible ones are disclosed.
- [ ] Conflicts are surfaced, not merged.
- [ ] Parametric differences are variables; structural differences are disclosed.
- [ ] Human edits are not encoded as instructions.
- [ ] Placeholders are well-formed and listed.
- [ ] The response follows the two-section contract.
