#!/usr/bin/env python3
"""
main.py — PurpleOcaz Listing Crew entry point.

Usage:
    python3 crewai_crew/main.py --niche "Nail Technician"
    python3 crewai_crew/main.py --niche "Lash Artist"
    python3 crewai_crew/main.py --niche "Personal Trainer"

The crew will:
  1. Planner: Read sample config, design full niche JSON, write to configs/niches/{slug}.json
  2. Builder: Run factory → hero pipeline → verify → evaluate → sprint contract

The Etsy listing is left as DRAFT. Andy activates manually after reviewing.
"""

import argparse
import sys
from pathlib import Path

# Ensure project root is on sys.path so imports work when run from any cwd
PROJECT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT))

from crewai_crew.crew import PurpleOcazCrew


def main():
    ap = argparse.ArgumentParser(
        description="PurpleOcaz Listing Crew — automated niche build pipeline"
    )
    ap.add_argument(
        "--niche",
        required=True,
        help='Human-readable niche name, e.g. "Nail Technician" or "Personal Trainer"',
    )
    args = ap.parse_args()

    print(f"\n{'='*60}")
    print(f"PURPLEOCAZ LISTING CREW")
    print(f"Niche: {args.niche}")
    print(f"Phase 1: Planner + Builder")
    print(f"{'='*60}\n")

    inputs = {"niche_name": args.niche}

    try:
        result = PurpleOcazCrew().crew().kickoff(inputs=inputs)
        print(f"\n{'='*60}")
        print("CREW COMPLETE")
        print(f"{'='*60}")
        print(result)
    except KeyboardInterrupt:
        print("\nAborted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\nCREW FAILED: {e}")
        raise


if __name__ == "__main__":
    main()
