# Installation

Reverse Prompt Engineer is one skill packaged for several hosts. Pick yours:

| Host | Method | Jump to |
|---|---|---|
| Claude Code (CLI, desktop, IDE) | Plugin marketplace, one command | [Claude Code](#claude-code) |
| OpenAI Codex / ChatGPT desktop | Plugin marketplace | [OpenAI Codex](#openai-codex) |
| Claude.ai and the Claude apps | Upload the skill ZIP | [Claude.ai](#claudeai-and-the-claude-apps) |
| Any other Agent Skills or Agent Plugins host | Copy the folder | [Other hosts](#other-agent-skills-and-agent-plugins-hosts) |

After installing, [check that it works](#check-that-it-works).

---

## Claude Code

### Install

On Claude Code 2.1.275 or later, one command does everything. Inside a session:

```text
/plugin install reverse-prompt-engineer --marketplace Suraj-Dhal/reverse-prompt-engineer
```

On any version, you can add the marketplace and then install from it:

```text
/plugin marketplace add Suraj-Dhal/reverse-prompt-engineer
/plugin install reverse-prompt-engineer@suraj-dhal
```

The same two steps from your shell:

```bash
claude plugin marketplace add Suraj-Dhal/reverse-prompt-engineer
claude plugin install reverse-prompt-engineer@suraj-dhal
```

`suraj-dhal` is the marketplace name defined in this repository's `.claude-plugin/marketplace.json`. Add `--scope project` to the install command to record the plugin in the current project's `.claude/settings.json`, so it is shared with everyone who works in that repository.

### Confirm

```bash
claude plugin list                                # shows reverse-prompt-engineer@suraj-dhal, enabled
claude plugin details reverse-prompt-engineer     # component inventory: Skills (1) reverse-prompt-engineer
```

### Use

Just ask naturally ("what prompt produced this?"); the skill activates on its own. To invoke it explicitly, use its namespaced name:

```text
/reverse-prompt-engineer:reverse-prompt-engineer
```

### Update

The plugin's version is pinned in its manifest, so you receive a new copy when a new version is released. To update manually:

```text
/plugin marketplace update suraj-dhal
```

or from the shell, `claude plugin update reverse-prompt-engineer@suraj-dhal`. To get updates automatically, open `/plugin`, go to **Marketplaces**, select `suraj-dhal` and choose **Enable auto-update**.

### Pin a version

Append a tag to the marketplace source to stay on a specific release:

```text
/plugin marketplace add Suraj-Dhal/reverse-prompt-engineer#v1.0.0
```

### Uninstall

```bash
claude plugin uninstall reverse-prompt-engineer@suraj-dhal
claude plugin marketplace remove suraj-dhal        # optional: also forget the marketplace
```

### Try it without installing

From a local clone, load it for one session only:

```bash
git clone https://github.com/Suraj-Dhal/reverse-prompt-engineer.git
claude --plugin-dir ./reverse-prompt-engineer
```

---

## OpenAI Codex

Codex reads this repository's marketplace file directly (it accepts the Claude-compatible `.claude-plugin/marketplace.json`), so the same marketplace serves both hosts.

```bash
codex plugin marketplace add Suraj-Dhal/reverse-prompt-engineer
codex plugin add reverse-prompt-engineer@suraj-dhal
codex plugin list        # reverse-prompt-engineer@suraj-dhal  installed, enabled  1.0.0
```

In the ChatGPT desktop app, after adding the marketplace, restart the app, open the **Plugins Directory**, choose the `suraj-dhal` marketplace and install **Reverse Prompt Engineer**.

Update or remove:

```bash
codex plugin marketplace upgrade suraj-dhal
codex plugin remove reverse-prompt-engineer@suraj-dhal
```

Codex shows the plugin with the listing metadata in `plugin.json` (`extensions.com.openai.interface`) and `.codex-plugin/plugin.json`: display name, short and long description, three starter prompts, the brand colour and the icon.

---

## Claude.ai and the Claude apps

Custom skills can be uploaded on Pro, Max, Team and Enterprise plans. Code execution must be enabled, because skills depend on it.

1. Download **`reverse-prompt-engineer-<version>-skill.zip`** from the [latest release](https://github.com/Suraj-Dhal/reverse-prompt-engineer/releases/latest). It contains a `reverse-prompt-engineer/` folder with `SKILL.md`, its references and assets, and a copy of the licence.
2. In Claude, open **Settings → Capabilities** and make sure **Code execution and file creation** is on.
3. In the **Skills** section, click **Upload skill** and choose the ZIP.
4. Make sure the skill is toggled on in your skills list.

Uploaded skills are private to your account. On Enterprise plans, an owner must first enable code execution and skills for the organisation. See Anthropic's help article [Using Skills in Claude](https://support.claude.com/en/articles/12512180-using-skills-in-claude) for current details.

You can also build the ZIP yourself from a clone: `python3 scripts/package.py` writes it to `dist/`.

---

## Other Agent Skills and Agent Plugins hosts

The skill follows the open [Agent Skills specification](https://agentskills.io/specification), and the repository root is a valid [Agent Plugins](https://agent-plugins.org/specification) package (`plugin.json` with skills in `skills/`).

- **Agent Plugins hosts:** point the host at the repository root, or at the extracted `reverse-prompt-engineer-<version>-plugin.zip`.
- **Agent Skills hosts:** copy the folder `skills/reverse-prompt-engineer/` into the host's skills directory. For example, for Claude Code *without* the plugin system:

  ```bash
  # personal (all projects)
  cp -r skills/reverse-prompt-engineer ~/.claude/skills/
  # or project-only
  cp -r skills/reverse-prompt-engineer .claude/skills/
  ```

The folder name must stay `reverse-prompt-engineer`, matching the `name` in `SKILL.md`.

---

## Check that it works

Paste this into a new conversation:

```text
What prompt could have produced this?

"Fresh coffee, friendly faces, and the best seat in town."
```

A working installation replies with exactly two sections, **Reconstructed Prompt** (one copy-ready block, probably with an `{{AUDIENCE}}` placeholder) and **Reasoning** (five labelled points ending with `Overall confidence: Low`), and does not claim to know the original prompt.

If the skill does not activate:

- Make sure it is enabled (`claude plugin list`, `codex plugin list`, or the toggle in Claude's skills settings).
- Start a new session after installing; skills are discovered at session start.
- Name it explicitly: "Use the reverse-prompt-engineer skill to …".
