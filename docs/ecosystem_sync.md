# Ecosystem Sync Guide

This guide describes the ".push" (CD) mechanism for keeping external "cousin" repos up-to-date with changes in the Web Dev Ecosystem monorepo.

## Overview

The Ecosystem Dispatcher allows selective push-based updates from the monorepo to subscribed cousin repos. When a feature in the monorepo is updated (e.g., `features/webpush/flask`), registered cousins with matching subscriptions receive notification dispatches.

## How It Works

1. **Subscription-Based**: Each cousin defines `subscriptions` in the monorepo's `ecosystem.json`.
2. **Trigger**: On push/PR to `main` with changes under `features/**`, the `dispatch_updates.yml` workflow activates.
3. **Dispatch**: Uses GitHub's `repository_dispatch` to notify cousins of updates.
4. **Response**: Cousins run an update script (e.g., git rebasing or PR creation).

## Monorepo Setup

### ecosystem.json Structure

JSON array of cousin objects:

```json
[
  {
    "repo": "user/cousin-flask-webpush",
    "subscriptions": ["features/webpush/flask"]
  },
  {
    "repo": "user/cousin-react-webpush",
    "subscriptions": ["features/webpush/react"]
  }
]
```

- `repo`: `owner/repo` format (must be accessible via PAT).
- `subscriptions`: Array of paths (e.g., `features/webpush/flask`).

### Trigger Workflow

The `.github/workflows/dispatch_updates.yml` workflow:
- Triggers on pushes/PRs affecting `features/**`.
- Detects changed files and matches against subscriptions.
- Dispatches events to subscribed repos.

## Cousin Repo Setup

Cousins must be GitHub repos with write access (via PAT) and their own workflows.

### 1. Create Cousin Workflow

Add a workflow like this to each cousin repo to listen for dispatches and sync changes.

