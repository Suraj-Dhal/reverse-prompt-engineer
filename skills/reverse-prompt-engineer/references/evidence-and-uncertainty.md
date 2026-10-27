# Evidence and uncertainty

The target output can support a plausible reconstruction; it cannot establish the exact historical prompt by itself. Multiple prompts, model behaviors, tools, and post-processing paths can produce similar results.

## Evidence classes

- **Explicit:** directly stated in the user's instructions or an authoritative source.
- **Observed:** visibly present in the target (such as headings, tone, layout, a table, or code structure), without assuming why it is present.
- **Strong inference:** a likely instruction supported by multiple specific clues or by a direct relationship between context and output.
- **Weak inference:** one plausible explanation among several; include only if it materially helps and label it.
- **Unknown:** not established by available evidence.
- **Conflict:** two or more sources or instructions cannot all be satisfied as written.

Do not upgrade an observed feature into an explicit instruction. A polished table is observed; a request to use that exact table schema is an inference unless the user or source says so.

## Confidence calibration

- **High:** the task and key constraints are explicitly supplied or strongly corroborated by several independent clues.
- **Moderate:** the overall task is clear, but some method, style, or constraint details are inferred.
- **Low:** the output is generic, sparse, ambiguous, or lacks relevant context. Keep the prompt conservative and use placeholders where necessary.

Confidence describes the reconstruction's evidentiary support, not the probability of reproducing an identical output.

## Source and citation discipline

- Preserve source labels and user-supplied provenance when material.
- Do not claim a citation is valid, a source was checked, or a fact is current unless verification actually occurred.
- For date-sensitive targets, preserve the relevant as-of date or use an explicit placeholder and request current verification when tools are available and authorized.
- Do not infer that browsing, code execution, a specific API, or a named model was used merely because the output contains citations or code.
- If source access is incomplete, disclose it and limit claims to what is available.

## Validation checklist

Before finalizing, check:

- [ ] Explicit requirements remain intact.
- [ ] Observed traits are not misrepresented as proven instructions.
- [ ] Strong and weak inferences are distinguishable.
- [ ] Unknowns and conflicts are visible where material.
- [ ] Names, figures, dates, units, scenarios, and dependencies are preserved accurately.
- [ ] No unsupported source, tool, execution, model, or metadata claims were added.
- [ ] Confidence matches the evidence and is not expressed as certainty.
- [ ] The reconstructed prompt remains actionable and copy-ready.
