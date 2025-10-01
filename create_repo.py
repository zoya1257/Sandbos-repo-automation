#!/usr/bin/env python3
"""
create_repo.py
Usage (from workflow):
  python create_repo.py <volunteer-github-username> [--org ORG_NAME]

This script will:
 - read token from env var GITHUB_TOKEN or GH_TOKEN
 - create repo libelle-sandbox-<volunteer> under your user or org
 - add README.md and add collaborator
"""

import sys
import os
import argparse
from github import Github, GithubException

def main():
    parser = argparse.ArgumentParser(description="Create sandbox repo for volunteer")
    parser.add_argument("volunteer", help="Volunteer GitHub username (e.g. zoya1257)")
    parser.add_argument("--org", help="Organization name (optional). If not set, use the authenticated user", default=None)
    args = parser.parse_args()

    volunteer = args.volunteer.strip()
    if not volunteer:
        print("ERROR: volunteer username empty", file=sys.stderr)
        return 2

    # Accept token from either GITHUB_TOKEN (preferred) or GH_TOKEN (legacy)
    token = os.getenv("GITHUB_TOKEN") or os.getenv("GH_TOKEN")
    if not token:
        print("ERROR: No GitHub token found in env. Please set GH_TOKEN secret and map it to GITHUB_TOKEN in workflow.", file=sys.stderr)
        return 2

    g = Github(token)

    # Choose owner: org or authenticated user
    owner = None
    if args.org:
        try:
            owner = g.get_organization(args.org)
            print(f"Info: using organization '{args.org}' as owner")
        except GithubException as e:
            print(f"ERROR: Could not access organization '{args.org}': {e}", file=sys.stderr)
            return 2
    else:
        try:
            owner = g.get_user()
            print(f"Info: using authenticated user '{owner.login}' as owner")
        except GithubException as e:
            print(f"ERROR: Could not get authenticated user: {e}", file=sys.stderr)
            return 2

    repo_name = f"libelle-sandbox-{volunteer}"
    print(f"Info: target repo name = {repo_name}")

    # Check if repo already exists under owner
    try:
        existing = owner.get_repo(repo_name)
        print(f"ERROR: Repo '{repo_name}' already exists at {existing.html_url}", file=sys.stderr)
        return 0  # consider success or change to non-zero if you prefer
    except GithubException:
        # expected if repo does not exist
        pass

    # Create repo
    try:
        repo = owner.create_repo(repo_name, private=True, auto_init=True)
        print(f"Created repo: {repo.full_name} ({repo.html_url})")
    except GithubException as e:
        print(f"ERROR: Failed to create repo '{repo_name}': {e}", file=sys.stderr)
        return 2

    # Add README.md (if auto_init didn't already create README, this will try to create)
    try:
        content = f"# Welcome {volunteer}!\n\nThis sandbox repository was automatically created. Happy hacking 🚀\n"
        commit_message = "chore: add welcome README"
        # If repo was auto_init=True, README might already exist; handle that:
        try:
            repo.create_file("README.md", commit_message, content)
            print("Added README.md")
        except GithubException as e_inner:
            # If file exists or other error, try to update or skip
            print(f"Note: couldn't create README (maybe exists): {e_inner}")
    except Exception as e:
        print(f"Warning: README step failed: {e}")

    # Add collaborator
    try:
        repo.add_to_collaborators(volunteer, permission="push")
        print(f"Invited collaborator: {volunteer}")
    except GithubException as e:
        print(f"Warning: Could not add collaborator '{volunteer}': {e}")

    print(f"✅ Sandbox repo created: {repo.full_name}")
    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
