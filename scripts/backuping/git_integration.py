import subprocess
import os
from typing import Optional, Tuple


def get_git_commit_hash() -> str:
    """Get current git commit hash."""
    try:
        result = subprocess.run(
            ['git', 'rev-parse', '--short', 'HEAD'],
            capture_output=True,
            text=True,
            cwd=os.getcwd()
        )
        if result.returncode == 0:
            return result.stdout.strip()
        else:
            print("Warning: Could not get git commit hash")
            return "nogit"
    except Exception as e:
        print(f"Warning: Git command failed: {e}")
        return "nogit"


def get_git_commit_message() -> str:
    """Get current git commit message."""
    try:
        result = subprocess.run(
            ['git', 'log', '-1', '--pretty=%B'],
            capture_output=True,
            text=True,
            cwd=os.getcwd()
        )
        if result.returncode == 0:
            return result.stdout.strip()
        else:
            print("Warning: Could not get git commit message")
            return "No commit message"
    except Exception as e:
        print(f"Warning: Git command failed: {e}")
        return "No commit message"


def get_git_status() -> dict:
    """Get git status information."""
    status = {
        'is_repository': False,
        'commit_hash': 'nogit',
        'commit_message': 'No commit message',
        'branch': 'unknown',
        'has_changes': False
    }
    
    try:
        # Check if we're in a git repository
        result = subprocess.run(
            ['git', 'rev-parse', '--git-dir'],
            capture_output=True,
            text=True,
            cwd=os.getcwd()
        )
        
        if result.returncode == 0:
            status['is_repository'] = True
            status['commit_hash'] = get_git_commit_hash()
            status['commit_message'] = get_git_commit_message()
            
            # Get current branch
            branch_result = subprocess.run(
                ['git', 'branch', '--show-current'],
                capture_output=True,
                text=True,
                cwd=os.getcwd()
            )
            if branch_result.returncode == 0:
                status['branch'] = branch_result.stdout.strip()
            
            # Check for uncommitted changes
            changes_result = subprocess.run(
                ['git', 'status', '--porcelain'],
                capture_output=True,
                text=True,
                cwd=os.getcwd()
            )
            if changes_result.returncode == 0 and changes_result.stdout.strip():
                status['has_changes'] = True
                
    except Exception as e:
        print(f"Warning: Git status check failed: {e}")
    
    return status


def is_git_repository() -> bool:
    """Check if current directory is a git repository."""
    try:
        result = subprocess.run(
            ['git', 'rev-parse', '--git-dir'],
            capture_output=True,
            text=True,
            cwd=os.getcwd()
        )
        return result.returncode == 0
    except Exception:
        return False


def get_git_info() -> Tuple[str, str]:
    """Get git commit hash and message as a tuple."""
    return get_git_commit_hash(), get_git_commit_message()
