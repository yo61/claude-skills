# Polyrepo migration implementation plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Split the two plugins out of `yo61/claude-skills` into their own GitHub repos with per-plugin release-please pipelines, and reduce `yo61/claude-skills` to a marketplace-only repo with github-source pins.

**Architecture:** Three repos at the end (`yo61/claude-plugin-contributory-factors`, `yo61/claude-plugin-reportlab-pdf`, `yo61/claude-skills` slimmed-down). Each plugin repo is bootstrapped via `git filter-repo --subdirectory-filter` to preserve history, then scaffolded with a standard release-please simple-mode setup. The marketplace repo's `marketplace.json` pins each plugin entry to an exact release tag (`ref: vX.Y.Z`). Manual marketplace bumps for now; automation deferred.

**Tech Stack:** `git-filter-repo` (history extraction); `gh` CLI (repo creation, releases); `release-please-action` v4+ (releases); `commitlint` + `@commitlint/config-conventional`; `pre-commit`; Conventional Commits.

---

## Working assumptions

- Working from `/Users/robin/code/github/yo61/claude-skills` on branch `add-release-automation` (already created, 2 commits ahead of main: issue template + new spec).
- `gh` CLI is authenticated against the `yo61` GitHub user/org.
- `git-filter-repo` may or may not be installed locally — Task 1 verifies and installs if needed.
- `pre-commit` and `node`/`npm` are installable locally (`brew install pre-commit node` if not present).
- All commits use Conventional Commits and end with the `Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>` trailer.
- Per the user's personal-repo workflow: feature branch → ff-merge to main locally → delete; no PRs for personal repos. The plugin repos and marketplace repo each follow this for the bootstrap branches.
- Working extraction directory: `/tmp/polyrepo-extract/` (auto-cleaned by macOS on reboot; nothing precious there).
- **Pause and confirm with the user before any task that creates a GitHub repository, force-pushes, or merges a Release PR.** These affect shared state and are not freely reversible.

---

## Task 1: Prerequisites

**Files:** none changed. Verification only.

### Step 1.1 — Verify `gh` is authenticated for `yo61`

```bash
gh api user --jq '.login'
```

Expected: prints `yo61` (or `RobinBowes`, whichever GitHub login is the canonical owner of the repos). If it prints anything else, run `gh auth login` interactively before continuing.

### Step 1.2 — Verify `git-filter-repo` is installed; install if not

```bash
which git-filter-repo || brew install git-filter-repo
git-filter-repo --version
```

Expected: prints a version (e.g., `2.45.0`).

### Step 1.3 — Verify `pre-commit` is installed; install if not

```bash
which pre-commit || brew install pre-commit
pre-commit --version
```

Expected: prints a version (e.g., `4.0.1`).

### Step 1.4 — Capture the source repo path and confirm clean working tree

```bash
SOURCE_REPO=/Users/robin/code/github/yo61/claude-skills
cd "$SOURCE_REPO"
git status
git log --oneline main..HEAD
```

Expected: clean working tree on branch `add-release-automation`, two commits ahead of main:

```
d6ad7e0 docs: add polyrepo migration design spec
5d341d9 chore: add issue template for features and tasks
```

### Step 1.5 — Ensure the extract working directory exists and is empty

```bash
mkdir -p /tmp/polyrepo-extract
rm -rf /tmp/polyrepo-extract/*
ls /tmp/polyrepo-extract
```

Expected: empty directory.

### Step 1.6 — Look up SHAs for the actions we'll pin (used in every workflow we write)

```bash
resolve_sha() {
  local repo="$1"
  local tag
  tag=$(gh api "repos/${repo}/releases/latest" --jq '.tag_name')
  local sha
  sha=$(git ls-remote "https://github.com/${repo}" "refs/tags/${tag}^{}" | awk '{print $1}')
  if [ -z "$sha" ]; then
    sha=$(git ls-remote "https://github.com/${repo}" "refs/tags/${tag}" | awk '{print $1}')
  fi
  echo "${repo}@${sha}  # ${tag}"
}

resolve_sha googleapis/release-please-action
```

Record the output as `RP_SHA  # RP_TAG`. We'll need this exact line for every plugin repo's `release.yml` and the marketplace repo's `release.yml`. (No `actions/checkout` or `astral-sh/setup-uv` needed in the polyrepo design — each release.yml has only one step.)

---

## Task 2: Extract and scaffold `claude-plugin-contributory-factors`

**Pause and confirm with the user before Step 2.4 (creating the GitHub repo).**

**Files (in the extracted repo, after filter-repo):**
- Create: `LICENSE`
- Create: `.gitignore`
- Create: `.github/ISSUE_TEMPLATE/feature.md`
- Create: `.github/workflows/release.yml`
- Create: `.pre-commit-config.yaml`
- Create: `commitlint.config.mjs`
- Create: `release-please-config.json`
- Create: `.release-please-manifest.json`

