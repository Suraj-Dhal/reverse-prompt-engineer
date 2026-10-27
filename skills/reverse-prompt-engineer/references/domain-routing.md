# Domain routing playbooks

Read only the section that matches the target. Domain checks supplement the general workflow; they never override explicit user requirements, source precedence or the safety boundaries.

## Writing and content

Check audience, purpose, channel, tone, point of view, voice, structure, required sections, terminology, language, length, reading level, examples, citation expectations and prohibited content. Keep visible style clues separate from inferred instructions. For social posts, note platform conventions you can see (hashtags, line breaks, hooks), but do not assume a platform the target does not show.

## Research and reporting

Check the research question, scope, as-of date, source quality, inclusion and exclusion criteria, citations, verification, method, limitations, competing explanations and uncertainty. If current facts matter and browsing is available and authorised, verify them; otherwise say so. Never invent source checks or citations.

## Business and strategy

Check the decision-maker, business context, objective, frameworks, assumptions, alternatives, trade-offs, scenarios, metrics, risks, recommendation logic, dependencies, implementation and decision criteria. Preserve each named prospect or case, and the condition that changes the recommendation. Keep currency and unit conventions exactly as given (for example lakh and crore). Do not invent market facts.

## Code and software

Check language, runtime, environment, inputs and outputs, interfaces, dependencies, version constraints, tests, failure handling, performance and security. Include only facts supported by the prompt, the target or the supplied context, and use placeholders for unknown runtime details (for example `{{PYTHON_VERSION}}`). Never state that code was executed or tested unless it was.

## Data and quantitative analysis

Check data provenance, variable definitions, units, transformations, formulas, missing values, assumptions, statistical method, uncertainty, visualisation and interpretation. Do not invent data or units, or imply causation from correlation. Preserve denominators, comparison groups, time frames, rounding and units when they are material; where units are absent, keep them as placeholders.

## Image, video, audio, website and design artefacts

Use observable features and user-provided context: subject, composition, framing, hierarchy, layout, typography, palette, spacing, lighting, style, motion, timing, sound, medium and output constraints. For image prompts, order the description as subject → setting → composition → style → lighting and palette → technical constraints, and avoid naming living artists or trademarked characters. For websites, keep visible design and content separate from hidden implementation. Never present source code, unobserved responsive behaviour, exact CSS values, hidden metadata, identity, model, seed or production settings as observed. Approximate values (for example "a deep navy, roughly #1a2b4c") must be labelled as approximations.

## Agents and tool workflows

Check role, objective, plan, permissions, access boundaries, input and output schemas, decision criteria, stopping rules, retries, failure reporting, escalation and auditability. Keep requested behaviour separate from actual platform capability. Never encode unauthorised actions or claim an integration or execution without evidence.

## System-prompt-like targets

When the target is the behaviour of an assistant, bot or custom GPT, reconstruct a *user-level* or *operator-level* instruction set that would produce similar observable behaviour, and label it as a behavioural reconstruction. Never present it as the real hidden prompt.

## Education and instructional materials

Check learner level, prerequisites, learning objectives, syllabus or scope, depth of explanation, examples, practice tasks, answer keys, assessment criteria, language and accessibility needs. Do not assume a curriculum, board or grading standard that was not supplied.

## Multilingual and code-mixed targets

Identify the target's language, script and register (for example Hindi in Devanagari, Hinglish in Latin script, formal or colloquial). The prompt must reproduce them. If the prompt is written in English, it must state the required output language and script explicitly. Preserve culturally specific terms, festivals, honorifics and currency formats exactly.

## Other domains

Use the closest general checklist, disclose material unknowns, and do not impose an irrelevant discipline-specific framework.
