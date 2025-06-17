from pdfrw import PdfReader
pdf = PdfReader('forms/WV_permit.pdf')     # path to your blank permit
for p in pdf.pages:
    if '/Annots' in p:
        for a in p.Annots or []:
            if a.T:
                print(a.T[1:-1])
