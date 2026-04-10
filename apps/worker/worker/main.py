from .pipeline import run_pipeline


def main() -> int:
    run_pipeline("dry-run")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
