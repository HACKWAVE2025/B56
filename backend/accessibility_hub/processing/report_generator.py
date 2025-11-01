import textstat
import re
import json # Used for structuring the final output

def analyze_readability(text):
    """Calculates readability scores for cognitive accessibility."""
    if not text.strip():
        return {
            "flesch_kincaid_grade": "N/A", 
            "automated_readability_index": "N/A",
            "average_sentence_length": "N/A"
        }

    # Calculate standard readability scores
    try:
        fk_grade = textstat.flesch_kincaid_grade(text)
        ari = textstat.automated_readability_index(text)
        avg_sentence_len = textstat.avg_sentence_length(text)
    except Exception:
        # Handle case where textstat fails (e.g., text too short or invalid)
        return {
            "flesch_kincaid_grade": "Error", 
            "automated_readability_index": "Error",
            "average_sentence_length": "Error"
        }

    return {
        "flesch_kincaid_grade": f"{fk_grade} (Target: Grade 8 or below)",
        "automated_readability_index": f"{ari:.2f}",
        "average_sentence_length": f"{avg_sentence_len:.2f}"
    }

def check_structure(html_content, total_images=1):
    """
    Performs basic structural checks on the simplified HTML.
    Mocks ALT text check based on the inserted placeholder.
    """
    
    # 1. Heading Check (A basic check for any heading tag usage)
    has_headings = bool(re.search(r'<h[1-6]>', html_content, re.IGNORECASE))
    
    # 2. ALT Text Check: Checks if the image placeholder (with ALT text) was correctly appended.
    # We look for the unique ALT text structure generated in the simplifier.
    alt_text_pattern = r'aria-label="Image Description Placeholder:'
    alt_found_count = len(re.findall(alt_text_pattern, html_content))
    
    # Assuming one placeholder was inserted in the conversion step:
    alt_missing_count = 1 if total_images > 0 and alt_found_count == 0 else 0
        
    return {
        "heading_structure_status": "Found" if has_headings else "Missing",
        "alt_text_status": f"{alt_found_count}/{total_images} Expected ALT Placeholders Found",
        "alt_missing_count": alt_missing_count,
        "note": "Contrast/Color checks require specific styling data not available in raw HTML text."
    }

def generate_report(simplified_text, simplified_html):
    """Generates the full accessibility report."""
    
    readability = analyze_readability(simplified_text)
    structure_issues = check_structure(simplified_html)
    
    # Determine overall score based on simple metrics (ARI should be reasonably low)
    ari_score = float(readability["automated_readability_index"]) if readability["automated_readability_index"] not in ["N/A", "Error"] else 100
    
    if structure_issues["alt_missing_count"] == 0 and ari_score <= 14.0:
        score_status = "PASS (Meets MVP baseline for structure/readability)"
    else:
        score_status = "REVIEW (Check readability score and missing ALT text)"

    report = {
        "summary_score": score_status,
        "readability_metrics": readability,
        "structure_analysis": structure_issues,
    }
    
    # Return as a JSON formatted string for easy API transport
    return json.dumps(report, indent=4)