import docx

doc = docx.Document('Flood_Prediction_and_Early_Warning_System_Report_Fixed.docx')
latex_symbols = ['$$', r'\frac', r'\partial', r'\prod', r'\tau', r'\pi', r'\Delta', r'\lambda', r'\alpha', r'\text{', r'\approx', r'\mathcal']

found = []
for i, p in enumerate(doc.paragraphs):
    for sym in latex_symbols:
        if sym in p.text:
            found.append((i, sym, p.text))

if not found:
    print("VERIFICATION 100% PASSED: Zero raw LaTeX formulas or symbols exist in the Fixed Word document!")
else:
    print(f"Found {len(found)} remaining raw symbols:")
    for i, sym, txt in found:
        print(f"P{i} [{sym}]: {txt}")
