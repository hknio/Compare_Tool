import shutil
import subprocess
from pathlib import Path


def ensure_clean_dir(path: str):
    path = Path(path)
    shutil.rmtree(path, ignore_errors=True)
    path.mkdir(parents=True, exist_ok=True)


def clone_specific_rev(repo_url: str, commit_or_branch: str, to_dir: str):
    ensure_clean_dir(to_dir)
    subprocess.run(
        f"""
        git init
        git remote add origin {repo_url}
        git fetch origin {commit_or_branch}
        git checkout {commit_or_branch}
        """,
        cwd=to_dir, shell=True, check=True
    )


def clone_specific_rev_two(repo_url: str, commit_or_branch1: str, commit_or_branch2: str, to_dir1: str, to_dir2: str):
    clone_specific_rev(repo_url, commit_or_branch1, to_dir1)
    ensure_clean_dir(to_dir2)
    shutil.copytree(to_dir1, to_dir2, symlinks=True, dirs_exist_ok=True)
    subprocess.run(
        f"""
        git fetch origin {commit_or_branch2}
        git checkout {commit_or_branch2}
        """,
        cwd=to_dir2, shell=True, check=True
    )