### Step 2.1 — Clone the source repo into the extract directory

```bash
cd /tmp/polyrepo-extract
git clone /Users/robin/code/github/yo61/claude-skills claude-plugin-contributory-factors
cd claude-plugin-contributory-factors
git log --oneline | wc -l
```

Expected: clone succeeds; total commit count printed (e.g., 17).

### Step 2.2 — Run `git filter-repo` to extract just the plugin subdir

```bash
git filter-repo --subdirectory-filter plugins/contributory-factors --force
ls -la
git log --oneline | wc -l
```

Expected: working tree now shows the plugin's files (`.claude-plugin/`, `README.md`, `skills/`) at the repo root. Commit count is smaller than before (only commits that touched `plugins/contributory-factors/` survived).

### Step 2.3 — Spot-check the extracted history

```bash
git log --oneline -10
git log --all --oneline | head -20
```

Expected: every visible commit subject relates to `contributory-factors` (no `reportlab-pdf` or `md-to-pdf` references). The initial commit `171119e Initial commit: yo61-skills marketplace with contributory-factors plugin` should still be reachable (it introduced the plugin).

### Step 2.4 — Create the GitHub repo (USER CONFIRMATION GATE)

**Stop and confirm with the user before running this step.**

```bash
gh repo create yo61/claude-plugin-contributory-factors \
  --public \
  --description "Claude Code plugin: replaces 'root cause' thinking with contributory factors analysis (London Protocol 2024, Yorkshire Contributory Factors Framework)."
```

Expected: prints the new repo's URL.

### Step 2.5 — Add topics for discoverability

```bash
gh repo edit yo61/claude-plugin-contributory-factors \
  --add-topic claude-code \
  --add-topic claude-code-plugin \
  --add-topic incident-analysis \
  --add-topic systems-thinking
```

Expected: silent success.

### Step 2.6 — Copy LICENSE from the source repo

```bash
cp /Users/robin/code/github/yo61/claude-skills/LICENSE LICENSE
git add LICENSE
```

### Step 2.7 — Create `.gitignore`

Create `.gitignore`:

```
# macOS
.DS_Store

# Editors
.vscode/
.idea/

# Python (defensive — no Python in this plugin today, but cheap to include)
__pycache__/
*.py[cod]
*.egg-info/
.pytest_cache/
.ruff_cache/

# Misc
*.log
*.tmp
```

### Step 2.8 — Copy issue template from the source repo

```bash
mkdir -p .github/ISSUE_TEMPLATE
cp /Users/robin/code/github/yo61/claude-skills/.github/ISSUE_TEMPLATE/feature.md \
   .github/ISSUE_TEMPLATE/feature.md
```

### Step 2.9 — Create `commitlint.config.mjs`

Create `commitlint.config.mjs`:

```javascript
export default {
  extends: ['@commitlint/config-conventional'],
  rules: {
    // No scope-enum: this repo is a single package, so scope is decorative.
    // Subject case relaxation: allow identifiers like Palette or OpportunityQuery
    // to start a subject. Matches yo61/jobhound's commitlint config.
    'subject-case': [0],
  },
};
```

### Step 2.10 — Create `.pre-commit-config.yaml`

First, look up the latest tag for the commitlint hook:

```bash
gh api repos/alessandrojcm/commitlint-pre-commit-hook/releases/latest --jq '.tag_name'
```

Record as `COMMITLINT_HOOK_TAG` (e.g., `v9.25.0`). Substitute below.

Create `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: https://github.com/alessandrojcm/commitlint-pre-commit-hook
    rev: <COMMITLINT_HOOK_TAG>
    hooks:
      - id: commitlint
        stages: [commit-msg]
        additional_dependencies:
          - "@commitlint/config-conventional@^21"
```

### Step 2.11 — Create `release-please-config.json`

Create `release-please-config.json`:

```json
{
  "$schema": "https://raw.githubusercontent.com/googleapis/release-please/main/schemas/config.json",
  "include-v-in-tag": true,
  "release-type": "simple",
  "packages": {
    ".": {
      "package-name": "contributory-factors",
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

### Step 2.12 — Create `.release-please-manifest.json` at current version

Create `.release-please-manifest.json` (no trailing newline, matching jobhound's convention):

```json
{".":"1.0.0"}
```

### Step 2.13 — Create `.github/workflows/release.yml`

Substitute the `RP_SHA  # RP_TAG` recorded in Step 1.6:

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
      - uses: googleapis/release-please-action@<RP_SHA>  # <RP_TAG>
        with:
          config-file: release-please-config.json
          manifest-file: .release-please-manifest.json
```

### Step 2.14 — Stage everything and commit

```bash
git add LICENSE .gitignore .github/ \
        .pre-commit-config.yaml commitlint.config.mjs \
        release-please-config.json .release-please-manifest.json
