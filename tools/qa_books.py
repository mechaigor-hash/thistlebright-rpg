#!/usr/bin/env python3
from pathlib import Path
import subprocess, shutil
ROOT = Path(__file__).resolve().parents[1]
PDF = ROOT/'pdf'
QA = ROOT/'qa'/'book-pages'
if QA.exists():
    shutil.rmtree(QA)
QA.mkdir(parents=True, exist_ok=True)
books = sorted(p.stem for p in PDF.glob('*.pdf'))
for slug in books:
    pdf = PDF/f'{slug}.pdf'
    outdir = QA/slug
    outdir.mkdir(parents=True, exist_ok=True)
    info = subprocess.check_output(['pdfinfo', str(pdf)], text=True)
    pages = 1
    for line in info.splitlines():
        if line.startswith('Pages:'):
            pages = int(line.split(':',1)[1].strip())
    samples = sorted(set([1, 2, 3, max(1, pages//2), pages]))
    for p in samples:
        prefix = outdir/f'page-{p:02d}'
        subprocess.run(['pdftoppm','-png','-r','90','-f',str(p),'-singlefile',str(pdf),str(prefix)], check=True)
    print(slug, 'sample pages', samples)
