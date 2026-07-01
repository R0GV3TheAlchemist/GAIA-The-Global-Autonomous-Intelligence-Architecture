# Branch Protection Rules — GAIA OS

This document is the authoritative reference for the branch protection
configuration on this repository. Apply these rules via
**Settings → Branches → Add rule** or via the GitHub CLI commands below.

---

## Protected branches

### `main`

| Setting | Value |
|---|---|
| Require a pull request before merging | ✅ |
| Required approving reviews | 1 |
| Dismiss stale reviews on new push | ✅ |
| Require status checks to pass before merging | ✅ |
| Require branches to be up to date before merging | ✅ |
| Require conversation resolution before merging | ✅ |
| Do not allow bypassing the above settings | ✅ |
| Allow force pushes | ❌ |
| Allow deletions | ❌ |

#### Required status checks (exact names)

These are the GitHub Actions job names that must pass before any PR
can merge into `main`. The string must match the job name exactly
as it appears in the Actions UI.

```
CI / Python 3.11 tests
CI / Python 3.12 tests
CI / Docker build validation
Container smoke test / Container smoke test
CodeQL / CodeQL
```

---

### `develop`

| Setting | Value |
|---|---|
| Require a pull request before merging | ✅ |
| Required approving reviews | 1 |
| Dismiss stale reviews on new push | ✅ |
| Require status checks to pass before merging | ✅ |
| Require branches to be up to date before merging | ✅ |
| Require conversation resolution before merging | ✅ |
| Allow force pushes | ❌ |
| Allow deletions | ❌ |

#### Required status checks

```
CI / Python 3.11 tests
CI / Python 3.12 tests
CI / Docker build validation
Container smoke test / Container smoke test
```

(CodeQL is not required on `develop` — it runs but is advisory.)

---

## Apply via GitHub CLI

Install the GitHub CLI (`gh`) and run from the repo root.
You must be authenticated as a repository admin.

### `main`

```bash
gh api \
  --method PUT \
  -H "Accept: application/vnd.github+json" \
  /repos/R0GV3TheAlchemist/GAIA-The-Global-Autonomous-Intelligence-Architecture/branches/main/protection \
  --input - <<'EOF'
{
  "required_status_checks": {
    "strict": true,
    "contexts": [
      "CI / Python 3.11 tests",
      "CI / Python 3.12 tests",
      "CI / Docker build validation",
      "Container smoke test / Container smoke test",
      "CodeQL / CodeQL"
    ]
  },
  "enforce_admins": true,
  "required_pull_request_reviews": {
    "dismiss_stale_reviews": true,
    "require_code_owner_reviews": false,
    "required_approving_review_count": 1
  },
  "restrictions": null,
  "required_conversation_resolution": true,
  "allow_force_pushes": false,
  "allow_deletions": false
}
EOF
```

### `develop`

```bash
gh api \
  --method PUT \
  -H "Accept: application/vnd.github+json" \
  /repos/R0GV3TheAlchemist/GAIA-The-Global-Autonomous-Intelligence-Architecture/branches/develop/protection \
  --input - <<'EOF'
{
  "required_status_checks": {
    "strict": true,
    "contexts": [
      "CI / Python 3.11 tests",
      "CI / Python 3.12 tests",
      "CI / Docker build validation",
      "Container smoke test / Container smoke test"
    ]
  },
  "enforce_admins": false,
  "required_pull_request_reviews": {
    "dismiss_stale_reviews": true,
    "require_code_owner_reviews": false,
    "required_approving_review_count": 1
  },
  "restrictions": null,
  "required_conversation_resolution": true,
  "allow_force_pushes": false,
  "allow_deletions": false
}
EOF
```

---

## Status check name reference

Each required check name is `"<workflow name> / <job name>"` as
displayed in the GitHub Actions UI.

| Check name | Workflow file | Job id |
|---|---|---|
| `CI / Python 3.11 tests` | `ci.yml` | `test` (matrix: 3.11) |
| `CI / Python 3.12 tests` | `ci.yml` | `test` (matrix: 3.12) |
| `CI / Docker build validation` | `ci.yml` | `docker-build` |
| `Container smoke test / Container smoke test` | `smoke-test.yml` | `smoke` |
| `CodeQL / CodeQL` | `security.yml` | `codeql` |

> **Note:** Status check names only appear in the branch protection
> settings dropdown *after the workflow has run at least once* on the
> target branch. If you're adding protection before the first run,
> type the name manually exactly as shown above.
