# main.py  – WV permit API + helper
# ---------------------------------
# REQUIREMENTS:  Flask  ·  pdfrw
# PDF template stored at forms/WV_permit.pdf
# -----------------------------------------

import os, uuid
from flask import Flask, request, send_file
from pdfrw import PdfReader, PdfWriter, PdfDict

TEMPLATE = 'forms/WV_permit.pdf'        # relative path inside repl

app = Flask(__name__)

# ---------- helper: fill every AcroForm box ----------
def fill_permit(answer_dict: dict) -> str:
    """
    answer_dict comes from Google Apps Script.
    We match PDF field names after strip() + lower(), so
    'Name of Applicant' == 'Name of Applicant  ' in the PDF.
    Returns a filepath in /tmp/…
    """
    pdf = PdfReader(TEMPLATE)
    clean = {k.strip().lower(): v for k, v in answer_dict.items()}

    for page in pdf.pages:
        for a in page.Annots or []:
            if a.T:
                raw = a.T[1:-1]              # '(Name of Applicant  )'
                key = raw.strip().lower()    # 'name of applicant'
                if key in clean:
                    a.V  = PdfDict(V=clean[key])
                    a.AP = ''                # refresh appearance
                    a.Ff = 1                 # lock field

    out_path = f'/tmp/{uuid.uuid4()}.pdf'
    PdfWriter().write(out_path, pdf)
    return out_path

# ---------- routes ----------
@app.route('/')
def alive():
    return 'Flask server running 👍'

@app.route('/fields', methods=['GET'])
def list_fields():
    """Return plain-text list of every field name in the PDF."""
    names = set()
    for page in PdfReader(TEMPLATE).pages:
        for a in page.Annots or []:
            if a.T:
                names.add(a.T[1:-1].strip())
    return '\n'.join(sorted(names)), 200, {'Content-Type':'text/plain'}

@app.route('/run', methods=['POST'])
def run():
    payload = request.get_json(force=True) or {}
    pdf_path = fill_permit(payload.get('data', {}))
    return send_file(pdf_path,
                     mimetype='application/pdf',
                     as_attachment=True,
                     download_name='WV_Permit.pdf')

# ---------- launch ----------
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))   # Render sets $PORT
    app.run(host='0.0.0.0', port=port)
