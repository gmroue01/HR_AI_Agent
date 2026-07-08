## Git - "Refusing to merge unrelated histories"

**Context**: Push to the `main` branch failed.

```bash
(venv) PS C:\Users\gmrou\HR_AgentIA> git push origin main
To https://github.com/gmroue01/HR_AI_Agent.git
 ! [rejected]        main -> main (non-fast-forward)
error: failed to push some refs to 'https://github.com/gmroue01/HR_AI_Agent.git'
hint: Updates were rejected because the tip of your current branch is behind
hint: its remote counterpart. Integrate the remote changes (e.g.
hint: 'git pull ...') before pushing again.
hint: See the 'Note about fast-forwards' in 'git push --help' for details.
```

The push is rejected because the local branch is behind the remote branch.

**Hypothesis**: The local and remote repositories have unrelated histories — the GitHub repo was created with a README and `.gitignore` already committed remotely, while the local repo was initialized separately.

**Solution**:
```bash
git pull origin main --allow-unrelated-histories
```

**Why**: `--allow-unrelated-histories` forces Git to merge two histories that don't share a common ancestor (blocked by default as a safety measure).



