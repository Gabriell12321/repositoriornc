import os
import subprocess
import sys

REPO = r"G:\\My Drive\\Trabalhos pendentes\\rncs\\RELATORIO DE NÃO CONFORMIDADE IPPEL"
MESSAGE = (
    "feat(groups, julia-analytics): validacoes robustas, cache TTL, pool de DB; + testes e tasks VS Code"
)

def run(cmd, cwd=REPO):
    print("$", " ".join(cmd))
    try:
        out = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, check=False)
        if out.stdout:
            print(out.stdout)
        if out.stderr:
            print(out.stderr)
        return out.returncode
    except Exception as e:
        print("ERR:", e)
        return 1

if __name__ == "__main__":
    # Ensure we're in repo
    if not os.path.isdir(os.path.join(REPO, ".git")):
        print(".git not found at:", REPO)
        sys.exit(2)

    # Show status
    run(["git", "--no-pager", "status", "-sb"]) 

    # Stage changes
    run(["git", "add", "-A"]) 

    # Check if anything is staged
    rc = run(["git", "diff", "--cached", "--name-only"]) 

    # Commit (allow empty so we can push reliably)
    run(["git", "commit", "--allow-empty", "-m", MESSAGE])

    # Push
    rc = run(["git", "push", "origin", "HEAD:master"]) 
    if rc != 0:
        print("Push failed with code", rc)
        sys.exit(rc)

    # Show local/remote heads
    run(["git", "--no-pager", "log", "-1", "--oneline"]) 
    run(["git", "ls-remote", "origin", "-h", "refs/heads/master"]) 
    print("DONE")
