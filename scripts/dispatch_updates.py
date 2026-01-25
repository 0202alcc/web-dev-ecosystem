#!/usr/bin/env uv run python
import json
import subprocess
import os
import sys


def get_changed_features(previous_commit):
    """Get set of changed feature paths from git diff."""
    try:
        cmd = ["git", "diff", "--name-only", previous_commit, "HEAD"]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        changed_files = result.stdout.strip().split("\n")

        # Filter for features/ paths and extract unique feature dirs (e.g., features/webpush/flask)
        changed_features = set()
        for file in changed_files:
            if file.startswith("features/"):
                parts = file.split("/")
                if len(parts) >= 3:
                    changed_features.add("/".join(parts[:3]))

        return changed_features
    except subprocess.CalledProcessError:
        print("Failed to get git diff")
        return set()


def get_subscribed_repos(feature_path):
    """Get list of repos subscribed to the given feature path."""
    if not os.path.exists("ecosystem.json"):
        print("ecosystem.json not found")
        return []

    try:
        with open("ecosystem.json", "r") as f:
            ecosystem = json.load(f)

        repos = []
        for entry in ecosystem:
            if "subscriptions" in entry and feature_path in entry["subscriptions"]:
                repos.append(entry["repo"])
        return repos
    except (json.JSONDecodeError, KeyError) as e:
        print(f"Error reading ecosystem.json: {e}")
        return []


def dispatch_to_repo(repo, feature_path, commit_sha, dry_run=False):
    """Send repository_dispatch event to a repo using gh CLI."""
    payload = {"updated_feature": feature_path, "commit_sha": commit_sha}

    cmd = [
        "gh",
        "api",
        f"repos/{repo}/dispatches",
        "-X",
        "POST",
        "-H",
        "Accept: application/vnd.github+json",
        "-f",
        f"event_type=feature-update",
        "-f",
        f"client_payload={json.dumps(payload)}",
    ]

    if dry_run:
        print(
            f"DRY RUN: Would dispatch to {repo} for {feature_path} with payload {json.dumps(payload)}"
        )
        return True

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        print(f"✅ Dispatched to {repo} for {feature_path}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to dispatch to {repo}: {e.stderr}")
        return False


def main():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--dry-run", action="store_true", help="Simulate dispatches without sending"
    )
    args = parser.parse_args()

    # Get previous commit (for diff)
    commit_cmd = ["git", "rev-parse", "HEAD~1"]
    try:
        result = subprocess.run(commit_cmd, capture_output=True, text=True, check=True)
        previous_commit = result.stdout.strip()
    except subprocess.CalledProcessError:
        previous_commit = "HEAD~1"  # Fallback

    # Get commit SHA
    sha_cmd = ["git", "rev-parse", "HEAD"]
    commit_sha = subprocess.run(
        sha_cmd, capture_output=True, text=True, check=True
    ).stdout.strip()

    # Find changed features
    changed_features = get_changed_features(previous_commit)
    if not changed_features:
        print("No feature directories changed, skipping dispatch")
        return

    print(f"Changed features: {', '.join(changed_features)}")

    # Collect unique repos to dispatch to
    repos_to_dispatch = set()
    for feature in changed_features:
        repos = get_subscribed_repos(feature)
        repos_to_dispatch.update(repos)

    # Dispatch to each repo
    for repo in sorted(repos_to_dispatch):
        success = True
        for feature in changed_features:
            if dispatch_to_repo(repo, feature, commit_sha, dry_run=args.dry_run):
                continue
            else:
                success = False
        if not success:
            print(f"Some dispatches failed for {repo}")


if __name__ == "__main__":
    main()
