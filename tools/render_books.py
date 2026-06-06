#!/usr/bin/env python3
from pathlib import Path
from weasyprint import HTML
import subprocess
ROOT = Path(__file__).resolve().parents[1]
PRINT = ROOT/'printable-a4'
PDF = ROOT/'pdf'
PDF.mkdir(exist_ok=True)
books = ['player-handbook','guide-book','bestiary','campaigns','character-sheets']
for slug in books:
    src = PRINT/f'{slug}-a4.html'
    out = PDF/f'{slug}.pdf'
    HTML(filename=str(src), base_url=str(src.parent)).write_pdf(str(out))
    print('---', slug, '---')
    info = subprocess.check_output(['pdfinfo', str(out)], text=True)
    for line in info.splitlines():
        if line.startswith(('Pages:', 'Page size:', 'File size:')):
            print(line)
