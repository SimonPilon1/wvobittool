# main.py  – tiny permit API
# ---------------------------------------------
from flask import Flask, request, send_file
from pdfrw import PdfReader, PdfWriter, PdfDict
import os, io, uuid

TEMPLATE = 'forms/WV_permit.pdf'          # make sure this file exists
FIELD_MAP = {'Name of Applicant': 'Name of Applicant'}  # keep for now

app = Flask(__name__)

def fill_permit(data: dict):
    pdf = PdfReader(TEMPLATE)
    for page in pdf.pages:
        for a in page.Annots or []:
            if a.T:
                key = a.T[1:-1]
                if key in FIELD_MAP and FIELD_MAP[key] in data:
                    a.update(PdfDict(V=data[FIELD_MAP[key]]))
                    a.AP = ''
                    a.Ff = 1
    out_path = f"/tmp/{uuid.uuid4()}.pdf"
    PdfWriter().write(out_path, pdf)
    return out_path

# ---------- HTTP routes ----------
@app.route('/')
def alive():
    return 'Flask server running 👍'

@app.route('/run', methods=['POST'])
def run():
    payload = request.get_json(force=True)
    pdf_path = fill_permit(payload.get('data', {}))
    return send_file(pdf_path, mimetype='application/pdf',
                     as_attachment=True, download_name='WV_Permit.pdf')

if __name__ == '__main__':
    #  Replit looks for something listening on port 8080
    app.run(host='0.0.0.0', port=8080)
