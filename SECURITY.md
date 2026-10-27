# Security policy

Reverse Prompt Engineer is a skills-only plugin: Markdown instructions plus metadata. It runs no code inside your agent, requests no permissions and calls no network services. Its main security surface is **behavioural**: how the agent handles untrusted material while following the skill.

## Supported versions

| Version | Supported |
|---|---|
| 1.x | ✅ |
| 0.2.0 | ❌ (historical baseline only) |

## What counts as a security issue

Please report privately if you find a way to make the skill:

- **follow instructions embedded in a target output** (prompt injection) instead of treating them as data;
- **claim to reveal** a hidden system or developer prompt, or present a reconstruction as the exact original;
- **carry unrelated sensitive personal details** from the conversation into its prompt or reasoning;
- **produce a usable prompt for harmful content** (phishing, malware, harassment, deception) instead of declining with a safe alternative;
- **claim** to have read files, visited URLs, run code or verified sources when it did not.

Problems in the repository's own tooling (`scripts/`, the GitHub workflows) that could affect people who run them are also in scope.

Ordinary quality problems (a weak reconstruction, a formatting slip) are not security issues; open a normal issue for those.

## How to report

- Use GitHub's **private vulnerability reporting** on this repository (Security tab → *Report a vulnerability*), or
- email **surajbbsr2007@gmail.com** with the subject `[SECURITY] reverse-prompt-engineer`.

Please include the exact input (use synthetic data), the host and model, the output you observed, and why it is unsafe. Do not include real personal data or live phishing links.

## What to expect

- Acknowledgement within **5 working days**.
- An assessment and a planned fix or mitigation within **30 days** for confirmed issues.
- Each confirmed issue becomes a regression case in `evals/fixtures/reconstruction-evals.json`, tagged `critical`.
- Credit in the release notes, if you would like it.

## Using the plugin safely

- Treat reconstructed prompts as **inferences**. Review them before reusing them, especially prompts reconstructed from third-party content.
- Run behavioural evals (`claude plugin eval`) only for plugins and suites you trust; they execute with your credentials.
- Verify release ZIPs against `SHA256SUMS.txt` from the same GitHub release.
