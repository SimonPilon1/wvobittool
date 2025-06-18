# main.py  – tolerant field-matcher + /fields helper
import os, uuid, re
from flask import Flask, request, send_file
from pdfrw import PdfReader, PdfWriter, PdfDict

TEMPLATE = 'forms/WV_permit.pdf'
app = Flask(__name__)

def norm(s: str) -> str:
    """lower-case, drop all non-alphanum to make matching fault-tolerant"""
    return re.sub(r'[^0-9a-z]', '', s.lower())

def fill_permit(ans: dict) -> str:
    clean = {norm(k): v for k, v in ans.items()}
    pdf   = PdfReader(TEMPLATE)
    filled, missed = [], []

    for page in pdf.pages:
        for a in page.Annots or []:
            if not a.T:
                continue
            raw = a.T[1:-1]
            key = norm(raw)
            if key in clean and clean[key]:
                a.V, a.AP, a.Ff = PdfDict(V=clean[key]), '', 1
                filled.append(raw)
            else:
                missed.append(raw)

    print('filled:', ', '.join(filled) or 'none')
    print('missed:', ', '.join(missed) or 'none')

    out = f'/tmp/{uuid.uuid4()}.pdf'
    PdfWriter().write(out, pdf)
    return out

@app.route('/')
def alive():
    return 'Flask server running 👍'

@app.route('/fields', methods=['GET'])
def list_fields():
    names = {a.T[1:-1].strip()
             for p in PdfReader(TEMPLATE).pages
             for a in (p.Annots or []) if a.T}
    return '\n'.join(sorted(names)), 200, {'Content-Type':'text/plain'}

@app.route('/run', methods=['POST'])
def run():
    pdf = fill_permit(request.get_json(force=True).get('data', {}))
    return send_file(pdf, mimetype='application/pdf',
                     as_attachment=True, download_name='WV_Permit.pdf')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
