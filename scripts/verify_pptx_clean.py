from pptx import Presentation

prs = Presentation('Flood_Prediction_and_Early_Warning_System.pptx')
bad_terms = ['$$', r'\frac', r'\partial', r'\prod', r'\tau', r'\pi', r'\Delta', r'\lambda', r'\alpha', r'\text{', r'\approx', r'\mathcal']

found = []
for idx, slide in enumerate(prs.slides, 1):
    for shape in slide.shapes:
        if shape.has_text_frame:
            for p in shape.text_frame.paragraphs:
                for term in bad_terms:
                    if term in p.text:
                        found.append((idx, term, p.text))

if not found:
    print("PPTX VERIFICATION 100% PASSED: Zero raw LaTeX formulas or symbols exist in the PowerPoint presentation!")
else:
    print(f"Found {len(found)} remaining raw symbols in PPTX:")
    for idx, term, txt in found:
        print(f"Slide {idx:02d} [{term}]: {txt}")
