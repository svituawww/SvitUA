# GitHub Multiple Accounts & Repositories Management Guide

## 🔑 Key Concepts (Universal - Any OS)
1. **One SSH Key per Account**: `~/.ssh/id_ed25519_github_[account]` (Windows: `%USERPROFILE%\.ssh\`)
2. **SSH Host Aliases**: `~/.ssh/config` maps `git@github-personal` → specific SSH key
3. **Local Git Config**: Each repo uses `git config user.name/email` (not global)
4. **Remote URLs**: `git@github-personal:username/repo.git` (uses SSH alias)
5. **Account Isolation**: Different directories, keys, and configs prevent conflicts
6. **Verification**: `ssh -T git@github-[alias]` tests connection before work
7. **Key Management**: `ssh-add` loads keys, `ssh-add -l` lists loaded keys
8. **Universal Commands**: Same workflow on Windows/macOS/Linux with path adjustments
9. **No Token Conflicts**: SSH keys eliminate GitHub token authentication issues
10. **Scalable**: Add unlimited accounts by creating new SSH key + host alias pairs
