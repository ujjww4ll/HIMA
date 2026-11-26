"""
Fix raw LaTeX formulas across Flood_Prediction_and_Early_Warning_System_Report.docx
Preserves ALL user edits:
- Bennett University & School of Computer Science Engineering and Technology
- Course: CSET381 (Application of Artificial Intelligence)
- Semester: Fifth Semester B.Tech (2025-2026 Academic Session)
- Supervisor: Dr. Kimmi Gupta
- Team Member Full Names: Sachin Sharma, Anshul Yadav, Ujjwal, Aadi Dhiman, Malvika Yadav, Shubhangi Singh, Sonam Bharti
Transforms all raw LaTeX math ($$...$$, \\frac, \\partial, etc.) into clean, elegant, publication-grade typographic formulas.
"""
import docx
import shutil
from pathlib import Path
import os
import time

DOCX_SRC = Path(r"c:\Users\lenovo\Desktop\aiml project\Flood_Prediction_and_Early_Warning_System_Report.docx")
DOCX_FIXED = Path(r"c:\Users\lenovo\Desktop\aiml project\Flood_Prediction_and_Early_Warning_System_Report_Fixed.docx")

def clean_math_text(text: str) -> str:
    # 1. Saint-Venant equations
    text = text.replace(
        r"$$\frac{\partial A}{\partial t} + \frac{\partial Q}{\partial x} = q, \quad \frac{\partial Q}{\partial t} + \frac{\partial}{\partial x}\left(\frac{\beta Q^2}{A}\right) + gA \frac{\partial h}{\partial x} + gA(S_f - S_0) = 0$$",
        "\n\n    • Continuity Equation (Conservation of Mass):\n      ∂A/∂t + ∂Q/∂x = q\n\n    • Momentum Equation (Conservation of Momentum):\n      ∂Q/∂t + ∂(β·Q² / A)/∂x + g·A·(∂h/∂x) + g·A·(S_f - S_0) = 0\n\nwhere A is wetted cross-sectional area (m²), Q is river discharge (m³/s), h is water depth (m), S_0 is channel bed slope, S_f is friction slope, β is the momentum correction coefficient, g is acceleration due to gravity (9.81 m/s²), and q is lateral tributary inflow."
    )
    
    # 2. Bayesian Prior Odds Calibration
    text = text.replace(
        r"$$\text{Odds}_{true} = \text{Odds}_{sample} \times \left( \frac{\pi_{true}}{1 - \pi_{true}} \Big/ \frac{\pi_{sample}}{1 - \pi_{sample}} \right)$$",
        "\n\n    • Prior Odds Adjustment Formula:\n      Odds_true = Odds_sample × [ (π_true / (1 - π_true)) / (π_sample / (1 - π_sample)) ]\n"
    )
    text = text.replace(
        r"$$P_{calibrated} = \frac{\text{Odds}_{true}}{1 + \text{Odds}_{true}}$$ ",
        "\n    • Calibrated Probability Recovery Formula:\n      P_calibrated = Odds_true / (1 + Odds_true)\n\n"
    )
    text = text.replace(
        r"($BS = \frac{1}{N} \sum (p_i - y_i)^2$)",
        "[Brier Score = (1/N) · Σ (p_i - y_i)²]"
    )
    
    # 3. SVG Dial stroke-dashoffset formula
    text = text.replace(
        r"$$\text{stroke-dashoffset} = 346 \times \left(1 - \frac{\text{Risk Percentage}}{100}\right)$$",
        "\n\n    • Dial Dash-Offset Interpolation:\n      stroke-dashoffset = 346 × [ 1 - (Risk Percentage / 100) ]\n"
    )
    
    # 4. KD-Tree math
    text = text.replace(r"$253,408 \times 2,491 \approx 6.31 \times 10^8$", "253,408 × 2,491 ≈ 6.31 × 10⁸")
    text = text.replace(r"$\mathcal{O}(N \log M)$", "O(N · log M)")
    
    # 5. Cyclical seasonality & Dewpoint
    text = text.replace(r"$f_{\sin} = \sin(2\pi \cdot \text{doy} / 365)$ and $f_{\cos} = \cos(2\pi \cdot \text{doy} / 365)$", "f_sin = sin(2π · DOY / 365) and f_cos = cos(2π · DOY / 365)")
    text = text.replace(r"$\Delta T_d = T_{air} - T_{dew}$", "ΔT_d = T_air - T_dew")
    text = text.replace(r"$\Delta T_d > 15^\circ\text{C}$", "ΔT_d > 15°C")
    text = text.replace(r"($P_{daily} < 1.0\text{ mm}$)", "(P_daily < 1.0 mm)")
    
    # 6. Target and algorithm parameters
    text = text.replace(r"$y_i = 1$", "y_i = 1")
    text = text.replace(r"$y_i = 0$", "y_i = 0")
    text = text.replace(r"($p = 0.765$)", "(p = 0.765)")
    text = text.replace(r"($\lambda = 1.0$)", "(λ = 1.0)")
    text = text.replace(r"$P(X|y) = \prod P(x_j|y)$", "P(X | y) = ∏ P(x_j | y)")
    text = text.replace(r"$\alpha = 0.005$", "α = 0.005")
    text = text.replace(r"**$\tau = 0.2849$**", "τ = 0.2849")
    text = text.replace(r"($0.00035$)", "(0.00035)")
    text = text.replace(r"$\pi_{sample}$", "π_sample")
    text = text.replace(r"$\pi_{true}$", "π_true")
    
    # 7. Coordinate shift
    text = text.replace(r"$\text{Longitude} > 91.6^\circ\text{E}$", "Longitude > 91.6°E")
    text = text.replace(r"($T_{1d}$–$T_{10d}$)", "(T_1d to T_10d)")
    text = text.replace(r"($km^2$)", "(km²)")
    text = text.replace(r"($n$)", "(n)")
    text = text.replace(r"($T_{1d}$ to $T_{10d}$)", "(T_1d to T_10d)")
    
    # Catch any remaining single dollar signs wrapping short math
    text = text.replace("$", "")
    
    return text

def main():
    print(f"Reading user-updated document: {DOCX_SRC}")
    doc = docx.Document(str(DOCX_SRC))
    
    modified_count = 0
    for idx, p in enumerate(doc.paragraphs):
        old_text = p.text
        new_text = clean_math_text(old_text)
        if new_text != old_text:
            p.text = new_text
            modified_count += 1
            print(f"Fixed formulas in Paragraph {idx}")
            
    for ti, table in enumerate(doc.tables):
        for ri, row in enumerate(table.rows):
            for ci, cell in enumerate(row.cells):
                old_text = cell.text
                new_text = clean_math_text(old_text)
                if new_text != old_text:
                    cell.text = new_text
                    modified_count += 1
                    print(f"Fixed formulas in Table {ti} R{ri} C{ci}")
                    
    print(f"Total elements updated: {modified_count}")
    
    # 1. Save to DOCX_FIXED
    doc.save(str(DOCX_FIXED))
    print(f"Successfully saved fixed document to: {DOCX_FIXED}")
    
    # 2. Try to overwrite DOCX_SRC if not locked
    try:
        doc.save(str(DOCX_SRC))
        print(f"Successfully overwrote original document: {DOCX_SRC}")
    except PermissionError:
        print("Note: Original document is currently open in Microsoft Word. We saved the clean version to Flood_Prediction_and_Early_Warning_System_Report_Fixed.docx.")

if __name__ == "__main__":
    main()
