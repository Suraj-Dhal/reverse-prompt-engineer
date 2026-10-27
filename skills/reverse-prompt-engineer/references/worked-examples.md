# Worked examples

Three complete examples of the default response contract. All names, firms and figures are fictional. Each response is checked automatically by `scripts/lint_response.py` in CI, so these examples always match the contract in `SKILL.md`.

Use them to calibrate format and depth, not as templates to copy word for word.

---

## Example 1: social post with partial context (writing)

**User:** We're a small CA firm. Our intern wrote this LinkedIn post with ChatGPT and has since left. What prompt would make posts like this for our next events?

> 🚀 GST e-invoicing is now mandatory for more MSMEs — is your business ready?
>
> On 14 November 2026, Mohanty & Associates is hosting a FREE 90-minute workshop in Bhubaneswar for small business owners.
>
> What you'll learn:
> ✅ Who must issue e-invoices, and from when
> ✅ How to generate an IRN, step by step
> ✅ The 5 mistakes that trigger notices
>
> 📍 Saheed Nagar, Bhubaneswar | 🕓 4:00–5:30 PM
> 🎟️ Only 40 seats — register via the link in the comments.
>
> #GST #MSME #Odisha #EInvoicing #SmallBusiness

**Response:**

<!-- example-response: social-post -->
````markdown
## Reconstructed Prompt

Paste this into a new chat and fill in the placeholders:

```text
ROLE
You are the social media writer for Mohanty & Associates, a small chartered accountancy firm in Bhubaneswar.

CONTEXT
Audience: owners of small and medium businesses (MSMEs) in Odisha who are not accountants.
Purpose: fill a free, in-person workshop.

TASK
Write a LinkedIn post announcing our free workshop on {{TOPIC}}.

EVENT DETAILS (use exactly as given)
Date: {{DATE}}
Time: {{TIME}}
Duration: {{DURATION}}
Venue: {{VENUE}}
Seats: {{SEAT_COUNT}}
Registration: link in the comments

OUTPUT FORMAT
1. A hook line that starts with one emoji and asks whether the reader's business is ready.
2. One or two sentences naming the firm, the free format, the duration, the city and the audience.
3. "What you'll learn:" followed by exactly three ✅ bullets, each one short line.
4. One logistics line using 📍 and 🕓, separated by " | ".
5. A scarcity line using 🎟️ that states the seat limit and how to register.
6. Four to six relevant hashtags on the final line.

CONSTRAINTS
Tone: friendly, slightly urgent, professional, in plain English.
Length: under 100 words, excluding hashtags.
Do not state legal deadlines, thresholds or penalties unless they appear in the verified facts below. If such a fact is needed and missing, write [VERIFY: <fact>] instead.
Verified facts: {{VERIFIED_FACTS}}
```

## Reasoning

1. **Observable clues:** an emoji-led hook framed as a readiness question; firm, "FREE", duration and city in the second paragraph; exactly three ✅ learning bullets; a 📍/🕓 logistics line; a 🎟️ scarcity line; five hashtags; about 80 words before the hashtags.
2. **Likely intent:** a reusable event-promotion post that drives registrations from MSME owners.
3. **Context preserved:** your firm name and city, the MSME audience, the free in-person format and the comment-link registration route. The 14 November date, the 40 seats and the venue became placeholders, because you want posts for future events.
4. **Prompt-design factors:** the role and audience fix the voice; the numbered output format reproduces the six-part structure and emoji pattern; the length limit matches the original; the verification rule stops the model asserting regulatory claims on its own.
5. **Confidence and limits:** Overall confidence: Moderate. The structure is observed directly; the tone and the length limit are inferred. The opening claim that e-invoicing "is now mandatory for more MSMEs" is unverified (I have not checked current GST rules), so the prompt asks you to supply verified facts. Placeholders: `{{TOPIC}}`, `{{DATE}}`, `{{TIME}}`, `{{DURATION}}`, `{{VENUE}}`, `{{SEAT_COUNT}}`, `{{VERIFIED_FACTS}}`. The intern's actual wording cannot be recovered from the post.
````

---

## Example 2: code with an unknown runtime (software)

**User:** Reverse-prompt this function. I found it in our repo and I think someone generated it.

```python
import re
from datetime import datetime

def parse_invoice_date(raw: str) -> datetime:
    """Parse invoice dates like '05/11/2026', '5-Nov-2026' or '2026-11-05'.

    Raises:
        ValueError: if the string matches none of the supported formats.
    """
    raw = raw.strip()
    formats = ("%d/%m/%Y", "%d-%b-%Y", "%Y-%m-%d")
    for fmt in formats:
        try:
            return datetime.strptime(raw, fmt)
        except ValueError:
            continue
    if re.fullmatch(r"\d{8}", raw):
        return datetime.strptime(raw, "%d%m%Y")
    raise ValueError(f"Unsupported date format: {raw!r}")
```

**Response:**

<!-- example-response: python-function -->
````markdown
## Reconstructed Prompt

