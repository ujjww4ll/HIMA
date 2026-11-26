"""
Clean and fix all mathematical formulas across the user-updated 25-slide PowerPoint Presentation:
Flood_Prediction_and_Early_Warning_System.pptx
Replaces raw LaTeX syntax ($$...$$, \\frac, \\pi, \\sin, \\cos, \\ge, etc.) with clean,
professional presentation typography that renders natively and beautifully in PowerPoint.
"""
from pptx import Presentation
from pathlib import Path

PPTX_PATH = Path(r"c:\Users\lenovo\Desktop\aiml project\Flood_Prediction_and_Early_Warning_System.pptx")
PPTX_FIXED = Path(r"c:\Users\lenovo\Desktop\aiml project\Flood_Prediction_and_Early_Warning_System_Fixed.pptx")

def clean_pptx_formula(text: str) -> str:
    # Slide 10: Wildfire Cyclical and Dewpoint formulas
    text = text.replace(
        r"$$\sin(2\pi \cdot \text{doy} / 365), \quad \cos(2\pi \cdot \text{doy} / 365)$$",
        "sin(2π · DOY / 365),   cos(2π · DOY / 365)"
    )
    text = text.replace(r"$T_{air} - T_{dew}$", "ΔT_d = T_air - T_dew")
    text = text.replace(r"($rain < 1.0\text{ mm}$)", "(Rain < 1.0 mm)")
    
    # Slide 14: Bayesian Prior Odds Formula
    text = text.replace(
        r"$$\text{Odds}_{true} = \text{Odds}_{sample} \times \left( \frac{\pi_{true}}{1 - \pi_{true}} \Big/ \frac{\pi_{sample}}{1 - \pi_{sample}} \right)$$",
        "Odds_true = Odds_sample × [ (π_true / (1 - π_true)) / (π_sample / (1 - π_sample)) ]"
    )
    
    # Slide 16: Flood variables and lags
    text = text.replace(r"$\ge$", "≥")
    text = text.replace(r"- $T_{1d}$:", "- T_1d:")
    text = text.replace(r"- $T_{2d}, T_{3d}$:", "- T_2d, T_3d:")
    text = text.replace(r"- $T_{4d}, T_{5d}, T_{6d}, T_{7d}$:", "- T_4d to T_7d:")
    text = text.replace(r"- $T_{8d}, T_{9d}, T_{10d}$:", "- T_8d to T_10d:")
    text = text.replace(r"($km^2$)", "(km²)")
    
    # Slide 21: Catchment scaling and coordinates
    text = text.replace(r"($100\text{ km}^2$)", "(100 km²)")
    text = text.replace(r"($50,000\text{ km}^2$)", "(50,000 km²)")
    text = text.replace(r"> 91.6°E", "> 91.6°E")
    
    # Slide 23: Recall percentage
    text = text.replace(r"$> 85\%$", "> 85%")
    text = text.replace(r"\%", "%")
    
    # Remove any stray dollar signs
    text = text.replace("$", "")
    
    return text

def main():
    print(f"Loading presentation: {PPTX_PATH}")
    prs = Presentation(str(PPTX_PATH))
    print(f"Total slides in presentation: {len(prs.slides)}")
    
    updated_paragraphs = 0
    
    for idx, slide in enumerate(prs.slides, 1):
        for shape in slide.shapes:
            if shape.has_text_frame:
                for p in shape.text_frame.paragraphs:
                    old_text = p.text
                    new_text = clean_pptx_formula(old_text)
                    if new_text != old_text:
                        p.text = new_text
                        updated_paragraphs += 1
                        print(f"Slide {idx:02d}: Updated formula in paragraph")
                        
            if shape.has_table:
                for row in shape.table.rows:
                    for cell in row.cells:
                        old_text = cell.text
                        new_text = clean_pptx_formula(old_text)
                        if new_text != old_text:
                            cell.text = new_text
                            updated_paragraphs += 1
                            print(f"Slide {idx:02d}: Updated formula in table cell")
                            
    print(f"Total formula updates applied: {updated_paragraphs}")
    
    # Save directly to main file
    prs.save(str(PPTX_PATH))
    print(f"Successfully saved updated presentation to: {PPTX_PATH}")
    
    # Save a fixed copy as backup
    prs.save(str(PPTX_FIXED))
    print(f"Successfully saved backup copy to: {PPTX_FIXED}")

if __name__ == "__main__":
    main()