git status
```

Expected: 8 files staged.

```bash
git commit -m "$(cat <<'EOF'
feat: add release-please scaffolding and supporting config

Adds LICENSE (MIT, from yo61/claude-skills), .gitignore, the feature/task
issue template, a release.yml workflow running release-please in simple
mode with SHA-pinned actions, commitlint config (no scope-enum since this
is a single-package repo), pre-commit config with commitlint on commit-msg,
release-please-config.json with extra-files updating .claude-plugin/plugin.json,
and the manifest pre-populated at 1.0.0.

Extracted from yo61/claude-skills@d6ad7e0 via:
  git filter-repo --subdirectory-filter plugins/contributory-factors

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

### Step 2.15 — Add the remote and push

```bash
git remote add origin git@github.com:yo61/claude-plugin-contributory-factors.git
git push -u origin main
```

Expected: push succeeds.

### Step 2.16 — Verify the first workflow run completes

```bash
gh run watch --repo yo61/claude-plugin-contributory-factors --exit-status
```

Expected: workflow succeeds. release-please runs but does NOT open a PR (there are no new conventional commits since the manifest was initialised at 1.0.0).

---

## Task 3: Bootstrap the first release for `claude-plugin-contributory-factors`

**Pause and confirm with the user before Step 3.4 (merging a release PR).**

### Step 3.1 — From the extracted clone, create a bootstrap branch

```bash
cd /tmp/polyrepo-extract/claude-plugin-contributory-factors
git checkout -b bootstrap-v1.0.0
```

### Step 3.2 — Create the bootstrap commit

```bash
git commit --allow-empty -m "$(cat <<'EOF'
chore: release 1.0.0

Release-As: 1.0.0

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

### Step 3.3 — Push, ff-merge to main locally, delete the bootstrap branch

```bash
git push -u origin bootstrap-v1.0.0
git checkout main
git merge --ff-only bootstrap-v1.0.0
git push origin main
git push origin --delete bootstrap-v1.0.0
git branch -d bootstrap-v1.0.0
```

### Step 3.4 — Wait for the release-please workflow run to open the Release PR

```bash
gh run watch --repo yo61/claude-plugin-contributory-factors --exit-status
gh pr list --repo yo61/claude-plugin-contributory-factors --state open
```

Expected: one open PR titled approximately `chore(main): release 1.0.0`.

### Step 3.5 — Inspect the Release PR diff before merging

```bash
PR=$(gh pr list --repo yo61/claude-plugin-contributory-factors --state open --json number -q '.[0].number')
gh pr diff "$PR" --repo yo61/claude-plugin-contributory-factors
```

Expected diff:

- `.claude-plugin/plugin.json`: `"version": "1.0.0"` stays at 1.0.0 (already there; release-please re-asserts).
- `.release-please-manifest.json`: `{".":"1.0.0"}` (unchanged).
- New file: `CHANGELOG.md` with a release entry.

### Step 3.6 — Merge the Release PR (USER CONFIRMATION GATE)

**Stop and confirm with the user before running this step.**

```bash
gh pr merge "$PR" --repo yo61/claude-plugin-contributory-factors --merge
```

### Step 3.7 — Wait for the post-merge workflow run (creates tag + GH Release)

```bash
gh run watch --repo yo61/claude-plugin-contributory-factors --exit-status
gh release list --repo yo61/claude-plugin-contributory-factors
git fetch --tags
gh api repos/yo61/claude-plugin-contributory-factors/git/refs/tags/v1.0.0 --jq '.ref'
```

Expected: workflow succeeds; `gh release list` shows `v1.0.0`; the tag `v1.0.0` resolves.

### Step 3.8 — Test that `gh release-stats` returns data

```bash
gh release-stats --repo yo61/claude-plugin-contributory-factors 2>/dev/null || \
  gh api repos/yo61/claude-plugin-contributory-factors/releases --jq '.[].tag_name'
