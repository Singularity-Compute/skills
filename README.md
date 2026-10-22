# Singularity Compute agent skills

Skills that teach coding agents to build on [Super Decider](https://github.com/Singularity-Compute/super-decider), a decision model that returns a choice, a yes or no, a score or a copied span of text, with a calibrated probability for every answer.

The skill teaches a coding agent when a feature needs a decision instead of generated text, how to write the questions, how to read probabilities in code, and how to call the API. It bundles the API reference, a question-design guide, fourteen patterns and ten runnable examples, so it works without browsing.

## Install

### Claude Code plugin

```bash
claude plugin marketplace add Singularity-Compute/skills
claude plugin install super-decider@singularity-compute
```

### Other agents (Codex, Cursor, Gemini CLI and more) via skills.sh

```bash
npx skills add Singularity-Compute/skills --skill super-decider
```

Pick your agent when prompted. Add `-g` to install for all projects.

### Manually

Copy [`skills/super-decider/`](skills/super-decider/) into your agent's skills folder, for example `~/.claude/skills/super-decider/`.

## Use

Set `API_KEY` to a Super Decider key from [ASI:Cloud](https://asicloud.cudos.org/), then ask your agent, for example:

> Use Super Decider to route incoming support tickets by team, with human review when it is unsure.

> Add a guardrail that checks every message to and from our chatbot for prompt injection and personal data.

> We call Jev to classify leads. Switch the integration to Super Decider.

In Claude Code you can also invoke the skill directly with `/super-decider:super-decider`.

| Skill | Purpose |
|---|---|
| [super-decider](skills/super-decider/SKILL.md) | Design decisions, write the API calls, and apply patterns such as routing, guardrails, reranking, extraction and agent tool gating |

## License

[Apache-2.0](LICENSE)
