# Polyrepo migration — design

Date: 2026-05-18
Status: approved (pending implementation plan)
Tracking issue: [#7](https://github.com/yo61/claude-skills/issues/7)
Supersedes: [`2026-05-18-release-automation-design.md`](2026-05-18-release-automation-design.md)

## Summary

Split the two plugins out of `yo61/claude-skills` into their own GitHub repositories — `yo61/claude-plugin-contributory-factors` and `yo61/claude-plugin-reportlab-pdf` — and reduce `yo61/claude-skills` to a marketplace-only repo. `marketplace.json` keeps each plugin entry but uses `source: { source: "github", repo: ..., ref: "vX.Y.Z" }` to pin each plugin to an exact release tag. Each of the three repos runs its own release-please simple-mode setup. The complex monorepo machinery from the superseded spec (sync script, locked commit scopes, component-tagged release-please) is gone.

## Motivation

The monorepo design (see superseded spec) was paying significant complexity to compensate for a structure that didn't reflect the plugins' actual independence. `contributory-factors` and `reportlab-pdf` share nothing except both being mine. They have separate concerns, separate release cadences, and the original trigger for this work — per-plugin `gh release-stats` telemetry — is *trivially* solved when each plugin is its own repo.

Concretely, the monorepo design required:

- A `sync_marketplace.py` script that regenerated `marketplace.json` from canonical inputs.
- A pre-commit hook + a workflow step running that script to push sync commits into open Release PRs.
- `commitlint` with a locked `scope-enum` (so release-please could route commits to the right plugin).
- `release-please-config.json` with `include-component-in-tag: true` and per-package `extra-files` entries.
- A `Release-As:` bootstrap dance to populate the first GitHub Releases.

The polyrepo design drops every one of those. Each plugin gets a textbook release-please setup. The marketplace becomes a hand-curated list of pointers — small, simple, occasionally updated.

A secondary motivator: independent GitHub presence per plugin. Each plugin gets its own README homepage, issue tracker, stars/watchers, releases page, and search visibility. The marketplace becomes navigation, not the home for each plugin.

## Decisions

### D1 — Three-repo polyrepo topology

The end state:

| Repo | Role | Current state |
|---|---|---|
| `yo61/claude-plugin-contributory-factors` | Owns the `contributory-factors` plugin | New |
| `yo61/claude-plugin-reportlab-pdf` | Owns the `reportlab-pdf` plugin | New |
| `yo61/claude-skills` | Marketplace-only; lists the two plugin repos | Exists; needs significant cleanup |

The `claude-plugin-` prefix on plugin repos signals their purpose at a glance for casual GitHub visitors. The marketplace repo keeps its current name (`claude-skills`) — renaming would break the `/plugin marketplace add yo61/claude-skills` invocation users have already adopted.

**Trade-off accepted:** three repos to maintain instead of one. Solo maintenance with two plugins makes this cost low and bounded.

### D2 — Git history preserved via `git filter-repo --subdirectory-filter`

Each plugin repo is bootstrapped from a fresh clone of `yo61/claude-skills` filtered down to just that plugin's directory. The filter command rewrites history so `plugins/<name>/` becomes the new repo root and only commits that touched that subdirectory survive.

**Trade-off accepted:** requires installing `git-filter-repo` locally (`brew install git-filter-repo`). The result is per-file `git blame` archaeology that still makes sense after the move.

**Alternative considered:** fresh-start initial commits with a "extracted from ..." pointer. Rejected because the existing per-plugin history is short but useful — `md-to-pdf` skill's evolution is worth preserving on the `reportlab-pdf` side.

### D3 — Standard release-please simple mode in each plugin repo

Each plugin repo uses `release-type: simple` with a single package. Tags are bare `vX.Y.Z` (no component prefix). Manifest pre-populated with the existing declared version:

- `claude-plugin-contributory-factors`: starts at `1.0.0`
- `claude-plugin-reportlab-pdf`: starts at `1.2.0`

`extra-files` updates the `version` field in `.claude-plugin/plugin.json` via jsonpath `$.version`. No `marketplace.json` to worry about in plugin repos — that lives only in the marketplace repo.

**Trade-off accepted:** none meaningful. This is the canonical release-please setup the tool was designed for.

### D4 — Marketplace repo also runs release-please for its own versioning

`yo61/claude-skills` gets release-please too, in simple mode, tracking its own `marketplace.json` `version` field. Starts at `v0.1.0` (the "start at v0.1.0" instruction from the original task lands here — on the marketplace, not on the plugins). When the marketplace repo bumps a plugin's pinned `ref`, that's a release-worthy event with its own CHANGELOG entry.

**Trade-off accepted:** one more release-please setup. Pays off by giving users a versioned marketplace and a changelog that shows which plugin versions shipped together at each marketplace release.

### D5 — Exact-tag pinning in `marketplace.json`; manual bumps initially

Each marketplace entry pins to `ref: vX.Y.Z`. When a plugin cuts a new release in its own repo, a human updates `marketplace.json` and lets release-please cut a new marketplace release.

**Alternative considered:** rolling major tags (`ref: v1`), no pinning (always default branch), or automated bumps via `repository_dispatch` from each plugin repo. The exact-tag-with-manual-bump option ships fastest, keeps releases as deliberate events, and leaves an obvious next-step automation that can be added once the manual ceremony gets annoying.

### D6 — Marketplace entry fields: `name`, `source`, `category`, `tags`, `description`

Each entry in `marketplace.json` contains these five fields. `description` is duplicated from the plugin's `plugin.json` — accepted drift, because it's updated at the same time as the `ref` bump. `category` and `tags` (the marketplace docs use `tags`, not `keywords`) live only in `marketplace.json` — they're discovery metadata, not plugin behaviour.

**Trade-off accepted:** description duplication. Mitigated by the fact that descriptions change rarely and are touched in the same PR as version bumps.

### D7 — Conventional Commits per repo; no `scope-enum`

Each repo runs `commitlint` with `@commitlint/config-conventional` extended. **No** `scope-enum` rule — each repo is a single package, so scope is decorative. `subject-case` relaxed to `[0]` (matches jobhound's pattern: allow identifiers like `Palette` to start a subject).

**Trade-off accepted:** loss of cross-repo scope conventions. Worth it for simpler config.

### D8 — All actions pinned to 40-char SHAs with `# vX.Y.Z` comments

Same policy as the superseded spec. Every `uses:` resolves to a full commit SHA with a human-readable version trailing comment. SHAs are looked up at implementation time, not guessed.

### D9 — Default `GITHUB_TOKEN` everywhere

Each repo's release workflow uses the default `GITHUB_TOKEN` with job-scoped `contents: write` + `pull-requests: write`. No App-token plumbing initially. The `github-actions[bot]`-PRs-don't-trigger-workflows trap (from jobhound) only bites when there's branch protection requiring CI. None of these repos have that yet. App-token migration is a per-repo follow-up.

### D10 — pre-commit kept minimal per repo

Each repo gets `.pre-commit-config.yaml` with one hook only: `commitlint` on `commit-msg` stage. Plugin repos may grow additional hooks later (e.g., `ruff` for `reportlab-pdf` if Python content expands) — out of scope for this work.

### D11 — Marketplace repo cleanup deletes monorepo-era artifacts

In the same branch/PR that converts the marketplace, the following are deleted:

- `plugins/` directory (extracted into separate repos).
- `docs/superpowers/specs/2026-05-18-release-automation-design.md` (superseded; this file replaces it).
- `docs/superpowers/plans/2026-05-18-release-automation.md` (superseded).

No deprecation shims, no migration notes left in place. The git history retains the superseded files; current state is clean.

## Architecture

### Each plugin repo's file layout

```
yo61/claude-plugin-<name>/
├── .claude-plugin/
│   └── plugin.json              ← release-please bumps `version` here
├── .github/
│   ├── ISSUE_TEMPLATE/
│   │   └── feature.md           ← copied from claude-skills
│   └── workflows/
│       └── release.yml          ← SHA-pinned release-please
├── .pre-commit-config.yaml
├── .release-please-manifest.json  ← { ".": "1.0.0" } or { ".": "1.2.0" }
├── CHANGELOG.md                  ← created on first release
├── LICENSE                       ← copied from claude-skills
├── README.md                     ← keep / adapt
├── commitlint.config.mjs
├── release-please-config.json
└── (plugin content: skills/, hooks/, agents/, etc.)
```

### Marketplace repo's final file layout

```
yo61/claude-skills/
├── .claude-plugin/
│   └── marketplace.json         ← hand-edited; lists two github-sourced plugins
├── .github/
│   ├── ISSUE_TEMPLATE/
│   │   └── feature.md           ← already exists
│   └── workflows/
│       └── release.yml          ← SHA-pinned release-please for marketplace
├── .pre-commit-config.yaml
├── .release-please-manifest.json  ← { ".": "0.1.0" }
├── CHANGELOG.md                  ← created on first release
├── LICENSE                       ← keep
├── README.md                     ← rewritten for marketplace-only role
├── commitlint.config.mjs
├── docs/
│   └── superpowers/
│       ├── specs/
│       │   └── 2026-05-18-polyrepo-migration-design.md  ← this file
│       └── plans/
│           └── 2026-05-18-polyrepo-migration.md
└── release-please-config.json
```

No `plugins/` directory. No `scripts/`. No `marketplace-config.json`. Just the marketplace.json and release-please plumbing.

### Final `marketplace.json` shape

```json
{
  "name": "yo61-skills",
  "owner": {
    "name": "yo61",
    "email": "robin@yo61.com"
  },
  "description": "Claude Code skills published by yo61",
  "version": "0.1.0",
  "plugins": [
    {
      "name": "contributory-factors",
      "description": "Replaces 'root cause' thinking with contributory factors analysis based on the London Protocol 2024 and the Yorkshire Contributory Factors Framework.",
      "category": "thinking",
      "tags": [
        "incident-analysis",
        "post-mortem",
        "debugging",
        "systems-thinking",
        "safety",
        "root-cause-analysis"
      ],
      "source": {
        "source": "github",
        "repo": "yo61/claude-plugin-contributory-factors",
        "ref": "v1.0.0"
      }
    },
    {
      "name": "reportlab-pdf",
      "description": "ReportLab-based PDF generation. Two skills: programmatic Platypus PDFs (CVs, invoices, reports) and a markdown-to-PDF renderer (mistune + Platypus).",
      "category": "document-generation",
      "tags": [
        "pdf",
        "reportlab",
        "platypus",
        "markdown",
        "mistune",
        "md-to-pdf",
        "document",
        "cv",
        "report",
        "letter",
        "invoice",
        "typography"
      ],
      "source": {
        "source": "github",
        "repo": "yo61/claude-plugin-reportlab-pdf",
        "ref": "v1.2.0"
      }
    }
  ]
}
```

Notes:

- Field rename: the old `keywords` becomes `tags` (the marketplace docs' canonical field name).
- The `source` field becomes a `github` object with `ref` pin.
- A `version` field at the top level captures the marketplace's own version, managed by release-please via `extra-files` jsonpath `$.version`.

### Plugin-repo release workflow shape

Same on both plugin repos (and analogous on the marketplace repo, minus the `extra-files` update):

```yaml
name: Release

on:
  push:
    branches: [main]

permissions: {}

jobs:
  release-please:
    runs-on: ubuntu-latest
    permissions:
      contents: write
      pull-requests: write
    steps:
      - uses: googleapis/release-please-action@<SHA>  # vX.Y.Z
        with:
          config-file: release-please-config.json
          manifest-file: .release-please-manifest.json
```

No second job. No sync. No checkout. No conditionals. The simplest release-please workflow that can exist.

### Plugin-repo `release-please-config.json` shape

```json
{
  "$schema": "https://raw.githubusercontent.com/googleapis/release-please/main/schemas/config.json",
  "include-v-in-tag": true,
  "release-type": "simple",
  "packages": {
    ".": {
      "package-name": "<plugin-name>",
      "changelog-path": "CHANGELOG.md",
      "extra-files": [
        {
          "type": "json",
          "path": ".claude-plugin/plugin.json",
          "jsonpath": "$.version"
        }
      ]
    }
  }
}
```

Marketplace repo's variant updates `.claude-plugin/marketplace.json` `$.version` instead, and has no `extra-files` for any plugin (those live in the plugin repos).

## Migration procedure

The high-level sequence. The implementation plan will turn each phase into bite-sized steps.

### Phase 1 — Extract each plugin into a new repo (per plugin)

1. Fresh clone `yo61/claude-skills` to a working directory outside this workspace.
2. Run `git filter-repo --subdirectory-filter plugins/<name>` in that clone. Result: a repo whose root contains the plugin's files and whose history contains only commits that touched the plugin.
3. Create the new GitHub repo (`yo61/claude-plugin-<name>`) via `gh repo create`.
4. Add the LICENSE file (copied from `claude-skills`).
5. Add release-please scaffolding (manifest, config, workflow, pre-commit, commitlint).
6. Push to the new remote.

### Phase 2 — Cut the initial release in each plugin repo

For each plugin repo:

1. Land an empty bootstrap commit on `main` with `Release-As: <version>` footer (`1.0.0` for contributory-factors, `1.2.0` for reportlab-pdf).
2. release-please opens a Release PR.
3. Merge the PR. release-please tags `v1.0.0` / `v1.2.0` and creates the GitHub Release.
4. Verify `gh release list` shows the release.

### Phase 3 — Refactor `claude-skills` into marketplace-only

1. Delete `plugins/` directory.
2. Delete the superseded spec and plan files.
3. Add release-please scaffolding (config, manifest at `v0.1.0`, workflow, pre-commit, commitlint).
4. Rewrite `marketplace.json` to use `github` source entries with exact-tag pins.
5. Rewrite `README.md` for the marketplace-only role.
6. Land an empty bootstrap commit with `Release-As: 0.1.0`.
7. Merge the Release PR. First marketplace release lands.

### Phase 4 — Verify end-to-end

1. `/plugin marketplace remove yo61/claude-skills && /plugin marketplace add yo61/claude-skills` in a test session.
2. `/plugin install contributory-factors` — verify it pulls from the new plugin repo at `v1.0.0` and works.
3. Same for `reportlab-pdf`.
4. `gh release-stats` against each plugin repo — non-empty.
5. Close issue #7.

## Failure modes and mitigations

| Failure mode | Mitigation |
|---|---|
| `git filter-repo` produces an empty or broken history for a plugin. | Verify with `git log --oneline` and a representative `git blame` after the filter. If broken, fall back to a fresh-start initial commit. |
| Plugin repo's first release-please run fails (manifest/config mismatch). | Catch in the per-repo bootstrap step. The Release PR diff makes the problem visible before merge. |
| `marketplace.json`'s `github` source doesn't resolve because a plugin repo isn't yet public when the marketplace tries to install. | Sequence the work: create + release plugin repos *first*, then refactor the marketplace, then verify the install path. |
| Old monorepo files left behind in `claude-skills`. | Phase 3 deletes them explicitly. A `git status` check at the end of Phase 3 surfaces any stragglers. |
| `git-filter-repo` not installed locally. | Step 1 of Phase 1 installs it (`brew install git-filter-repo`). |
| Existing users still have the old marketplace cached. | `/plugin marketplace update` refreshes it. Mentioned in the marketplace README. |

## Out of scope (tracked separately)

For now there are no follow-up issues open — they'll be filed inside each plugin repo (and possibly the marketplace repo) when those repos exist and the corresponding need arises. Anticipated future work:

- **Per-repo CI workflow** — commitlint, plugin-content lint, etc. File in each plugin repo and the marketplace repo.
- **Per-repo tarball release assets** — for unambiguous install-stat measurement. File in each plugin repo.
- **Per-repo branch protection + GitHub App token** — when CI gates are introduced. File in each repo.
- **Marketplace auto-update workflow** — `repository_dispatch` from plugin repos triggers marketplace.json bumps automatically. File in the marketplace repo once manual bumps become annoying.

## Open questions (resolved during implementation)

- **Exact `release-please-action` output shape.** Same caveat as in the superseded spec, but with much smaller blast radius here — the workflow has only one step. Verified at the pinned SHA during implementation.
- **`extra-files` JSON updater behaviour** on `plugin.json` / `marketplace.json`. Verified via a dry-run release-please invocation against a throwaway branch in each repo.
- **Whether GitHub's automatic redirect handles old marketplace consumers** after any URL changes (there are none planned in this work, but if the marketplace repo were ever renamed, this is the answer to want).
