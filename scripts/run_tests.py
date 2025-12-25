#!/usr/bin/env python
"""
🧪 Test Runner Script
=====================
Complete test automation for Privacy-Preserving Data Analyzer.

Usage:
    python scripts/run_tests.py              # Run all tests
    python scripts/run_tests.py --quick      # Quick tests only (no performance)
    python scripts/run_tests.py --coverage   # With coverage report
    python scripts/run_tests.py --benchmark  # Performance benchmarks only
    python scripts/run_tests.py --lint       # Lint checks only
    python scripts/run_tests.py --all        # Everything: lint + tests + coverage + benchmark
"""

import subprocess
import sys
import os
import argparse
from pathlib import Path

# Colors for terminal output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'
BOLD = '\033[1m'


def print_header(text):
    print(f"\n{BOLD}{BLUE}{'='*60}{RESET}")
    print(f"{BOLD}{BLUE}{text:^60}{RESET}")
    print(f"{BOLD}{BLUE}{'='*60}{RESET}\n")


def print_success(text):
    print(f"{GREEN}✓ {text}{RESET}")


def print_error(text):
    print(f"{RED}✗ {text}{RESET}")


def print_warning(text):
    print(f"{YELLOW}⚠ {text}{RESET}")


def run_command(cmd, description, exit_on_fail=True):
    """Run a command and handle output."""
    print(f"{BLUE}→ {description}...{RESET}")
    result = subprocess.run(cmd, shell=True)
    
    if result.returncode == 0:
        print_success(f"{description} passed")
        return True
    else:
        print_error(f"{description} failed")
        if exit_on_fail:
            sys.exit(1)
        return False


def run_lint():
    """Run all linting checks."""
    print_header("🧹 Code Quality Checks")
    
    all_passed = True
    
    # Black
    if not run_command("black --check src/ tests/", "Black formatting check", exit_on_fail=False):
        print_warning("Run 'black src/ tests/' to fix formatting")
        all_passed = False
    
    # isort
    if not run_command("isort --check-only src/ tests/", "isort import check", exit_on_fail=False):
        print_warning("Run 'isort src/ tests/' to fix imports")
        all_passed = False
    
    # Flake8
    run_command("flake8 src/ tests/ --max-line-length=120 --ignore=E501,W503 --count", 
                "Flake8 linting", exit_on_fail=False)
    
    # mypy (optional)
    run_command("mypy src/ --ignore-missing-imports", "MyPy type checking", exit_on_fail=False)
    
    return all_passed


def run_unit_tests(coverage=False):
    """Run unit tests."""
    print_header("🧪 Unit Tests")
    
    if coverage:
        cmd = "pytest tests/ -v --cov=src --cov-report=term-missing --cov-report=html -m 'not benchmark'"
    else:
        cmd = "pytest tests/ -v -m 'not benchmark'"
    
    return run_command(cmd, "Unit tests")


def run_benchmarks():
    """Run performance benchmarks."""
    print_header("🚀 Performance Benchmarks")
    
    return run_command(
        "pytest tests/test_performance.py -v --benchmark-only --benchmark-columns=min,max,mean,stddev",
        "Performance benchmarks"
    )


def run_security():
    """Run security checks."""
    print_header("🔒 Security Checks")
    
    run_command("bandit -r src/ -ll --skip B101", "Bandit security scan", exit_on_fail=False)
    run_command("pip-audit", "Dependency vulnerability check", exit_on_fail=False)


def main():
    parser = argparse.ArgumentParser(description="Test runner for Privacy-Preserving Data Analyzer")
    parser.add_argument("--quick", action="store_true", help="Quick tests only (no performance)")
    parser.add_argument("--coverage", action="store_true", help="Run with coverage report")
    parser.add_argument("--benchmark", action="store_true", help="Performance benchmarks only")
    parser.add_argument("--lint", action="store_true", help="Lint checks only")
    parser.add_argument("--security", action="store_true", help="Security checks only")
    parser.add_argument("--all", action="store_true", help="Run everything")
    
    args = parser.parse_args()
    
    # Change to project root
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)
    
    print(f"\n{BOLD}🔒 Privacy-Preserving Data Analyzer - Test Suite{RESET}")
    print(f"Project root: {project_root}\n")
    
    if args.lint:
        run_lint()
    elif args.benchmark:
        run_benchmarks()
    elif args.security:
        run_security()
    elif args.all:
        run_lint()
        run_unit_tests(coverage=True)
        run_benchmarks()
        run_security()
    elif args.quick:
        run_unit_tests(coverage=False)
    elif args.coverage:
        run_unit_tests(coverage=True)
    else:
        # Default: quick tests
        run_unit_tests(coverage=False)
    
    print_header("✅ All Tests Completed!")


if __name__ == "__main__":
    main()
