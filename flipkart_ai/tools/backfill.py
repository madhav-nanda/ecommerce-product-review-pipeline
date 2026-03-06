"""Simple wrapper for historical backfill runs."""
import argparse
import subprocess


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", required=True)
    parser.add_argument("--max_pages", type=int, default=200)
    args = parser.parse_args()
    cmd = [
        "python", "-m", "src.orchestration.run_pipeline",
        "--url", args.url,
        "--max_pages", str(args.max_pages),
        "--mode", "full",
    ]
    subprocess.run(cmd, check=True)


if __name__ == "__main__":
    main()
