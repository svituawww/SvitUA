#!/usr/bin/env python3
"""
CLI Launcher for Deployment Script
Changes to the scripts directory before running deploy.py
"""

import os
import sys
import subprocess

def main():
    # Get the directory where this script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    scripts_dir = os.path.join(script_dir, 'scripts')
    
    # Change to scripts directory
    os.chdir(scripts_dir)
    
    # Get all command line arguments
    args = sys.argv[1:]
    
    # Run deploy.py with the arguments
    deploy_script = os.path.join(scripts_dir, 'deploy.py')
    cmd = [sys.executable, deploy_script] + args
    
    try:
        result = subprocess.run(cmd, check=True)
        return result.returncode
    except subprocess.CalledProcessError as e:
        return e.returncode
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
        return 1

if __name__ == '__main__':
    sys.exit(main())
