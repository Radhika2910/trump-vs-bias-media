from __future__ import annotations

import argparse

from src.pipeline.run_collection import main


parser = argparse.ArgumentParser(description="Collect and analyze Trump/media-bias data.")
parser.add_argument("--sample", action="store_true", help="Use the included sample dataset instead of live APIs.")
args = parser.parse_args()

main(use_sample=args.sample)

