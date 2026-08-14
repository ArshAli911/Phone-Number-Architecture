import docx, re, json
from docx.table import Table
from docx.text.paragraph import Paragraph
from docx.oxml.ns import qn

d = docx.Document('/mnt/user-data/uploads/Phone_Number_Architecture.docx')
body = d.element.body
items = []
for child in body.iterchildren():
    if child.tag == qn('w:p'):
        p = Paragraph(child, d)
        # detect list
        numPr = child.find(qn('w:pPr'))
        is_list = False
        if numPr is not None and numPr.find(qn('w:numPr')) is not None:
            is_list = True
        bold = bool(p.runs) and all(r.bold for r in p.runs if r.text.strip())
        items.append({'k':'p','text':p.text.rstrip(),'list':is_list,'bold':bold})
    elif child.tag == qn('w:tbl'):
        t = Table(child, d)
        rows=[[c.text.strip() for c in r.cells] for r in t.rows]
        items.append({'k':'table','rows':rows})

json.dump(items, open('items.json','w'), ensure_ascii=False, indent=0)
print(len(items))
