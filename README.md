# yo61-skills

A Claude Code plugin marketplace published by [yo61](https://github.com/yo61).

## Plugins

| Plugin | Repo | Description |
|---|---|---|
| `contributory-factors` | [`yo61/claude-plugin-contributory-factors`](https://github.com/yo61/claude-plugin-contributory-factors) | Replaces "root cause" thinking with contributory factors analysis (London Protocol 2024, Yorkshire Contributory Factors Framework). |
| `reportlab-pdf` | [`yo61/claude-plugin-reportlab-pdf`](https://github.com/yo61/claude-plugin-reportlab-pdf) | ReportLab-based PDF generation. Programmatic Platypus PDFs (CVs, invoices, reports) and a markdown-to-PDF renderer (mistune + Platypus). |
| `agent-team-topologies` | [`yo61/agent-team-topologies`](https://github.com/yo61/agent-team-topologies) | Reusable Claude Code agent team topology patterns. Topology selector skill plus 6 specialist subagents (explorer, architect, implementer, security/perf/test reviewers). |

## Use

In Claude Code:

```
/plugin marketplace add yo61/claude-skills
/plugin install contributory-factors
/plugin install reportlab-pdf
/plugin install agent-team-topologies
```

Refresh your local copy of the marketplace after a new release with:

```
/plugin marketplace update
```

## Versioning

This is a [release-please](https://github.com/googleapis/release-please)-managed marketplace. Each entry in `marketplace.json` pins to an exact release tag of its plugin repo. When a plugin cuts a new release, this marketplace bumps its `ref` and cuts its own release.

## License

MIT — see [LICENSE](LICENSE).
