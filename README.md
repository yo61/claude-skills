# yo61-skills

A Claude Code plugin marketplace published by [yo61](https://github.com/yo61).

## Plugins

| Plugin | Repo | Description |
|---|---|---|
| `contributory-factors` | [`yo61/claude-plugin-contributory-factors`](https://github.com/yo61/claude-plugin-contributory-factors) | Replaces "root cause" thinking with contributory factors analysis (London Protocol 2024, Yorkshire Contributory Factors Framework). |
| `reportlab-pdf` | [`yo61/claude-plugin-reportlab-pdf`](https://github.com/yo61/claude-plugin-reportlab-pdf) | ReportLab-based PDF generation. Programmatic Platypus PDFs (CVs, invoices, reports) and a markdown-to-PDF renderer (mistune + Platypus). |
| `agent-team-topologies` | [`yo61/agent-team-topologies`](https://github.com/yo61/agent-team-topologies) | Reusable Claude Code agent team topology patterns. Topology selector skill plus 6 specialist subagents (explorer, architect, implementer, security/perf/test reviewers). |
| `civi-mcp` | [`yo61/civi-mcp`](https://github.com/yo61/civi-mcp) | Read-only CiviCRM access over APIv4. An MCP server with four generic query tools (`list_entities`, `describe_entity`, `get`, `count`) and a companion skill with CRM workflow heuristics. Prompts for site URL and API key at install time; the key is stored in the system keychain. |
| `lastlight-pr-gate` | [`yo61/claude-plugin-lastlight-pr-gate`](https://github.com/yo61/claude-plugin-lastlight-pr-gate) | Stops unreviewed commits reaching a remote: every push needs a local Last Light PR review recorded at that exact SHA, run with Last Light's own review skill pulled from npm. |
| `guardrails` | [`yo61/claude-plugin-guardrails`](https://github.com/yo61/claude-plugin-guardrails) | Deterministic `PreToolUse` guardrails for the Bash tool. Blocks known-wrong shell commands (`grep -r`, `rg -rn`, `which`, `rm -rf`, `find -name`, legacy toolchains) and bash-only syntax that breaks under zsh, handing back the correct form. |

## Use

In Claude Code:

```
/plugin marketplace add yo61/claude-skills
/plugin install contributory-factors
/plugin install reportlab-pdf
/plugin install agent-team-topologies
/plugin install civi-mcp
/plugin install lastlight-pr-gate
/plugin install guardrails
```

Refresh your local copy of the marketplace after a new release with:

```
/plugin marketplace update
```

## Versioning

This is a [release-please](https://github.com/googleapis/release-please)-managed marketplace. Each entry in `marketplace.json` pins to an exact release tag of its plugin repo. When a plugin cuts a new release, this marketplace bumps its `ref` and cuts its own release.

## License

MIT — see [LICENSE](LICENSE).
