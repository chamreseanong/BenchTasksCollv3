#!/usr/bin/env python3
import json
import os
import shutil
import subprocess


def run(cmd, check=True):
    print("+", " ".join(cmd))
    return subprocess.run(cmd, check=check)


def main():
    run(["git", "fetch", "--all", "--prune"])
    with open("tasks/finalpool_manifest.json", encoding="utf-8") as f:
        tasks = json.load(f)

    os.makedirs("tasks/finalpool", exist_ok=True)
    missing = []
    for entry in tasks:
        src = f"tasks/{entry['dev']}/{entry['task']}"
        branch = entry["branch"]
        if subprocess.run(["git", "cat-file", "-e", f"{branch}:{src}"]).returncode != 0:
            missing.append((branch, src))
            continue
        shutil.rmtree(src, ignore_errors=True)
        run(["git", "checkout", branch, "--", src])
        dest = f"tasks/finalpool/{entry['task']}"
        shutil.rmtree(dest, ignore_errors=True)
        shutil.move(src, dest)

    if missing:
        print("MISSING TASKS:")
        for item in missing:
            print(item)

    run(["git", "add", "tasks/finalpool"], check=False)
    run(["git", "rm", "-f", "tasks/finalpool_manifest.json", "scripts/build_finalpool.py", ".github/workflows/finalpool.yml"], check=False)

    status = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True)
    if not status.stdout.strip():
        print("No changes to commit.")
        return

    run(["git", "config", "user.name", "github-actions[bot]"])
    run(["git", "config", "user.email", "github-actions[bot]@users.noreply.github.com"])
    run(["git", "commit", "-m", "Add implemented tasks to tasks/finalpool"])
    token = os.environ.get("GITHUB_TOKEN")
    repo = os.environ.get("GITHUB_REPOSITORY")
    remote = f"https://x-access-token:{token}@github.com/{repo}.git"
    run(["git", "push", remote, "finalpool"])


if __name__ == "__main__":
    main()
