#!/usr/bin/env python3
from pathlib import Path
import subprocess
ROOT = Path(__file__).resolve().parents[1]
pdf = ROOT/'pdf/style-proof.pdf'
out = ROOT/'qa/style-proof-pages'
out.mkdir(parents=True, exist_ok=True)
for p in range(1, 11):
    prefix = out / f'page-{p:02d}'
    subprocess.run(['pdftoppm','-png','-r','100','-f',str(p),'-singlefile',str(pdf),str(prefix)], check=True)
print('rendered', len(list(out.glob('*.png'))), 'pages to', out)