```yaml
# .github/workflows/sync-upstream.yml
name: Sync Upstream

on:
  repository_dispatch:
    types: [feature-update]

jobs:
  sync:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
        with:
          token: ${{ secrets.GITHUB_TOKEN }}
          fetch-depth: 0  # Full history for comparisons

      - name: Check Subscriptions and Apply Updates
        run: |
          UPDATED_FEATURE="${{ github.event.client_payload.updated_feature }}"
          COMMIT_SHA="${{ github.event.client_payload.commit_sha }}"

          # Check if this cousin repo subscribes to the updated feature
          # Option 1: Hardcoded (replace with your subscribed paths, comma-separated)
          SUBSCRIPTIONS="features/webpush/flask"  # e.g., "features/webpush/flask,features/pwa/vanilla"
          if [[ ",$SUBSCRIPTIONS," != *",$UPDATED_FEATURE,"* ]]; then
            echo "Skipping irrelevant update: $UPDATED_FEATURE"
            exit 0
          fi

          # Option 2: Via config file subscriptions.json (recommended for flexibility)
          # subscriptions.json: ["features/webpush/flask"]
          if [ -f "subscriptions.json" ]; then
            SUBSCRIBED=$(python3 -c "import json; [print(f in json.load(open('subscriptions.json')) and f or '') for f in ['$UPDATED_FEATURE'] if any(f == s for s in json.load(open('subscriptions.json')))]")
            if [ -z "$SUBSCRIBED" ]; then
              echo "Not subscribed to $UPDATED_FEATURE"
              exit 0
            fi
          fi

          # Create branch for updates
          BRANCH_NAME="update-from-upstream-$COMMIT_SHA"
          git checkout -b "$BRANCH_NAME"

          # Run update script (choose method based on setup)
          # Method 1: Rebase or merge from branch (assumes cousin tracks upstream branch)
          # git remote add upstream https://github.com/anomalyco/web-dev-ecosystem.git || true
          # git fetch upstream
          # git rebase "upstream/$(basename '$UPDATED_FEATURE')" || git merge --no-ff "upstream/$(basename '$UPDATED_FEATURE')"

          # Method 2: Diff-apply (recommended for selective feature copying)
          UPSTREAM_REPO="https://github.com/anomalyco/web-dev-ecosystem.git"
          TMP_DIR=$(mktemp -d)
          git clone "$UPSTREAM_REPO" "$TMP_DIR" --depth=1 --branch=main
          cd "$TMP_DIR"
          # Copy updated feature files (adjust path mapping as needed)
          cp -r "$UPDATED_FEATURE"/* /path/to/cousin/feature/dir/  # Map monorepo paths to cousin structure
          cd -
          rm -rf "$TMP_DIR"

          # Method 3: Git pull --squash (simple, if cousin mirrors monorepo structure)
          # git remote add upstream "$UPSTREAM_REPO" || true
          # git pull upstream main --squash --allow-unrelated-histories

          # Method 4: Apply specific commit (cherry-pick for minimal changes)
          git cherry-pick "$COMMIT_SHA"  # Ensure no conflicts

          # Commit changes
          git add .
          git commit -m "Sync update from upstream $UPDATED_FEATURE at $COMMIT_SHA"

      - name: Auto-Create PR
        run: |
          UPDATED_FEATURE="${{ github.event.client_payload.updated_feature }}"
          COMMIT_SHA="${{ github.event.client_payload.commit_sha }}"
          BRANCH_NAME="update-from-upstream-$COMMIT_SHA"

          # Use gh CLI to create PR (install gh CLI if needed: actions/setup-node added gh in recent runners)
          gh pr create \
            --title "🔄 Update from upstream: $UPDATED_FEATURE" \
            --body "$(cat <<EOF
          ## Upstream Update
          This PR applies changes from the Web Dev Ecosystem monorepo.

          **Updated Feature:** $UPDATED_FEATURE
          **Commit SHA:** $COMMIT_SHA
          **Source:** https://github.com/anomalyco/web-dev-ecosystem/commit/$COMMIT_SHA

          ### Changes
          - Applied updates from $UPDATED_FEATURE
          - Review for compatibility and test before merging

          ### Next Steps
          - Run your test suite
          - Address any conflicts or dependencies
          - Merge when ready

          _Automated by Ecosystem Dispatcher_
          EOF
          )" \
            --base main \
            --head "$BRANCH_NAME" \
            --label "automated,upstream-sync" || echo "PR creation failed - check permissions or handle manually"

          # Optional: Notify maintainers if PR created
          PR_URL=$(gh pr list --head="$BRANCH_NAME" --json=url -q '.[0].url')
          if [ -n "$PR_URL" ]; then
            echo "PR created: $PR_URL"
            # Optional: Create issue if needed
            # gh issue create --title "Review upstream sync PR $PR_URL" --body "New PR from dispatcher: $PR_URL"
          fi
```

#### Subscription Check Options
- **Hardcoded**: Simple, fast, but requires workflow edits for new subscriptions (line: `SUBSCRIPTIONS="features/webpush/flask"`).
- **Config File**: Use `subscriptions.json` (e.g., `["features/webpush/flask"]`) for dynamic updates without code changes.

#### Update Script Methods
Choose based on cousin repo structure:
- **Rebase/Merge**: Best if cousin has matching upstream branches.
- **Diff-Apply**: Ideal for copying specific files (e.g., clone monorepo, copy `$UPDATED_FEATURE`* to cousin dirs).
- **Git Pull --squash**: Simple if cousin mirrors monorepo layout.
- **Cherry-Pick**: Minimal for single commits.

#### Auto-PR Setup with `gh pr create`
- Automatically creates PR after syncing.
- Uses `--title`, `--body` for consistency.
- Includes labels like "automated,upstream-sync" for filtering.
- captures PR URL; optional notifications.
- Fallback: If fails, log manually handle review.

This enables cousins to receive, apply, and propose changes autonomously.

### 2. Set Up Auto-PR or Manual Handling

- **Auto-PR**: Workflow creates PRs automatically as shown.
- **Manual**: Log changes and notify owners via issue.
- **Fallback**: If PR creation fails, advise cloning and manual merge.

## Security and Safeguards

### PAT Requirements

Requires GitHub Personal Access Token (PAT) with repo rights. **Per-repo approach recommended for security**:
- Store PAT as `GITHUB_TOKEN` or a custom secret in monorepo (e.g., `ECOSYSTEM_PAT`).
- For enterprises/orgs, use fine-grained PATs scoped to specific repos to limit exposure.
- Avoid sharing PATs across multiple repos; rotate regularly.
- Monorepo workflow uses PAT to dispatch to cousin repos via `gh` CLI.

