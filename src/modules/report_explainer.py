import os
import re

try:
    import pymupdf as fitz
except ImportError:
    import fitz

class ReportExplainer:
    def __init__(self):
        # Reference ranges for common blood and lab tests
        self.reference_ranges = {
            "glucose": {"min": 70, "max": 99, "unit": "mg/dL", "name": "Fasting Blood Glucose"},
            "hba1c": {"min": 4.0, "max": 5.6, "unit": "%", "name": "HbA1c (Glycated Hemoglobin)"},
            "hemoglobin": {"min": 12.0, "max": 17.5, "unit": "g/dL", "name": "Hemoglobin (Hb)"},
            "wbc": {"min": 4.5, "max": 11.0, "unit": "x10^3 / µL", "name": "White Blood Cell Count (WBC)"},
            "platelets": {"min": 150, "max": 450, "unit": "x10^3 / µL", "name": "Platelet Count"},
            "cholesterol": {"min": 125, "max": 200, "unit": "mg/dL", "name": "Total Cholesterol"},
            "hdl": {"min": 40, "max": 60, "unit": "mg/dL", "name": "HDL (Good) Cholesterol"},
            "ldl": {"min": 50, "max": 100, "unit": "mg/dL", "name": "LDL (Bad) Cholesterol"},
            "triglycerides": {"min": 35, "max": 150, "unit": "mg/dL", "name": "Triglycerides"},
            "tsh": {"min": 0.4, "max": 4.0, "unit": "mIU/L", "name": "Thyroid Stimulating Hormone (TSH)"},
            "creatinine": {"min": 0.6, "max": 1.2, "unit": "mg/dL", "name": "Serum Creatinine"},
            "vitamin_d": {"min": 30, "max": 100, "unit": "ng/mL", "name": "25-hydroxy Vitamin D"}
        }

    def extract_text_from_pdf(self, file_path: str) -> str:
        """Extract raw text from a PDF report using PyMuPDF (fitz) or fallback."""
        text = ""
        try:
            doc = fitz.open(file_path)
            for page in doc:
                text += page.get_text("text") + "\n"
            doc.close()
        except Exception as e:
            text = f"Error reading PDF with fitz: {e}\n"
            try:
                import pypdf
                reader = pypdf.PdfReader(file_path)
                text = "\n".join([page.extract_text() or "" for page in reader.pages])
            except Exception as e2:
                text += f" Fallback pypdf error: {e2}"
        return text

    def explain_pdf(self, file_path: str) -> dict:
        """Analyze the PDF report and return structured findings."""
        if not os.path.exists(file_path):
            return {
                "success": False,
                "error": "File not found.",
                "summary": "The requested PDF report could not be found."
            }

        raw_text = self.extract_text_from_pdf(file_path)
        if not raw_text.strip():
            return {
                "success": False,
                "error": "Empty or unreadable PDF.",
                "summary": "Could not extract readable text from the uploaded PDF document. Please ensure it is not a scanned image PDF without OCR."
            }

        text_lower = raw_text.lower()
        extracted_metrics = []
        overall_status_flags = []

        # Analyze key medical parameters using regex search
        for key, ref in self.reference_ranges.items():
            pattern = rf"{re.escape(key)}|{re.escape(ref['name'].lower())}"
            if re.search(pattern, text_lower):
                # Search for numeric values following the parameter name
                matches = re.findall(rf"(?:{re.escape(key)}|{re.escape(ref['name'].lower())})[^\d\n]*?(\d+(?:\.\d+)?)", text_lower)
                if matches:
                    try:
                        raw_val = matches[0]
                        if isinstance(raw_val, (tuple, list)):
                            raw_val = raw_val[0]
                        val = float(raw_val)
                        
                        status = "Normal"
                        interpretation = f"Within standard reference range ({ref['min']} - {ref['max']} {ref['unit']})."
                        
                        if val < ref['min']:
                            status = "Low ⚠️"
                            interpretation = f"Below normal threshold ({ref['min']} {ref['unit']}). May indicate lower than expected levels."
                            overall_status_flags.append(f"Low {ref['name']}")
                        elif val > ref['max']:
                            status = "High ⚠️"
                            interpretation = f"Above normal threshold ({ref['max']} {ref['unit']}). May indicate elevated levels."
                            overall_status_flags.append(f"High {ref['name']}")

                        extracted_metrics.append({
                            "name": ref['name'],
                            "value": val,
                            "unit": ref['unit'],
                            "reference_range": f"{ref['min']} - {ref['max']} {ref['unit']}",
                            "status": status,
                            "interpretation": interpretation
                        })
                    except (ValueError, TypeError):
                        continue

        # Generate human-readable overall summary
        if overall_status_flags:
            summary = f"Analysis complete. Found {len(extracted_metrics)} lab metrics. Attention suggested for: {', '.join(overall_status_flags)}."
        elif extracted_metrics:
            summary = f"Analysis complete. Analyzed {len(extracted_metrics)} lab metrics. All detected parameters appear to be within normal reference ranges."
        else:
            summary = "Report text analyzed successfully. General medical report scanned, but specific automated numeric lab markers were not explicitly auto-classified. Detailed breakdown below."

        plain_english = self._generate_plain_english_translation(extracted_metrics, raw_text)
        recommendations = self._generate_recommendations(overall_status_flags)

        return {
            "success": True,
            "raw_text_length": len(raw_text),
            "summary": summary,
            "metrics": extracted_metrics,
            "plain_english_translation": plain_english,
            "recommendations": recommendations,
            "raw_snippet": raw_text[:1000] + ("..." if len(raw_text) > 1000 else "")
        }

    def _generate_plain_english_translation(self, metrics: list, raw_text: str) -> list:
        translations = []
        if not metrics:
            translations.append("• The report contains general diagnostic note text. It is advisable to review the doctor's impression section with your primary care provider.")
        for m in metrics:
            if "High" in m["status"]:
                translations.append(f"• **{m['name']} ({m['value']} {m['unit']})**: Elevated. Your level is higher than the typical cutoff of {m['reference_range']}.")
            elif "Low" in m["status"]:
                translations.append(f"• **{m['name']} ({m['value']} {m['unit']})**: Decreased. Your level is lower than the typical reference of {m['reference_range']}.")
            else:
                translations.append(f"• **{m['name']} ({m['value']} {m['unit']})**: Normal. Healthy baseline matching target standards.")
        return translations

    def _generate_recommendations(self, flags: list) -> list:
        recs = [
            "Share these report findings with your attending healthcare provider or specialist for clinical correlation.",
            "Keep a digital or paper copy of this lab result to track changes over time across your future check-ups.",
            "Maintain optimal hydration and follow any pre-test preparation instructions if follow-up testing is requested."
        ]
        if flags:
            recs.insert(0, f"Discuss the out-of-range markers ({', '.join(flags)}) with your physician to evaluate lifestyle, dietary, or medication adjustments.")
        return recs