```

Expected: at minimum, `v1.0.0` appears.

---

## Task 4: Extract and scaffold `claude-plugin-reportlab-pdf`

**Pause and confirm with the user before Step 4.4 (creating the GitHub repo).**

This task is structurally identical to Task 2 but for the second plugin. All file contents are reproduced inline (DRY-of-the-plan is sacrificed for "the engineer might be reading tasks out of order").

**Files (in the extracted repo, after filter-repo):**
- Create: `LICENSE`
- Create: `.gitignore`
- Create: `.github/ISSUE_TEMPLATE/feature.md`
- Create: `.github/workflows/release.yml`
- Create: `.pre-commit-config.yaml`
- Create: `commitlint.config.mjs`
- Create: `release-please-config.json`
- Create: `.release-please-manifest.json`

### Step 4.1 — Clone the source repo into the extract directory

```bash
cd /tmp/polyrepo-extract
git clone /Users/robin/code/github/yo61/claude-skills claude-plugin-reportlab-pdf
cd claude-plugin-reportlab-pdf
```

### Step 4.2 — Run `git filter-repo` to extract just the plugin subdir

```bash
git filter-repo --subdirectory-filter plugins/reportlab-pdf --force
ls -la
git log --oneline | wc -l
```

Expected: working tree shows the plugin's files (`.claude-plugin/`, `README.md`, `skills/`) at the repo root. The bundled `md_to_pdf.py` should be at `skills/md-to-pdf/scripts/md_to_pdf.py`.

### Step 4.3 — Spot-check the extracted history

```bash
git log --oneline | head -20
```

Expected: commits relevant to `reportlab-pdf` (`Add reportlab-pdf plugin for PDF generation`, `Bundle md_to_pdf.py script with PEP 723 metadata`, `Allow custom renderer in md-to-pdf API`, etc.). No `contributory-factors` references.

### Step 4.4 — Create the GitHub repo (USER CONFIRMATION GATE)

**Stop and confirm with the user before running this step.**

```bash
gh repo create yo61/claude-plugin-reportlab-pdf \
  --public \
  --description "Claude Code plugin: ReportLab-based PDF generation. Programmatic Platypus PDFs (CVs, invoices, reports) and a markdown-to-PDF renderer (mistune + Platypus)."
```

### Step 4.5 — Add topics

```bash
gh repo edit yo61/claude-plugin-reportlab-pdf \
  --add-topic claude-code \
  --add-topic claude-code-plugin \
  --add-topic pdf-generation \
  --add-topic reportlab \
  --add-topic markdown
```

### Step 4.6 — Copy LICENSE

```bash
cp /Users/robin/code/github/yo61/claude-skills/LICENSE LICENSE
git add LICENSE
```

### Step 4.7 — Create `.gitignore`

Create `.gitignore`:

```
# macOS
.DS_Store

# Editors
.vscode/
.idea/

# Python
__pycache__/
*.py[cod]
*.egg-info/
.pytest_cache/
.ruff_cache/
.venv/

# Misc
*.log
*.tmp
```

### Step 4.8 — Copy issue template

```bash
mkdir -p .github/ISSUE_TEMPLATE
cp /Users/robin/code/github/yo61/claude-skills/.github/ISSUE_TEMPLATE/feature.md \
   .github/ISSUE_TEMPLATE/feature.md
```

### Step 4.9 — Create `commitlint.config.mjs`

Create `commitlint.config.mjs`:

```javascript
export default {
  extends: ['@commitlint/config-conventional'],
  rules: {
    // No scope-enum: this repo is a single package, so scope is decorative.
    // Subject case relaxation: allow identifiers like Palette or OpportunityQuery
    // to start a subject. Matches yo61/jobhound's commitlint config.
    'subject-case': [0],
  },
};
```

### Step 4.10 — Create `.pre-commit-config.yaml`

Substitute the `COMMITLINT_HOOK_TAG` from Step 2.10:

```yaml
repos:
  - repo: https://github.com/alessandrojcm/commitlint-pre-commit-hook
    rev: <COMMITLINT_HOOK_TAG>
    hooks:
      - id: commitlint
        stages: [commit-msg]
        additional_dependencies:
          - "@commitlint/config-conventional@^21"
