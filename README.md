# yo61 Claude Skills

A [Claude Code plugin marketplace](https://code.claude.com/docs/en/plugin-marketplaces)
hosting skills published by [yo61](https://github.com/yo61).

## Installation

Add this marketplace to Claude Code:

```text
/plugin marketplace add yo61/claude-skills
```

Then install whichever plugin you want:

```text
/plugin install <plugin-name>@yo61-skills
```

## Available plugins

| Plugin | Description |
| ------ | ----------- |
| [`contributory-factors`](plugins/contributory-factors) | Replaces "root cause" thinking with contributory factors analysis based on the London Protocol 2024 and the Yorkshire Contributory Factors Framework. |
| [`reportlab-pdf`](plugins/reportlab-pdf) | Generate professional, multi-page PDF documents using Python's ReportLab Platypus layout engine. |

## Updating

Pull the latest plugin manifests:

```text
/plugin marketplace update yo61-skills
```

Then reinstall a plugin to pick up its newest version:

```text
/plugin install <plugin-name>@yo61-skills
```

## Repository layout

```
.
├── .claude-plugin/
│   └── marketplace.json          # marketplace manifest (lists plugins)
├── plugins/
│   └── <plugin-name>/            # one directory per plugin
│       ├── .claude-plugin/
│       │   └── plugin.json       # plugin manifest
│       ├── README.md
│       └── skills/
│           └── <skill-name>/
│               ├── SKILL.md
│               └── references/   # optional supporting material
└── README.md
```

Each plugin is self-contained under `plugins/<name>/` with its own manifest,
versioning, and documentation. The top-level `marketplace.json` lists every
plugin in the repo and points at its subdirectory via a relative path.

## Adding a new plugin

1. Create `plugins/<plugin-name>/.claude-plugin/plugin.json`.
2. Put skills under `plugins/<plugin-name>/skills/<skill-name>/SKILL.md`.
3. Add an entry for the plugin to `.claude-plugin/marketplace.json`.
4. Document the plugin in its own `plugins/<plugin-name>/README.md` and add
   a row to the table above.

## Contributing

Issues and pull requests welcome.

## License

[MIT](LICENSE)
