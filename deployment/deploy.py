#!/usr/bin/env python3
"""
Main Deployment Script for Loopia.se Hosting
Command-line interface for deployment automation
"""

import argparse
import sys
import os
import json
from datetime import datetime
from pathlib import Path

# Add scripts directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'scripts'))

from deployment_manager import DeploymentManager


def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description='Deployment automation script for Loopia.se hosting',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python deploy.py --environment production --source ./cms/ --remote /public_html/
  python deploy.py --environment staging --incremental --source ./cms/ --remote /public_html/staging/
  python deploy.py --rollback --version 2024-01-15-14-30-00
  python deploy.py --config ./config/deployment_config.yaml --environment production
        """
    )
    
    parser.add_argument(
        '--environment', '-e',
        choices=['development', 'staging', 'production'],
        help='Target environment for deployment'
    )
    
    parser.add_argument(
        '--source', '-s',
        help='Source directory to deploy'
    )
    
    parser.add_argument(
        '--remote', '-r',
        help='Remote directory path'
    )
    
    parser.add_argument(
        '--config', '-c',
        default='config/deployment_config.yaml',
        help='Configuration file path (default: config/deployment_config.yaml)'
    )
    
    parser.add_argument(
        '--incremental', '-i',
        action='store_true',
        help='Perform incremental deployment (only changed files)'
    )
    
    parser.add_argument(
        '--rollback',
        action='store_true',
        help='Rollback to previous version'
    )
    
    parser.add_argument(
        '--version',
        help='Version to rollback to (required with --rollback)'
    )
    
    parser.add_argument(
        '--test',
        action='store_true',
        help='Test configuration and connections without deploying'
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be deployed without actually deploying'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Verbose output'
    )
    
    return parser.parse_args()


def validate_arguments(args):
    """Validate command line arguments"""
    # Test command doesn't need deployment arguments
    if args.test:
        if not os.path.exists(args.config):
            print(f"Error: Configuration file '{args.config}' does not exist")
            return False
        return True
    
    if args.rollback:
        if not args.version:
            print("Error: --version is required when using --rollback")
            return False
        if args.environment or args.source or args.remote:
            print("Error: --rollback cannot be used with deployment arguments")
            return False
    else:
        if not args.environment:
            print("Error: --environment is required for deployment")
            return False
        if not args.source:
            print("Error: --source is required for deployment")
            return False
        if not args.remote:
            print("Error: --remote is required for deployment")
            return False
        if not os.path.exists(args.source):
            print(f"Error: Source directory '{args.source}' does not exist")
            return False
    
    if not os.path.exists(args.config):
        print(f"Error: Configuration file '{args.config}' does not exist")
        return False
    
    return True


def print_banner():
    """Print deployment banner"""
    print("=" * 60)
    print("           Loopia.se Deployment Automation")
    print("=" * 60)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()


def print_deployment_info(args):
    """Print deployment information"""
    print("Deployment Configuration:")
    print(f"  Environment: {args.environment}")
    print(f"  Source: {args.source}")
    print(f"  Remote: {args.remote}")
    print(f"  Config: {args.config}")
    print(f"  Incremental: {args.incremental}")
    print(f"  Dry Run: {args.dry_run}")
    print()


def test_configuration(config_file):
    """Test configuration and connections"""
    print("Testing configuration and connections...")
    
    try:
        manager = DeploymentManager(config_file)
        
        # Test configuration loading
        print("✓ Configuration loaded successfully")
        
        # Test connections to all environments
        for environment in manager.config['environments'].keys():
            print(f"Testing connection to {environment}...")
            if manager.connect(environment):
                print(f"✓ {environment} connection successful")
                manager.transfer.disconnect()
            else:
                print(f"✗ {environment} connection failed")
        
        # Generate test report
        print("\n" + manager.generate_test_report())
        
        return True
        
    except Exception as e:
        print(f"✗ Configuration test failed: {str(e)}")
        return False


def perform_deployment(args):
    """Perform the actual deployment"""
    try:
        manager = DeploymentManager(args.config)
        
        if args.dry_run:
            print("DRY RUN MODE - No files will be uploaded")
            print("Files that would be deployed:")
            
            # Connect to get file list
            if manager.connect(args.environment):
                files_to_upload = manager._get_files_to_upload(args.source, args.incremental)
                for local_file, remote_file in files_to_upload:
                    print(f"  {local_file} -> {remote_file}")
                print(f"\nTotal files: {len(files_to_upload)}")
                manager.transfer.disconnect()
            return True
        
        # Perform actual deployment
        result = manager.deploy(
            source_path=args.source,
            remote_path=args.remote,
            environment=args.environment,
            incremental=args.incremental
        )
        
        if result['success']:
            print(f"\n✓ Deployment successful!")
            print(f"  Files uploaded: {result['uploaded_count']}")
            print(f"  Files failed: {result['failed_count']}")
            print(f"  Deployment time: {result['deployment_time']:.2f}s")
        else:
            print(f"\n✗ Deployment failed: {result.get('error', 'Unknown error')}")
            return False
        
        return True
        
    except Exception as e:
        print(f"✗ Deployment error: {str(e)}")
        return False


def perform_rollback(args):
    """Perform rollback operation"""
    try:
        manager = DeploymentManager(args.config)
        result = manager.rollback(args.version)
        
        if result['success']:
            print(f"✓ Rollback successful: {result['message']}")
        else:
            print(f"✗ Rollback failed: {result.get('error', 'Unknown error')}")
            return False
        
        return True
        
    except Exception as e:
        print(f"✗ Rollback error: {str(e)}")
        return False


def main():
    """Main function"""
    print_banner()
    
    # Parse arguments
    args = parse_arguments()
    
    # Validate arguments
    if not validate_arguments(args):
        sys.exit(1)
    
    # Print deployment info
    if not args.rollback:
        print_deployment_info(args)
    
    # Test configuration if requested
    if args.test:
        if test_configuration(args.config):
            print("✓ Configuration test completed successfully")
        else:
            print("✗ Configuration test failed")
            sys.exit(1)
        return
    
    # Perform rollback if requested
    if args.rollback:
        if perform_rollback(args):
            print("✓ Rollback completed successfully")
        else:
            print("✗ Rollback failed")
            sys.exit(1)
        return
    
    # Perform deployment
    if perform_deployment(args):
        print("✓ Deployment completed successfully")
    else:
        print("✗ Deployment failed")
        sys.exit(1)


if __name__ == '__main__':
    main() 