```

### Step 4.11 — Create `release-please-config.json`

```json
{
  "$schema": "https://raw.githubusercontent.com/googleapis/release-please/main/schemas/config.json",
  "include-v-in-tag": true,
  "release-type": "simple",
  "packages": {
    ".": {
      "package-name": "reportlab-pdf",
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

### Step 4.12 — Create `.release-please-manifest.json` at current version

```json
{".":"1.2.0"}
```

### Step 4.13 — Create `.github/workflows/release.yml`

Substitute the `RP_SHA  # RP_TAG` from Step 1.6:

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
      - uses: googleapis/release-please-action@<RP_SHA>  # <RP_TAG>
        with:
          config-file: release-please-config.json
          manifest-file: .release-please-manifest.json
```

### Step 4.14 — Stage everything and commit

```bash
git add LICENSE .gitignore .github/ \
        .pre-commit-config.yaml commitlint.config.mjs \
        release-please-config.json .release-please-manifest.json
git commit -m "$(cat <<'EOF'
feat: add release-please scaffolding and supporting config

Adds LICENSE (MIT, from yo61/claude-skills), .gitignore, the feature/task
issue template, a release.yml workflow running release-please in simple
mode with SHA-pinned actions, commitlint config (no scope-enum since this
is a single-package repo), pre-commit config with commitlint on commit-msg,
release-please-config.json with extra-files updating .claude-plugin/plugin.json,
and the manifest pre-populated at 1.2.0.

Extracted from yo61/claude-skills@d6ad7e0 via:
  git filter-repo --subdirectory-filter plugins/reportlab-pdf

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

### Step 4.15 — Add the remote and push

```bash
git remote add origin git@github.com:yo61/claude-plugin-reportlab-pdf.git
git push -u origin main
```

### Step 4.16 — Verify the first workflow run completes

```bash
gh run watch --repo yo61/claude-plugin-reportlab-pdf --exit-status
```

Expected: workflow succeeds; no Release PR opens yet.

---

## Task 5: Bootstrap the first release for `claude-plugin-reportlab-pdf`

**Pause and confirm with the user before Step 5.6 (merging a release PR).**

### Step 5.1 — From the extracted clone, create a bootstrap branch

```bash
cd /tmp/polyrepo-extract/claude-plugin-reportlab-pdf
git checkout -b bootstrap-v1.2.0
```

### Step 5.2 — Create the bootstrap commit

```bash
git commit --allow-empty -m "$(cat <<'EOF'
chore: release 1.2.0

Release-As: 1.2.0

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

### Step 5.3 — Push, ff-merge to main locally, delete the bootstrap branch

```bash
git push -u origin bootstrap-v1.2.0
git checkout main
git merge --ff-only bootstrap-v1.2.0
git push origin main
git push origin --delete bootstrap-v1.2.0
git branch -d bootstrap-v1.2.0
```

### Step 5.4 — Wait for the workflow run to open the Release PR

```bash
gh run watch --repo yo61/claude-plugin-reportlab-pdf --exit-status
gh pr list --repo yo61/claude-plugin-reportlab-pdf --state open
```

Expected: one open PR titled approximately `chore(main): release 1.2.0`.

### Step 5.5 — Inspect the Release PR diff

```bash
PR=$(gh pr list --repo yo61/claude-plugin-reportlab-pdf --state open --json number -q '.[0].number')
gh pr diff "$PR" --repo yo61/claude-plugin-reportlab-pdf
```

Expected: `.claude-plugin/plugin.json` stays at 1.2.0; CHANGELOG.md created.

### Step 5.6 — Merge the Release PR (USER CONFIRMATION GATE)

**Stop and confirm with the user before running this step.**

```bash
gh pr merge "$PR" --repo yo61/claude-plugin-reportlab-pdf --merge
```

### Step 5.7 — Wait for the post-merge workflow + verify release

```bash
gh run watch --repo yo61/claude-plugin-reportlab-pdf --exit-status
gh release list --repo yo61/claude-plugin-reportlab-pdf
gh api repos/yo61/claude-plugin-reportlab-pdf/git/refs/tags/v1.2.0 --jq '.ref'
```

Expected: `v1.2.0` exists as both a tag and a GitHub Release.

---

## Task 6: Slim `claude-skills` to marketplace-only and add release-please

Working in `/Users/robin/code/github/yo61/claude-skills` on branch `add-release-automation`. No GitHub-state-affecting operations in this task — all local file edits + commits.

**Files:**
- Delete: `plugins/` (entire directory)
- Delete: `docs/superpowers/specs/2026-05-18-release-automation-design.md`
- Delete: `docs/superpowers/plans/2026-05-18-release-automation.md`
- Modify: `.claude-plugin/marketplace.json` (rewrite as github-source entries with tag pins)
- Modify: `README.md` (rewrite for marketplace-only role)
- Create: `.github/workflows/release.yml`
- Create: `.pre-commit-config.yaml`
- Create: `commitlint.config.mjs`
- Create: `release-please-config.json`
- Create: `.release-please-manifest.json`

### Step 6.1 — Switch to the working tree and confirm branch state

```bash
cd /Users/robin/code/github/yo61/claude-skills
git status
git branch --show-current
git log --oneline main..HEAD
```

Expected: clean tree on `add-release-automation` with two commits ahead of main.

### Step 6.2 — Delete the `plugins/` directory

```bash
git rm -r plugins/
git status
```

Expected: `git status` shows all files under `plugins/` as deleted.

### Step 6.3 — Delete the superseded spec and plan

```bash
git rm docs/superpowers/specs/2026-05-18-release-automation-design.md
git rm docs/superpowers/plans/2026-05-18-release-automation.md
```

### Step 6.4 — Rewrite `marketplace.json`

Replace the contents of `.claude-plugin/marketplace.json` with:

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

### Step 6.5 — Validate `marketplace.json` parses

```bash
python -m json.tool .claude-plugin/marketplace.json > /dev/null
```

Expected: exit 0, no output.

### Step 6.6 — Rewrite `README.md`

Replace the contents of `README.md` with:

```markdown
# yo61-skills

A Claude Code plugin marketplace published by [yo61](https://github.com/yo61).

## Plugins

| Plugin | Repo | Description |
|---|---|---|
| `contributory-factors` | [`yo61/claude-plugin-contributory-factors`](https://github.com/yo61/claude-plugin-contributory-factors) | Replaces "root cause" thinking with contributory factors analysis (London Protocol 2024, Yorkshire Contributory Factors Framework). |
| `reportlab-pdf` | [`yo61/claude-plugin-reportlab-pdf`](https://github.com/yo61/claude-plugin-reportlab-pdf) | ReportLab-based PDF generation. Programmatic Platypus PDFs (CVs, invoices, reports) and a markdown-to-PDF renderer (mistune + Platypus). |

## Use

In Claude Code:

```
/plugin marketplace add yo61/claude-skills
/plugin install contributory-factors
/plugin install reportlab-pdf
```

Refresh your local copy of the marketplace after a new release with:

```
/plugin marketplace update
```

## Versioning

This is a [release-please](https://github.com/googleapis/release-please)-managed marketplace. Each entry in `marketplace.json` pins to an exact release tag of its plugin repo. When a plugin cuts a new release, this marketplace bumps its `ref` and cuts its own release.

## License

MIT — see [LICENSE](LICENSE).
```

(Note: the inner ` ``` ` fences inside the README need to be preserved exactly as shown — they're code blocks for users to copy.)

### Step 6.7 — Create `commitlint.config.mjs`

Create `commitlint.config.mjs`:

```javascript
export default {
  extends: ['@commitlint/config-conventional'],
  rules: {
    // No scope-enum: this repo is a single package (the marketplace), so scope is decorative.
    'subject-case': [0],
  },
};
```

### Step 6.8 — Create `.pre-commit-config.yaml`

Substitute the `COMMITLINT_HOOK_TAG` from Step 2.10:

```yaml
repos:
  - repo: https://github.com/alessandrojcm/commitlint-pre-commit-hook
    rev: <COMMITLINT_HOOK_TAG>
    hooks:
      - id: commitlint
        stages: [commit-msg]
        additional_dependencies:
          - "@commitlint/config-conventional@^21"
```

### Step 6.9 — Create `release-please-config.json`

Create `release-please-config.json` (note: `extra-files` updates `marketplace.json`'s `$.version`, not `plugin.json`):

```json
{
  "$schema": "https://raw.githubusercontent.com/googleapis/release-please/main/schemas/config.json",
  "include-v-in-tag": true,
  "release-type": "simple",
  "packages": {
    ".": {
      "package-name": "yo61-skills-marketplace",
      "changelog-path": "CHANGELOG.md",
      "extra-files": [
        {
          "type": "json",
          "path": ".claude-plugin/marketplace.json",
          "jsonpath": "$.version"
        }
      ]
    }
  }
}
```

### Step 6.10 — Create `.release-please-manifest.json` at 0.1.0

Create `.release-please-manifest.json`:

```json
{".":"0.1.0"}
```

### Step 6.11 — Create `.github/workflows/release.yml`

Substitute the `RP_SHA  # RP_TAG` from Step 1.6:

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
      - uses: googleapis/release-please-action@<RP_SHA>  # <RP_TAG>
        with:
          config-file: release-please-config.json
          manifest-file: .release-please-manifest.json
```

### Step 6.12 — Install pre-commit hooks locally

```bash
pre-commit install --install-hooks
pre-commit install --hook-type commit-msg
```

Expected: messages confirming installation.

### Step 6.13 — Stage and review

```bash
git add .github/workflows/release.yml \
        .pre-commit-config.yaml commitlint.config.mjs \
        release-please-config.json .release-please-manifest.json \
        .claude-plugin/marketplace.json README.md
git status
```

Expected: 5 new files staged, 2 modified, plugins/* and old spec/plan files staged for deletion.

### Step 6.14 — Commit

```bash
git commit -m "$(cat <<'EOF'
feat: slim claude-skills to marketplace-only with release-please

- Delete the plugins/ directory; each plugin now lives in its own repo
  (yo61/claude-plugin-contributory-factors at v1.0.0, yo61/claude-plugin-reportlab-pdf
  at v1.2.0).
- Delete the superseded monorepo design spec and plan
  (docs/superpowers/{specs,plans}/2026-05-18-release-automation*).
- Rewrite marketplace.json to use github source entries with exact-tag pins
  and a top-level version field managed by release-please.
- Rewrite README.md for the marketplace-only role.
- Add release-please scaffolding: simple mode, manifest at 0.1.0, extra-files
  updating marketplace.json $.version, SHA-pinned release-please-action.
- Add commitlint config (no scope-enum; single-package) and a minimal
  pre-commit config with commitlint on commit-msg.

Refs: #7

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

### Step 6.15 — Final inspection before ff-merge

```bash
git log --oneline main..HEAD
git diff --stat main..HEAD
find . -name 'plugins' -type d 2>/dev/null
ls docs/superpowers/specs/ docs/superpowers/plans/
```

Expected:
- 3 commits ahead of main (issue template, polyrepo spec, this commit).
- No `plugins/` directory remains.
- `docs/superpowers/specs/` contains only `2026-05-07-md-to-pdf-skill-design.md` and `2026-05-18-polyrepo-migration-design.md`.
- `docs/superpowers/plans/` contains only `2026-05-07-md-to-pdf-skill.md` and `2026-05-18-polyrepo-migration.md` (this file).

---

## Task 7: ff-merge to main and watch the marketplace's first workflow run

**Pause and confirm with the user before Step 7.3 (pushing to main on the shared repo).**

### Step 7.1 — Switch to main and confirm sync with origin

```bash
cd /Users/robin/code/github/yo61/claude-skills
git fetch origin
git checkout main
git log --oneline main..origin/main
```

Expected: empty output (local main matches origin/main).

### Step 7.2 — Fast-forward merge `add-release-automation`

```bash
git merge --ff-only add-release-automation
git log --oneline -5
```

Expected: "Fast-forward" line; HEAD advances by 3 commits.

### Step 7.3 — Push to main (USER CONFIRMATION GATE)

**Stop and confirm with the user before running this step.**

```bash
git push origin main
```

### Step 7.4 — Delete the feature branch locally and on remote (if it was pushed)

```bash
git branch -d add-release-automation
git push origin --delete add-release-automation 2>/dev/null || echo "branch not on remote, skipping"
```

### Step 7.5 — Watch the first marketplace workflow run

```bash
gh run watch --exit-status
```

Expected: workflow succeeds; release-please runs but does NOT open a PR (no qualifying conventional commits since manifest was initialised at 0.1.0).

---

## Task 8: Bootstrap the marketplace's first release at v0.1.0

**Pause and confirm with the user before Step 8.6 (merging a release PR).**

### Step 8.1 — Create a short-lived bootstrap branch

```bash
cd /Users/robin/code/github/yo61/claude-skills
git checkout -b bootstrap-v0.1.0 main
```

### Step 8.2 — Create the bootstrap commit

```bash
git commit --allow-empty -m "$(cat <<'EOF'
chore: release 0.1.0

Release-As: 0.1.0

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

### Step 8.3 — ff-merge to main, push, delete bootstrap branch

```bash
git checkout main
git merge --ff-only bootstrap-v0.1.0
git push origin main
git branch -d bootstrap-v0.1.0
```

### Step 8.4 — Watch the workflow open the Release PR

```bash
gh run watch --exit-status
gh pr list --state open
```

Expected: one open PR titled approximately `chore(main): release 0.1.0`.

### Step 8.5 — Inspect the Release PR diff

```bash
PR=$(gh pr list --state open --json number -q '.[0].number')
gh pr diff "$PR"
```

Expected: `marketplace.json` `version: "0.1.0"` (unchanged); manifest at 0.1.0; new `CHANGELOG.md`.

### Step 8.6 — Merge the Release PR (USER CONFIRMATION GATE)

**Stop and confirm with the user before running this step.**

```bash
gh pr merge "$PR" --merge
```

### Step 8.7 — Watch the post-merge workflow + verify release

```bash
gh run watch --exit-status
gh release list
git fetch --tags
git tag --list | grep -E '^v0\.1\.0$'
```

Expected: `v0.1.0` exists as tag + GitHub Release.

---

## Task 9: End-to-end verification

### Step 9.1 — Verify all three repos have their first releases

```bash
echo "=== contributory-factors ==="
gh release list --repo yo61/claude-plugin-contributory-factors

echo "=== reportlab-pdf ==="
gh release list --repo yo61/claude-plugin-reportlab-pdf

echo "=== claude-skills (marketplace) ==="
gh release list
```

Expected: each shows at least one release (`v1.0.0`, `v1.2.0`, `v0.1.0` respectively).

### Step 9.2 — Verify the marketplace.json on `main` has the correct pins

```bash
gh api repos/yo61/claude-skills/contents/.claude-plugin/marketplace.json --jq '.content' | base64 -d | jq '.plugins[] | {name, ref: .source.ref}'
```

Expected output:

```json
{
  "name": "contributory-factors",
  "ref": "v1.0.0"
}
{
  "name": "reportlab-pdf",
  "ref": "v1.2.0"
}
```

### Step 9.3 — Verify each plugin resolves at its pinned tag (raw fetch)

```bash
gh api repos/yo61/claude-plugin-contributory-factors/contents/.claude-plugin/plugin.json --jq '.content' | base64 -d | jq '.name, .version'
gh api repos/yo61/claude-plugin-reportlab-pdf/contents/.claude-plugin/plugin.json --jq '.content' | base64 -d | jq '.name, .version'
```

Expected:

```
"contributory-factors"
"1.0.0"
"reportlab-pdf"
"1.2.0"
```

### Step 9.4 — Verify `gh release-stats` returns non-empty results per plugin

```bash
gh release-stats --repo yo61/claude-plugin-contributory-factors 2>/dev/null
gh release-stats --repo yo61/claude-plugin-reportlab-pdf 2>/dev/null
gh release-stats --repo yo61/claude-skills 2>/dev/null
```

Expected: each invocation prints release data (download counts may be zero but the releases themselves are listed). This is the original trigger condition for this whole project being satisfied.

### Step 9.5 — Manual install test in a Claude Code session

Open a fresh Claude Code session and run:

```
/plugin marketplace remove yo61/claude-skills
/plugin marketplace add yo61/claude-skills
/plugin install contributory-factors
/plugin install reportlab-pdf
```

Expected: both plugins install successfully from their new GitHub source pins. (This step cannot be fully scripted; the executor performs it manually and reports back.)

---

## Task 10: Close issue #7 and clean up

### Step 10.1 — Close the tracking issue

```bash
gh issue close 7 --comment "Done.
- yo61/claude-plugin-contributory-factors at v1.0.0 — first release published.
- yo61/claude-plugin-reportlab-pdf at v1.2.0 — first release published.
- yo61/claude-skills at v0.1.0 — slimmed to marketplace-only; plugins/ removed; superseded specs/plans deleted.
- End-to-end install verified.

Follow-ups (per-repo CI, tarball assets, App token / branch protection, marketplace auto-update) will be filed in the relevant repos when needed."
```

### Step 10.2 — Clean up local extract directory

```bash
rm -rf /tmp/polyrepo-extract
```

### Step 10.3 — Update the per-conversation memory for the marketplace move

This step is for the controller (not a subagent). Update the relevant auto-memory entries to reflect:

- The two new plugin repo names (`yo61/claude-plugin-contributory-factors`, `yo61/claude-plugin-reportlab-pdf`).
- That `yo61/claude-skills` is now marketplace-only.
- That release pipelines exist on all three repos.

(The auto-memory mechanism handles this via the controller's own context, not subagent dispatch.)

---

## Self-review

Spec coverage check — every Decision (D1–D11) in `2026-05-18-polyrepo-migration-design.md` is covered:

- D1 (three-repo topology) → Tasks 2, 4, 6
- D2 (git filter-repo history preservation) → Steps 2.2, 4.2 + Task 1.2 (install)
- D3 (release-please simple mode per plugin) → Steps 2.11, 4.11
- D4 (marketplace runs release-please at v0.1.0) → Steps 6.9, 6.10, Task 8
- D5 (exact-tag pinning; manual bumps) → Step 6.4 (marketplace.json with ref: v1.0.0 / v1.2.0)
- D6 (marketplace entry fields: name, source, category, tags, description) → Step 6.4
- D7 (Conventional Commits per repo; no scope-enum) → Steps 2.9, 4.9, 6.7
- D8 (SHA-pinned actions with version comments) → Step 1.6 lookup + Steps 2.13, 4.13, 6.11
- D9 (default GITHUB_TOKEN; no App token) → Steps 2.13, 4.13, 6.11 (no `actions/create-github-app-token` anywhere)
- D10 (minimal pre-commit; just commitlint) → Steps 2.10, 4.10, 6.8
- D11 (delete superseded spec + plan in marketplace cleanup) → Step 6.3

Placeholder scan: no `TBD`, `TODO`, or "fill in details" remain. The substitutable parameters (`<RP_SHA>`, `<RP_TAG>`, `<COMMITLINT_HOOK_TAG>`) are resolved at known steps (1.6 and 2.10) with exact commands.

Type/name consistency:
- `package-name` differs per repo (`contributory-factors`, `reportlab-pdf`, `yo61-skills-marketplace`) — intentional.
- `extra-files.path` differs (`.claude-plugin/plugin.json` in plugin repos; `.claude-plugin/marketplace.json` in marketplace) — intentional, matches D4.
- `.release-please-manifest.json` content differs per repo (`1.0.0`, `1.2.0`, `0.1.0`) — matches D2 + D4.
- All workflow files use the same SHA-pinned `release-please-action` — consistent.

Open verification deferred to execution time (mirrors the spec's Open Questions):

- Exact release-please-action output shape at the pinned SHA — only matters if we later add a follow-up job; the plan's workflows have a single step, so this isn't blocking.
- `extra-files` JSON updater behaviour on `plugin.json` and `marketplace.json`. Each Release PR's diff inspection step (3.5, 5.5, 8.5) catches any failure before merge.

Sequencing: plugin repos are released **before** the marketplace pins to them. Marketplace cleanup happens on the same branch as the spec and plan (the existing `add-release-automation` branch), so the ff-merge in Task 7 lands all three commits at once.
