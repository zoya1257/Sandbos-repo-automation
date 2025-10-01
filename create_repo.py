import sys
import os
from github import Github

if _name_ == "_main_":
    volunteer = sys.argv[1]
    token = os.getenv("GH_TOKEN")
    g = Github(token)

    org = g.get_organization("your-org-name")
    repo_name = f"libelle-sandbox-{volunteer}"

    # 1. Create repo
    repo = user.create_repo(repo_name, private=True, auto_init=True)

    # 2. Add README
    repo.create_file("README.md", "add README", f"# Welcome {volunteer}!\nHappy hacking 🚀")

    # 3. Add collaborator
    repo.add_to_collaborators(volunteer, permission="push")

    print(f"✅ Sandbox repo created: {repo_name}")
