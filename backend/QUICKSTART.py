#!/usr/bin/env python3
"""
RegLoop AI - Quick Start Setup & Testing Guide

Run this to verify your obligation extraction engine is working.
"""

import subprocess
import sys
from pathlib import Path


def run_command(cmd, description):
    """Run a command and report results."""
    print(f"\n{'='*70}")
    print(f"▶ {description}")
    print(f"{'='*70}")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✓ Success\n{result.stdout}")
            return True
        else:
            print(f"✗ Failed\n{result.stderr}")
            return False
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        return False


def main():
    print("\n" + "╔" + "="*68 + "╗")
    print("║" + " "*68 + "║")
    print("║" + "  RegLoop AI - Setup & Testing Guide".center(68) + "║")
    print("║" + " "*68 + "║")
    print("╚" + "="*68 + "╝\n")

    # Check Python version
    print(f"Python Version: {sys.version}")
    if sys.version_info < (3, 8):
        print("⚠ Warning: Python 3.8+ recommended")

    # Step 1: Dependencies
    print("\n" + "─"*70)
    print("STEP 1: Verify Dependencies")
    print("─"*70)

    required_packages = {
        "fastapi": "FastAPI",
        "pdfplumber": "PDF extraction",
        "sqlalchemy": "Database ORM",
        "pydantic": "Data validation",
    }

    all_installed = True
    for package, description in required_packages.items():
        try:
            __import__(package.replace("-", "_"))
            print(f"✓ {package:20} ({description})")
        except ImportError:
            print(f"✗ {package:20} ({description}) - NOT INSTALLED")
            all_installed = False

    if not all_installed:
        print("\n▶ Installing missing packages...")
        run_command(
            "pip install fastapi pdfplumber sqlalchemy>=2.0.0 pydantic>=2.0.0",
            "Install missing dependencies"
        )

    # Step 2: Database setup
    print("\n" + "─"*70)
    print("STEP 2: Initialize Database")
    print("─"*70)

    try:
        from database.db import init_db
        init_db()
        print("✓ Database initialized successfully")
    except Exception as e:
        print(f"✗ Database initialization failed: {str(e)}")

    # Step 3: Test extraction service
    print("\n" + "─"*70)
    print("STEP 3: Test Extraction Service")
    print("─"*70)

    try:
        from services.obligation_extractor import get_extractor

        extractor = get_extractor()

        test_doc = """
        All organizations must implement security controls. 
        The compliance team shall maintain audit logs for 7 years.
        Employees are required to complete annual training.
        """

        result = extractor.extract_obligations(test_doc)
        obligations = result.get("obligations", [])

        print(f"✓ Extractor working - extracted {len(obligations)} obligations")

        for ob in obligations[:2]:
            print(f"\n  {ob['obligation_id']}: {ob['obligation_text'][:50]}...")
            print(f"  Category: {ob['category']} | Priority: {ob['priority']}")

    except Exception as e:
        print(f"✗ Extraction service failed: {str(e)}")
        import traceback
        traceback.print_exc()

    # Step 4: Run full test suite
    print("\n" + "─"*70)
    print("STEP 4: Run Full Test Suite")
    print("─"*70)

    try:
        print("▶ Running comprehensive tests...")
        run_command("python tests_examples.py", "Execute test suite")
    except Exception as e:
        print(f"⚠ Test suite: {str(e)}")

    # Step 5: API startup
    print("\n" + "─"*70)
    print("STEP 5: Ready to Start API")
    print("─"*70)

    print("""
✓ Setup Complete!

To start the FastAPI server:

    uvicorn main:app --reload

Then access:

    API Docs:  http://localhost:8000/docs
    Redoc:     http://localhost:8000/redoc
    OpenAPI:   http://localhost:8000/openapi.json

Quick workflow:

    1. POST /upload           - Upload PDF document
    2. POST /documents/{id}/analyze - Extract obligations
    3. GET /documents/{id}    - View results
    4. GET /obligations       - Query obligations
    5. GET /gap-analysis      - View gap analysis
    6. GET /compliance-summary - Get summary

Test with curl:

    # Upload
    curl -X POST http://localhost:8000/upload \\
      -F "file=@test.pdf"

    # Analyze
    curl -X POST http://localhost:8000/documents/1/analyze

    # Get results
    curl http://localhost:8000/documents/1
    """)

    print("\n" + "═"*70)
    print("✓ RegLoop AI is ready to extract compliance obligations!")
    print("═"*70 + "\n")


if __name__ == "__main__":
    main()
