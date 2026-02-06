#!/usr/bin/env python3
"""
Minimal driver script to run a single planning problem.
"""
import argparse
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description='Run a single planning problem')
    parser.add_argument('--domain', type=Path, required=True)
    parser.add_argument('--problem', type=Path, required=True)
    args = parser.parse_args()

    print(f"Domain: {args.domain}")
    print(f"Problem: {args.problem}")
    
    # Test simplafy import
    try:
        import simplafy
        print(f"✓ simplafy imported from: {simplafy.__file__}")
    except ImportError as e:
        print(f"✗ Failed to import simplafy: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())

