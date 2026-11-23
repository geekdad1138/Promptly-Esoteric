import argparse
import re
import shutil
import subprocess
import sys
from pathlib import Path


def run_ick(source: Path, expected: str) -> tuple[bool, str]:
    executable = shutil.which("ick")
    if not executable:
        return False, "ick is not installed"

    output_dir = source.parent / ".intercal-build"
    output_dir.mkdir(exist_ok=True)
    executable_path = output_dir / ("hello.exe" if sys.platform == "win32" else "hello")

    try:
        compile_result = subprocess.run(
            [executable, "-b", str(source), "-o", str(executable_path)],
            capture_output=True,
            text=True,
            timeout=30,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        return False, f"ick invocation failed: {exc}"

    if compile_result.returncode != 0:
        detail = (compile_result.stderr or compile_result.stdout).strip()
        return False, f"compiler error: {detail or 'unknown error'}"
    if not executable_path.exists():
        return False, "compiler did not produce an executable"

    try:
        run_result = subprocess.run(
            [str(executable_path)],
            capture_output=True,
            text=True,
            timeout=30,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        return False, f"program invocation failed: {exc}"

    actual = (run_result.stdout or "").strip()
    if run_result.returncode != 0:
        detail = (run_result.stderr or "").strip()
        return False, f"program exit {run_result.returncode}: {detail}"
    if actual == expected:
        return True, actual
    return False, f"expected {expected!r}, got {actual!r}"


def validate_structure(source: Path) -> tuple[bool, str]:
    try:
        code = source.read_text(encoding="utf-8")
    except OSError as exc:
        return False, f"could not read source: {exc}"

    if not re.search(r"\bDO\s*,1\s*<-+\s*#\d+", code, re.IGNORECASE):
        return False, "missing 16-bit array dimension assignment"
    if not re.search(r"\b(?:PLEASE\s+)?READ\s+OUT\s*,1\b", code, re.IGNORECASE):
        return False, "missing READ OUT for array ,1"
    if not re.search(r"\b(?:PLEASE\s+)?GIVE\s+UP\b", code, re.IGNORECASE):
        return False, "missing GIVE UP termination"

    assignments = re.findall(
        r",1\s+SUB\s+#(\d+)\s*<-\s*#(\d+)",
        code,
        re.IGNORECASE,
    )
    if len(assignments) < 1:
        return False, "missing array element assignments"

    indices = [int(index) for index, _ in assignments]
    if len(set(indices)) != len(indices) or max(indices) != len(indices):
        return False, "array element assignments are incomplete or duplicated"

    return True, f"structural validation passed ({len(assignments)} assigned elements)"


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify an INTERCAL Hello World program")
    parser.add_argument("source", type=Path)
    parser.add_argument("--expected", default="Hello World")
    args = parser.parse_args()

    print(f"--- Verifying {args.source} ---")

    valid, detail = validate_structure(args.source)
    if not valid:
        print(f"FAIL: {detail}")
        return 1

    passed, actual = run_ick(args.source, args.expected)
    if passed:
        print(f"PASS: Output matches {args.expected!r}")
        return 0
    if actual == "ick is not installed":
        print(f"SETUP: {detail}")
        print("SETUP: Install C-INTERCAL (ick) to execute this experiment")
        return 2

    print(f"FAIL: {actual}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
