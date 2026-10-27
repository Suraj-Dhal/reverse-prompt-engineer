#!/usr/bin/env python3
"""Structural checks for the Reverse Prompt Engineer package; not behavioral tests."""
from pathlib import Path
import json, re, sys

ROOT = Path(__file__).resolve().parents[3]  # plugin root: skills/<skill>/tests -> 3 parents
errors = []
def check(cond, message):
    if not cond:
        errors.append(message)

manifest_path = ROOT / "plugin.json"
check(manifest_path.exists(), "plugin.json missing")
manifest = json.loads(manifest_path.read_text())
check(manifest.get("$schema") == "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json", "root schema mismatch")
check(manifest.get("name") == "reverse-prompt-engineer", "manifest name/dir mismatch")
check(bool(re.fullmatch(r"(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)", manifest.get("version",""))), "version is not strict SemVer")
interface = manifest.get("extensions",{}).get("com.openai",{}).get("interface",{})
check(len(interface.get("shortDescription","")) <= 30, "shortDescription exceeds 30 chars")
check(bool(interface.get("displayName")), "displayName missing")

skill_path = ROOT / "skills" / "reverse-prompt-engineer" / "SKILL.md"
check(skill_path.exists(), "SKILL.md missing")
skill = skill_path.read_text()
check(skill.startswith("---\n"), "SKILL.md YAML frontmatter missing")
check("name: reverse-prompt-engineer" in skill, "skill name mismatch")
check("### Reconstructed Prompt" in skill and "### Reasoning" in skill, "two-section contract missing")
check("exact historical prompt" in skill, "historical-prompt limitation missing")

for rel in [
    "README.md",
    "skills/reverse-prompt-engineer/references/reconstruction-workflow.md",
    "skills/reverse-prompt-engineer/references/context-preservation.md",
    "skills/reverse-prompt-engineer/references/domain-routing.md",
    "skills/reverse-prompt-engineer/references/evidence-and-uncertainty.md",
    "skills/reverse-prompt-engineer/references/safety-and-trust-boundaries.md",
    "skills/reverse-prompt-engineer/assets/requirement-evidence-matrix-template.md",
    "skills/reverse-prompt-engineer/evals/README.md",
    "skills/reverse-prompt-engineer/evals/trigger-evals.json",
    "skills/reverse-prompt-engineer/evals/reconstruction-evals.json",
]:
    check((ROOT/rel).is_file(), f"required file missing: {rel}")

triggers = json.loads((ROOT/"skills/reverse-prompt-engineer/evals/trigger-evals.json").read_text())
behaviors = json.loads((ROOT/"skills/reverse-prompt-engineer/evals/reconstruction-evals.json").read_text())
check(len(triggers) >= 24, "fewer than 24 trigger cases")
check(sum(1 for x in triggers if x["expected_trigger"]) >= 10, "positive trigger cases underrepresented")
check(sum(1 for x in triggers if not x["expected_trigger"]) >= 10, "negative trigger cases underrepresented")
check(len(behaviors) >= 16, "fewer than 16 behavioral cases")
required_behavior_ids = {f"B{i:02d}" for i in range(1,17)}
check(required_behavior_ids.issubset({x.get("id") for x in behaviors}), "required behavioral scenarios incomplete")
for idx, case in enumerate(triggers,1):
    check(isinstance(case.get("query"), str) and isinstance(case.get("expected_trigger"), bool), f"invalid trigger schema at {idx}")
for case in behaviors:
    for key in ["input","context_available","must_preserve","expected_output","prohibited","pass_fail"]:
        check(key in case, f"{case.get('id')} missing {key}")

# Verify Markdown relative links, ignoring URL anchors and code fences.
for md in ROOT.rglob("*.md"):
    content = md.read_text()
    for link in re.findall(r"\[[^\]]+\]\(([^)]+)\)", content):
        target = link.split("#",1)[0]
        if not target or "://" in target or target.startswith("mailto:"):
            continue
        check((md.parent/target).resolve().exists(), f"broken relative link in {md.relative_to(ROOT)}: {link}")

if errors:
    print("FAIL")
    print("\\n".join(f"- {e}" for e in errors))
    sys.exit(1)
print(f"PASS: structural validation, {len(triggers)} trigger cases, {len(behaviors)} behavioral fixtures.")
