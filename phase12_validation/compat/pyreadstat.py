"""Phase 12 test-runtime adapter for a policy-blocked pyreadstat native module.

Use only by explicitly prepending this directory to PYTHONPATH. It reads the
original SAV in memory with an already-installed R/foreign distribution; it is
not a general replacement for pyreadstat or a production dependency.
"""

from __future__ import annotations

from io import StringIO
import os
from pathlib import Path
import shutil
import subprocess

import pandas as pd


_R_CODE = (
    "x <- foreign::read.spss(commandArgs(trailingOnly=TRUE)[1], "
    "use.value.labels=FALSE, to.data.frame=TRUE); "
    "write.csv(x, stdout(), row.names=FALSE, na='')"
)


def _rscript() -> str:
    candidate = os.environ.get("PHASE12_RSCRIPT") or shutil.which("Rscript")
    if not candidate and os.name == "nt":
        roots = sorted(Path(r"C:\Program Files\R").glob("R-*"), reverse=True)
        candidate = next((str(root / "bin" / "Rscript.exe") for root in roots
                          if (root / "bin" / "Rscript.exe").is_file()), None)
    if not candidate or not Path(candidate).is_file():
        raise RuntimeError("Rscript with the foreign package is required for the Phase 12 SAV adapter")
    return str(candidate)


def read_sav(path: str, apply_value_formats: bool = False):
    """Return numeric-coded SAV data and no pyreadstat metadata.

    Existing project callers use only the data frame. Unsupported value-label
    formatting is rejected rather than silently changing research semantics.
    """
    if apply_value_formats:
        raise ValueError("Phase 12 SAV adapter supports raw numeric value codes only")
    source = Path(path)
    if not source.is_file() or source.suffix.lower() != ".sav":
        raise FileNotFoundError(source)
    proc = subprocess.run([_rscript(), "-e", _R_CODE, str(source.resolve())],
                          capture_output=True, text=True, encoding="utf-8")
    if proc.returncode:
        raise RuntimeError(f"R foreign SAV read failed: {proc.stderr.strip()}")
    return pd.read_csv(StringIO(proc.stdout)), None