```text
Write a Python function `parse_invoice_date(raw: str) -> datetime` that parses invoice date strings.

Requirements:
- Strip surrounding whitespace first.
- Support these formats, tried in this order: "05/11/2026" (DD/MM/YYYY), "5-Nov-2026" (D-Mon-YYYY) and "2026-11-05" (YYYY-MM-DD).
- Also accept exactly eight digits with no separators, read as DDMMYYYY.
- Treat all dates as day-first. Never interpret them as month-first.
- If nothing matches, raise ValueError with a message that includes the original input.
- Use only the Python standard library (Python {{PYTHON_VERSION}} or later).
- Include type hints and a docstring that shows example formats and has a Raises section.

Return only the code.
```

## Reasoning

1. **Observable clues:** standard-library imports only (`re`, `datetime`); full type hints; a docstring with three example formats and a Raises section; an ordered tuple of `strptime` formats; a regex fallback for eight-digit strings; a `ValueError` that quotes the input with `!r`.
2. **Likely intent:** a small, dependency-free helper that normalises day-first invoice dates from mixed sources.
3. **Context preserved:** the exact formats and their order, the eight-digit fallback, the day-first convention and the error behaviour.
4. **Prompt-design factors:** each visible behaviour is an explicit, testable requirement; the order is stated because the order of attempts changes results for ambiguous strings; "Return only the code" reflects that the artefact is code with no prose around it.
5. **Confidence and limits:** Overall confidence: Moderate. The behaviour is observed directly in the source. "Return only the code" is a weak inference. The eight-digit fallback is not mentioned in the docstring, so it may be a later human addition (weak inference). I have not run this code, and no tests, runtime or version information was supplied, so the Python version is a placeholder: `{{PYTHON_VERSION}}`.
````

---

## Example 3: requirements audit plus reconstruction (audit mode)

**User:** Here's the prompt I used and what came back. Which of my instructions did it follow? Then give me the prompt that would reliably produce this.

*Original prompt:* "Write a 150-word product description for our handloom Sambalpuri cotton saree for an Amazon listing. Mention it's handwoven in Bargarh, use a warm tone, include care instructions, and end with a call to action. No exaggerated claims."

*Output:* "Bring home a piece of Odisha's living heritage. This Sambalpuri cotton saree is handwoven by skilled artisans in Bargarh, using the traditional tie-and-dye bandha technique that gives every motif its soft, feathered edge. Breathable and lightweight, it drapes comfortably through long summer days and festive evenings alike. The rich maroon body is framed by a contrasting temple border, and the pallu carries conch and wheel motifs. Pair it with silver jewellery for celebrations, or keep it simple for the office. Each saree carries small variations, a mark of the hand rather than a flaw. Add this timeless weave to your wardrobe today."

**Response:**

<!-- example-response: audit-mode -->
````markdown
## Reconstructed Prompt

```text
Write a product description of about 150 words for the Amazon listing of our handloom Sambalpuri cotton saree.

Product details: {{PRODUCT_DETAILS}}

Requirements:
- Mention that it is handwoven in Bargarh.
- Use a warm tone.
- Include care instructions.
- End with a call to action.
- No exaggerated claims.
```

## Reasoning

### Requirement audit

| # | Requirement | Status | Evidence |
|---|---|---|---|
| 1 | About 150 words | Partly | About 100 words |
| 2 | Amazon listing | Not verifiable | Plain prose; no listing-specific format is visible |
| 3 | Handwoven in Bargarh | Followed | "handwoven by skilled artisans in Bargarh" |
| 4 | Warm tone | Followed | "Bring home…", "a mark of the hand" |
| 5 | Care instructions | Missed | None present |
| 6 | Call to action | Followed | "Add this timeless weave to your wardrobe today." |
| 7 | No exaggerated claims | Partly | Mostly restrained; "timeless" and "living heritage" are mild puffery |

1. **Observable clues:** seven short sentences moving from heritage, to craft, to comfort, to visual details, to styling, to a final call to action; specific details (maroon body, temple border, conch and wheel motifs, bandha technique) that your prompt did not supply.
2. **Likely intent:** a warm, craft-led marketplace description that converts browsers.
3. **Context preserved:** every requirement from your original prompt, including the care instructions the output missed, because you want a prompt that produces what you intended.
4. **Prompt-design factors:** your wording is kept almost exactly (explicit evidence outranks inference). `{{PRODUCT_DETAILS}}` is added because the output contains product specifics that must have come from somewhere: either extra context the model had, or invention.
5. **Confidence and limits:** Overall confidence: Moderate. The requirements are explicit because you supplied them, but it is unknown where the product details came from. Check the colour, border, motifs and technique against the real saree before publishing. Placeholder: `{{PRODUCT_DETAILS}}`.

### Optional improvements (not evidence)

- Add "Use only the product details provided; do not invent colours, motifs or techniques."
- Ask for care instructions as two or three short bullets after the description.
- Specify "140–160 words" instead of "150-word" to reduce under-length drafts.
````
