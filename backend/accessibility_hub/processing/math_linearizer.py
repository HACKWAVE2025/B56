import re
from sympy import sympify, latex
from sympy.printing.mathml import print_mathml

def latex_to_mathml(latex_string):
    """
    Converts a LaTeX string into MathML using SymPy.
    Returns the original string if conversion fails.
    """
    try:
        # Sanitize and parse the LaTeX expression
        expr = sympify(latex_string)
        
        # Convert the SymPy expression to MathML
        mathml_output = print_mathml(expr)
        
        # Wrap in <math> tags for HTML embedding
        return f"<math>{mathml_output}</math>"
    except Exception as e:
        print(f"Could not convert LaTeX to MathML: {latex_string}. Error: {e}")
        # If conversion fails, return the original LaTeX string wrapped in a code tag
        # to prevent it from being rendered incorrectly.
        return f"<code>{latex_string}</code>"

def detect_and_convert_latex(text):
    """
    Detects LaTeX expressions (both inline and block) in a body of text
    and replaces them with accessible MathML.
    """
    # Pattern for block-level LaTeX ($$...$$)
    text = re.sub(r'\$\$(.*?)\$\$', lambda m: latex_to_mathml(m.group(1)), text, flags=re.DOTALL)
    
    # Pattern for inline LaTeX ($...$)
    text = re.sub(r'\$(.*?)\$', lambda m: latex_to_mathml(m.group(1)), text)
    
    return text

def detect_and_linearize(raw_text):
    """
    Main entry point for math processing.
    This function now converts LaTeX to MathML instead of linearizing.
    """
    if not raw_text:
        return ""
    
    # The main logic is now to convert LaTeX to MathML
    processed_text = detect_and_convert_latex(raw_text)
    
    return processed_text