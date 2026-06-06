#!/usr/bin/env python3
from pathlib import Path
from weasyprint import HTML
import subprocess
ROOT = Path(__file__).resolve().parents[1]
src = ROOT/'printable-a4/style-proof-a4.html'
out = ROOT/'pdf/style-proof.pdf'
out.parent.mkdir(exist_ok=True)
HTML(filename=str(src), base_url=str(src.parent)).write_pdf(str(out))
print(subprocess.check_output(['pdfinfo', str(out)], text=True))
