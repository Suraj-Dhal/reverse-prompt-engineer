# Evidence and uncertainty

A target output can support a plausible reconstruction. On its own it cannot establish the exact historical prompt: many prompts, model behaviours, tools and post-processing paths can produce similar results.

## Evidence classes

| Class | Meaning | Example |
|---|---|---|
| **Explicit** | Stated directly in the user's instructions or an authoritative source. | "Earlier you said: keep it under 2 pages." |
| **Observed** | Visibly present in the target, with no assumption about why. | The output has four H2 sections and a table. |
| **Strong inference** | A likely instruction supported by several specific clues, or by a direct link between context and output. | Every section ends with an action item, and the brief mentions "decision-ready". |
| **Weak inference** | One plausible explanation among several. Include it only if it materially helps, and label it. | The friendly tone *might* reflect a requested persona. |
| **Unknown** | Not established by the available evidence. | The exact word limit. |
| **Conflict** | Two or more sources or instructions cannot all be satisfied as written. | The brief says 20 pages; a later message says 2 pages. |

Never upgrade an observed feature into an explicit instruction. A polished table is *observed*; a request to use that exact table schema is an *inference* unless a source says so.

## Confidence calibration

State one overall level in Reasoning, as `Overall confidence: High`, `Moderate` or `Low`.

- **High:** the task and key constraints are explicitly supplied, or strongly corroborated by several independent clues.
- **Moderate:** the overall task is clear, but some method, style or constraint details are inferred.
- **Low:** the output is generic, sparse or ambiguous, or relevant context is missing. Keep the prompt conservative and use placeholders.

Confidence describes how well the evidence supports the reconstruction. It is not the probability of reproducing an identical output, and it is never expressed as certainty.

## Source and citation discipline

- Preserve source labels and user-supplied provenance when they are material.
- Never claim a citation is valid, a source was checked, or a fact is current unless that verification actually happened in this session.
- If citations in the target are unverified, say so. The reconstructed prompt can ask for verifiable sources, but it must not encode the unverified ones as trusted facts.
- For date-sensitive targets, keep the relevant as-of date, or use `{{AS_OF_DATE}}`, and ask for current verification when tools are available and authorised.
- Do not infer that browsing, code execution, a specific API or a named model was used just because the output contains citations or code.
- If source access is incomplete, say what was unavailable and limit claims to what was available.

## Validation checklist

- [ ] Explicit requirements remain intact.
- [ ] Observed traits are not presented as proven instructions.
- [ ] Strong and weak inferences can be told apart.
- [ ] Unknowns and conflicts are visible where they are material.
- [ ] Names, figures, dates, units, scenarios and dependencies are preserved accurately.
- [ ] No unsupported claims about sources, tools, execution, model or metadata were added.
- [ ] The confidence level matches the evidence.
- [ ] The reconstructed prompt is actionable and copy-ready.
