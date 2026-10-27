# Licensing

Reverse Prompt Engineer is released under the **MIT License**. This page explains in plain language what that allows, what it requires, what it covers, and a few related questions. The [`LICENSE`](../LICENSE) file is the legal text; if this summary and the licence ever differ, the licence wins.

> This page is general information, not legal advice. For a decision that matters (for example a commercial product or a legal dispute), consult a qualified lawyer in your jurisdiction.

## Summary

| You **can** | You **must** | You **cannot** expect |
|---|---|---|
| Use it for any purpose, personal or commercial | Keep the copyright notice and licence text in all copies or substantial portions | Any warranty or guarantee that it works or fits your purpose |
| Copy, modify and merge it into other work | | The author to be liable for any damage or loss |
| Publish, distribute and sublicense it | | |
| Sell it, or products that include it | | |
| Keep your modifications private or close their source | | |

## What the MIT License grants

The licence grants anyone who obtains a copy permission "to deal in the Software without restriction", explicitly including the rights to **use, copy, modify, merge, publish, distribute, sublicense, and/or sell** copies, and to let others do the same.

MIT is a *permissive* licence. Unlike "copyleft" licences such as the GPL, it does **not** require you to release your own changes, or the larger work you build, under the same licence. You can use this plugin inside a proprietary product or a closed company workflow.

## The one condition: keep the notice

The only condition is that **the copyright notice and the permission notice are included in all copies or substantial portions of the Software**. In practice:

- **Redistributing the plugin** (as is, modified, in a ZIP, or in another marketplace): keep the `LICENSE` file. The skill-only ZIP on the Releases page already contains it as `LICENSE.txt`, and the skill's frontmatter declares `license: MIT`.
- **Copying a substantial portion** (for example most of `SKILL.md` or a playbook into your own skill): include the notice alongside it, for example in your own licence file or a `THIRD-PARTY-NOTICES` file.
- **Using it** (installing it and running it, including at work): no action needed.

Attribution is not required beyond keeping the notice, but it is appreciated. A good form is:

```text
Based on Reverse Prompt Engineer by Suraj Dhal (https://github.com/Suraj-Dhal/reverse-prompt-engineer), MIT License.
```

## No warranty, no liability

The software is provided **"as is", without warranty of any kind**. The author is not liable for any claim, damages or other liability arising from its use. In particular, reconstructed prompts are inferences: they may be wrong or incomplete, and you are responsible for checking them before relying on them.

## What the licence covers

The MIT License applies to **everything in this repository** unless a file says otherwise:

- the skill (`skills/reverse-prompt-engineer/**`: `SKILL.md`, references, assets),
- the manifests and marketplace files,
- the scripts, tests, eval fixtures and generated eval suite,
- the documentation in `docs/` and the Markdown files at the repository root,
- the icon (`assets/icon.png`, `assets/icon.svg`), an original design made for this project.

No third-party code, text or artwork is bundled in the repository.

## Third-party tools and services

The project *uses* some tools that are not part of it and are not covered by this licence:

| Tool | Used for | Notes |
|---|---|---|
| Python standard library | All scripts | Python Software Foundation License |
| [`jsonschema`](https://pypi.org/project/jsonschema/) | Optional fixture schema tests in CI | MIT; not bundled, installed only for testing |
| Claude Code (`claude plugin validate`, `claude plugin eval`) | Validation and behavioural evals | Anthropic's terms apply to your use |
| GitHub Actions | Continuous integration and releases | GitHub's terms apply |
| AI host models (Claude, OpenAI models, …) | Running the skill | The provider's terms apply to your use of their service |

## Your outputs

The licence covers this plugin's own files. It does not claim any rights over the **prompts, text or other outputs you create while using it**; those are governed by your agreement with the AI provider you use and by the law that applies to you. Reconstructing a prompt does not give you rights to the original output or its source material, so respect the rights of whoever created the content you analyse.

## Trademarks

"Claude" and "Anthropic" are trademarks of Anthropic, PBC. "OpenAI", "ChatGPT" and "Codex" are trademarks of OpenAI. Other names may be trademarks of their respective owners. They are used here only to describe compatibility. **This project is independent and is not affiliated with, sponsored by or endorsed by Anthropic, OpenAI or any other company.** The MIT License grants no rights to use these trademarks, or the name "Reverse Prompt Engineer", in a way that suggests endorsement.

## Contributions

Unless a contributor explicitly states otherwise, any contribution intentionally submitted to this repository (for example a pull request) is licensed under the same MIT License ("inbound = outbound"). Contributors keep their copyright and should only submit work they have the right to license. See [CONTRIBUTING.md](../CONTRIBUTING.md).

## Versions and relicensing

Each released version is licensed under the terms in its `LICENSE` file at that tag. The copyright holder may release *future* versions under different terms, but cannot withdraw the MIT permissions already granted for versions released under MIT.

The original v0.2.0 package was published without a licence file. It is included in this repository's history at tag `v0.2.0` for auditability, and is made available under the MIT License by its author, together with everything else in the repository.

## FAQ

**Can I use this at my company, or in client work?**
Yes. Commercial use is allowed with no fee and no need to ask.

**Can I sell a product that includes it?**
Yes, as long as the copyright and licence notice stays with the copies you distribute.

**Do I have to open-source my changes?**
No. MIT does not require you to share modifications.

**Can I remove the licence or the author's name?**
Not from copies or substantial portions you distribute. That notice is the licence's only condition.

**Can I publish a modified version in my own marketplace?**
Yes. Keep the `LICENSE` file, change the plugin `name` so users don't confuse it with the original, and don't imply endorsement.

**Can I translate the skill into another language?**
Yes. A translation is a modification; keep the notice.

**Is there a warranty that reconstructions are correct?**
No. See [No warranty, no liability](#no-warranty-no-liability) and the [limitations](how-it-works.md#9-limitations).

**Who do I ask about licensing?**
Open an issue on GitHub, or email the author at surajbbsr2007@gmail.com.
