# contributory-factors

A Claude skill that replaces "root cause" thinking with **contributory factors
analysis** — the systems-thinking approach used by the
[London Protocol 2024](https://www.imperial.ac.uk/centre-for-health-policy/our-work/our-publications/london-protocol/)
and the Yorkshire Contributory Factors Framework.

When this plugin is active, Claude:

- Avoids the terms "root cause", "root cause analysis", and "RCA".
- Reframes incident, failure, and debugging discussions around the multiple
  interacting factors that contribute to outcomes.
- Applies an eight-level framework (subject, individual, task, team, technology,
  environment, organisation, institutional context) to map contributory factors
  systematically.
- Distinguishes specific from general factors, and steers recommendations
  towards system conditions rather than individual blame.

## Why

"Root cause" framing implies a single point of failure, encourages backward-
looking blame, and stops investigation as soon as a plausible cause is found.
Decades of safety science — across healthcare, aviation, nuclear, and software
— show that complex outcomes emerge from many interacting conditions. The
London Protocol 2024 explicitly rejects RCA in favour of *systems analysis*
focused on contributory factors.

This plugin brings that discipline into everyday work with Claude: incident
post-mortems, debugging sessions, project retrospectives, troubleshooting, and
casual problem-solving alike.

## Installation

From the [`yo61/claude-skills`](https://github.com/yo61/claude-skills)
marketplace:

```text
/plugin marketplace add yo61/claude-skills
/plugin install contributory-factors@yo61-skills
```

## What's in the plugin

```
contributory-factors/
├── .claude-plugin/
│   └── plugin.json
└── skills/
    └── contributory-factors/
        ├── SKILL.md             # the skill itself
        └── references/
            └── background.md    # origins, theory, full citations
```

`SKILL.md` is loaded into Claude's context when the skill triggers.
`references/background.md` is referenced from `SKILL.md` and loaded on demand.

## Origins and credits

The framework adapted in this skill is the work of:

- **Charles Vincent and colleagues** — the
  [London Protocol](https://www.imperial.ac.uk/centre-for-health-policy/our-work/our-publications/london-protocol/)
  (1998, 2004, 2024).
- **Rebecca Lawton and the Yorkshire Quality and Safety Research Group** — the
  Yorkshire Contributory Factors Framework (Lawton et al., 2012).
- **James Reason** — the organisational accident model that underpins both.

Full citations are in
[`skills/contributory-factors/references/background.md`](skills/contributory-factors/references/background.md).

This plugin contains only the skill (a derived prompt-engineering artefact)
and references those works by citation. The original papers and protocol
documents are not redistributed here — read them at the publishers.

## License

[MIT](../../LICENSE)