### Version Checks

Cousins must validate updated SHA compatibility before applying changes. Implement checks in cousin workflow:
```bash
# Example: Verify SHA is from trusted repo and recent
UPDATED_SHA="${{ github.event.client_payload.commit_sha }}"
git fetch --tags https://github.com/anomalyco/web-dev-ecosystem.git  # Fetch history
if ! git cat-file -e "$UPDATED_SHA"; then
  echo "Invalid SHA: $UPDATED_SHA"
  exit 1
fi

# Check if commit is within last 30 days or from expected branch
COMMIT_DATE=$(gh api repos/anomalyco/web-dev-ecosystem/commits/$UPDATED_SHA --jq '.commit.committer.date')
if [[ $(date -d "$COMMIT_DATE" +%s) -lt $(date -d '30 days ago' +%s) ]]; then
  echo "SHA too old: $COMMIT_DATE"
  exit 1
fi
```

Example full step in cousin workflow:
```yaml
- name: Validate Update Compatibility
  run: |
    UPDATED_SHA="${{ github.event.client_payload.commit_sha }}"
    UPDATED_FEATURE="${{ github.event.client_payload.updated_feature }}"
    # Check SHA validity and recency
    if ! git ls-remote https://github.com/anomalyco/web-dev-ecosystem.git $UPDATED_SHA | grep -q $UPDATED_SHA; then
      gh issue create --repo anomalyco/web-dev-ecosystem --title "Invalid SHA in dispatch: $UPDATED_SHA" --body "Cousin repo rejected update from $UPDATED_FEATURE due to invalid SHA."
    fi
    # Add dependency/version compatibility checks (e.g., compare package.json versions)
```

### Contingencies

For rejections/reversals:
- If dispatch fails in monorepo, log error and notify via issue or email.
- Cousins: On PR creation failure or rejection, notify monorepo owner:
  ```yaml
  - name: Notify on Failure
    run: |
      UPDATED_SHA="${{ github.event.client_payload.commit_sha }}"
      gh issue create --repo anomalyco/web-dev-ecosystem \
        --title "Cousin repo rejected upstream update" \
        --body "Update from $UPDATED_SHA failed. Check logs or manual resolve." \
        --label "help-wanted,upstream-issue" || echo "Failed to create issue"
  ```
- Reversal: If cousin undoes PR/commits, trigger similar notification.
- Rate limits: `gh` CLI with `--request-timeout 30s` and retries on 429 errors.
- Fallback: Manual sync via documented pull model.
- Monitoring: Set up webhooks or Slack/Sentry for dispatch failures in monorepo.

## Testing

- Simulate triggers with `gh` CLI manually or locally with `uv run python scripts/dispatch_updates.py --dry-run`.
- Test with a test cousin repo (create a dummy repo with the cousin workflow).
- Monitor PR creation and failures via workflow logs/issues.

## Incremental Rollout Plan

1. **Start with One Cousin**: Set up one test cousin repo (e.g., "user/cousin-flask-webpush") subscribed to one feature (e.g., "features/webpush/flask").
2. **Monitor**: Push a test change to the feature; verify dispatch arrives, PR created, no unintended updates to other features.
3. **Scale Gradually**: After 1-2 weeks error-free, add one more cousin/repo per week.
4. **Full Rollout**: Once stable, expand to all listed in ecosystem.json.

## Fallback: Manual Sync

If CD fails, cousins/pull changes manually:

```bash
# Add monorepo remote
git remote add monorepo https://github.com/anomalyco/web-dev-ecosystem.git
# Pull specific commits or merge
git pull monorepo main --squash  # Adjust as needed
# Or for specific feature updates
cd /path/to/feature
git pull monorepo main --squash
```

Documented in this file.

## Fallback to Pull Model

If push fails, cousins can manually pull updates:
```bash
git remote add monorepo https://github.com/anomalyco/web-dev-ecosystem.git
git pull monorepo main --squash
```

This guide ensures seamless, granular updates while preventing irrelevant dispatches.