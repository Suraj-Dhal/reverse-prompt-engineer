# Usage guide

How to ask, what to give the skill, how to read the answer, and how to get the most faithful reconstruction.

## The short version

Paste the output and ask what prompt produced it. Add whatever context you have. You get back one copy-ready prompt and a short explanation of how well the evidence supports it.

```text
What prompt would produce this? It's for our weekly client newsletter.

<paste the output here>
```

## What to provide

The more relevant context you give, the higher the confidence. In order of value:

1. **The output itself** (required): text pasted in, a file, a screenshot or a description.
2. **The original request,** if you have any part of it, even a rough memory.
3. **Audience and use:** who reads it and where it is published.
4. **Supporting material:** briefs, notes, data, earlier drafts, the conversation that led to it.
5. **What matters:** which features must be reproduced (structure? tone? the exact numbers?).

Mark the authoritative source if documents disagree ("the v2 brief is the final one"). Leave out unrelated personal details; the skill ignores them anyway.

## Ways to ask

| You want | Ask like this |
|---|---|
| The prompt behind one output | "What prompt could have produced this?" |
| A prompt you lost | "I lost the prompt I used for this report. Rebuild it from the final document." |
| A master prompt from a long chat | "Rebuild the master prompt from our conversation and these notes, so I can rerun the whole thing." |
| One prompt for several outputs | "Give me one prompt that would produce all three of these product descriptions." |
| An audit, then a reconstruction | "Here's my original prompt and the result. Which instructions did it follow or miss? Then give me a prompt that reliably produces this." |
| A reconstruction plus improvements | "Infer the prompt behind this answer, and suggest how to make it better." |
| An image or design prompt | "Infer an image-generation prompt from this picture." (Attach it, or describe it precisely.) |
| A bot's behaviour | "What instructions would make an assistant answer like this?" |
| A different format | "Same thing, but give me the prompt as a JSON object." Your format request overrides the default. |

The skill does **not** activate for nearby tasks such as polishing a prompt you already have, writing a new prompt from scratch, AI-text detection, or identifying which model wrote something.

## Reading the answer

### Reconstructed Prompt

One block you can copy as-is. Look for:

- **`{{PLACEHOLDERS}}`**: inputs the evidence could not establish. Replace each one with your real value before use. Every placeholder is also listed under *Confidence and limits*.
- **`[VERIFY: …]` markers**, where present: the prompt is telling the model to flag facts that need checking.

### Reasoning

Five fixed points:

| Label | What it tells you |
|---|---|
| **Observable clues** | What is actually in the output: structure, tone, format, domain signals. |
| **Likely intent** | The supported purpose, audience and deliverable. |
| **Context preserved** | Which of your facts, figures, scenarios and constraints were carried into the prompt. |
| **Prompt-design factors** | Why the prompt is built the way it is. |
| **Confidence and limits** | `Overall confidence: High`, `Moderate` or `Low`, then what is explicit, what is inferred, what is unknown or conflicting, which sources could not be read, and the placeholders. |

Mode-specific extras appear as sub-headings inside Reasoning: **Requirement audit** (a table of Followed / Partly / Missed / Not verifiable) and **Optional improvements (not evidence)**.

### What the confidence levels mean

| Level | Typical situation | What to do |
|---|---|---|
| **High** | You supplied the original requirements, or several independent clues agree. | Use the prompt; spot-check the output. |
| **Moderate** | The task is clear; some style or method details are inferred. | Run the prompt once and compare with the original. |
| **Low** | A short or generic output with little context. | Fill the placeholders, and add context if you can, then ask again. |

## Tips for better reconstructions

- **Paste exact text.** Paraphrases lose the structure and wording the skill relies on.
- **Say what is fixed and what varies.** "The event details change every month" turns them into placeholders instead of hard-coding them.
- **Flag edits.** If you or a colleague edited the output, say so; the skill reconstructs the generated part, not the edits.
- **Give all the pieces of a long chat.** Requirements stated early are easy to lose; the skill keeps still-valid earlier requirements, but only if it can see them.
- **Check the numbers.** If figures in your sources disagree, the skill reports the conflict instead of choosing. Resolve it and ask again.
- **Test the prompt.** Run it in a fresh chat and compare. If something is off, paste both outputs back and ask what to adjust.

## Language

Ask in any language. The reconstructed prompt reproduces the language of the *target* (a Hindi message gets a prompt that produces Hindi), and the Reasoning is written in *your* language.

## What it will not do

- Claim to recover the exact original prompt or any hidden system prompt.
- Identify the model, settings or seed that produced an output.
- Pretend to have read a file or webpage it could not access.
- Verify facts or citations, unless you ask and the host has a browsing tool.
- Reconstruct prompts for harmful content (for example phishing). It explains why and offers a safe alternative instead.

## Troubleshooting

| Symptom | Fix |
|---|---|
| The skill doesn't activate | Say "use the reverse-prompt-engineer skill", or in Claude Code invoke `/reverse-prompt-engineer:reverse-prompt-engineer`. Check that it is enabled ([installation](installation.md#check-that-it-works)). |
| Too many placeholders | Add the missing context (audience, purpose, original request) and ask again. |
| The prompt is too generic | Paste the exact output rather than a summary, and say which features must be reproduced. |
| You wanted several prompts | Ask explicitly: "give me separate prompts for each output". |
| You wanted the improved version only | Ask for "an optimised prompt". The faithful reconstruction is kept, and the optimised variant is labelled. |
