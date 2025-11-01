import re

def linearize_latex(text):
    """
    Converts common LaTeX structures into simple, spoken English.
    
    This is a rule-based approach for the MVP.
    """
    
    # Rule 1: Handle fractions (\frac{numerator}{denominator})
    # Example: \frac{a}{b} -> "a divided by b" or "a over b"
    # Note: Regex uses non-greedy matching (.*?) for content inside braces
    text = re.sub(r'\\frac{([^{}]+)}{([^{}]+)}', 
                  lambda m: f"the fraction {m.group(1)} over {m.group(2)}", 
                  text)

    # Rule 2: Handle powers/exponents (x^{power})
    # Example: x^2 -> "x squared"; e^{-3} -> "e to the power of negative 3"
    text = re.sub(r'\^\{(.*?)\}', 
                  lambda m: f" to the power of {m.group(1)}", 
                  text)
    
    # Rule 3: Handle basic subscripts (x_{sub})
    # Example: H_2O -> "H sub 2 O"
    text = re.sub(r'_\{(.*?)\}', 
                  lambda m: f" sub {m.group(1)}", 
                  text)
                  
    # Rule 4: Handle square root (\sqrt{content})
    text = re.sub(r'\\sqrt{([^{}]+)}', 
                  lambda m: f"the square root of {m.group(1)}", 
                  text)
                  
    # Rule 5: Simplify common functions/symbols (e.g., \alpha, \sum)
    replacements = {
        r'\\sum': 'the sum of',
        r'\\int': 'the integral of',
        r'\\alpha': 'alpha',
        r'\\beta': 'beta',
        r'\\cdot': ' times ',
    }
    for pattern, replacement in replacements.items():
        text = re.sub(pattern, replacement, text)

    # Cleanup: Remove math mode delimiters ($$)
    text = text.replace('$$', '').replace('$', '')
    
    return text.strip()

def detect_and_linearize(raw_text):
    """
    Finds LaTeX snippets (delimited by $, $$, or \[ \]) 
    and linearizes them to spoken math, then cleans up structural clutter.
    """
    linearized_text = raw_text
    
    # Combined pattern to find content inside: $...$, $$...$$, or \[...\]
    math_pattern = re.compile(r'(\$\$?|\\\[)(.*?)(\$\$?|\\\])', re.DOTALL)
    
    # Find and replace math snippets with linearized text
    for start_delim, content, end_delim in math_pattern.findall(raw_text):
        if len(content.split('\n')) > 10: 
             continue
        
        linearized_content = linearize_latex(content)
        original_snippet = start_delim + content + end_delim
        
        # Use a non-greedy replacement to avoid replacing too much text if the snippet appears multiple times
        # Note: Since we are iterating over findall, we use simple string replace for speed, 
        # assuming content is unique enough post-linearization.
        linearized_text = linearized_text.replace(original_snippet, f" (Mathematical Formula: {linearized_content}) ", 1)

    # -------------------------------------------------------------
    # POST-PROCESSING CLEANUP (Structural Element Removal)
    # -------------------------------------------------------------
    text = linearized_text
    
    # 1. Remove large environments (documentclass, usepackage, document, center) and their arguments
    # Target: \command{...} or \command[...]
    # This aggressively removes the boilerplate header/footer code.
    text = re.sub(r'\\(documentclass|usepackage|geometry|array|begin|end)\{[^{}]*\}?', '', text, flags=re.IGNORECASE) 

    # 2. Remove commands that define structure but don't output text (section*, item, rule, newcommand, etc.)
    # The '?' makes the argument brace { } optional in case it was stripped earlier
    structural_commands = [
        r'\\section\*?\{[^{}]*\}',  # E.g., \section*{Introduction}
        r'\\(itemize|enumerate|tabular|tabularx|array|hline|rowcolor|arraystretch|vspace|hspace|label|caption|rule|vspace|hline)', # Structural environments
        r'\\(document|center|par)', # Environment delimiters already stripped
        r'\\[0-9.]{1,5}cm', # \newline spacing commands like \\[0.5cm]
    ]
    for pattern in structural_commands:
        text = re.sub(pattern, ' ', text, flags=re.IGNORECASE | re.DOTALL)

    # 3. Handle text formatting commands and keep the content
    # Target: \bf{content}, \LARGE{content}, \textit{content}
    text = re.sub(r'\\(\w+)\{([^{}]+)\}', r'\2', text) 
    
    # 4. Remove all remaining structural characters: \, {, }, [, ]
    text = re.sub(r'[\\\{\}\[\]]', ' ', text)
    
    # 5. Final cleanup of excessive whitespace (multiple spaces/newlines to single space)
    text = re.sub(r'\s+', ' ', text)
    
    return text.strip()