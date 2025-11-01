import re

def simplify_text_rule_based(text, sentence_limit=15):
    """Applies initial rule-based simplification for cognitive accessibility."""
    
    simplified_segments = []
    paragraphs = text.split('\n\n')

    for para in paragraphs:
        if not para.strip():
            continue
            
        sentences = re.split(r'(?<=[.?!])\s+', para.strip())
        simplified_para = []
        
        for sentence in sentences:
            # Rule 1: Break very long sentences (rough word count check)
            if len(sentence.split()) > sentence_limit and ' and ' in sentence:
                sub_sentences = sentence.split(' and ', 1) 
                simplified_para.append(sub_sentences[0].strip() + '.')
                if len(sub_sentences) > 1:
                    simplified_para.append(sub_sentences[1].strip())
            else:
                simplified_para.append(sentence.strip())

        simplified_segments.append(' '.join(simplified_para))
        
    return '\n\n'.join(simplified_segments)

def generate_image_html_placeholder(description="Diagram"):
    """Generates accessible HTML for an image placeholder."""
    alt_text = f"Image Description Placeholder: A {description} was found here. Content requires manual description for full accessibility."
    
    return f"""
    <figure class="my-6 p-4 border-2 border-dashed border-gray-400 rounded-lg bg-gray-50 text-center" aria-label="{alt_text}">
        <div style="font-size: 2.5rem; color: #4F46E5; line-height: 1.5;">🖼️</div>
        <figcaption class="text-sm font-semibold text-gray-700 mt-2">
            {description.upper()} PLACEHOLDER
        </figcaption>
        <p class="text-xs text-gray-500 mt-1" role="img" aria-label="{alt_text}">
            {alt_text}
        </p>
    </figure>
    """

def clean_visual_clutter(text):
    """Removes transition words, column headers, and structural noise."""
    
    # 1. Remove table/list headers and structural noise (Specific to the LaTeX example)
    clutter_patterns = {
        r'Sides Label Formula': '', 
        r'Visual Representation:': '', 
        r'Perpendicular a': '',
        r'Base b': '',
        r'Hypotenuse c': '',
        r'Relation to Formula': '',
        r'Applications of Pythagoras Theorem:': 'Applications:',
        r'Mathematical Equation:': 'If the sides are,',
    }
    for pattern, replacement in clutter_patterns.items():
        text = text.replace(pattern, replacement)
    
    # 2. Cleanup numbering/bullets left behind by list environments
    text = re.sub(r'(\s)\d\.\s', r'\1', text) 
    text = re.sub(r'\s+', ' ', text)
    
    return text.strip()

def reintroduce_headings(text):
    """
    Identifies capitalized phrases followed by a colon or appearing alone (like section titles) 
    and wraps them in <h2> tags.
    """
    
    # Pattern 1: Find capital phrases followed by a colon (e.g., Introduction:)
    text = re.sub(
        r'([A-Z][a-zA-Z\s]+):', 
        r'<h2>\1</h2>', 
        text
    )
    
    # Pattern 2: Find capital phrases appearing alone (e.g., Conclusion)
    # This assumes the title is at the start of a line/paragraph
    # Note: We must be careful not to match sentence starts here.
    text = re.sub(
        r'(^|\n)([A-Z][A-Z\s]+)', 
        r'\1<h2>\2</h2>', 
        text
    )
    
    # Cleanup: Remove stray newlines/whitespace left by the process
    text = text.replace('</h2>\n', '</h2>').replace('\n<h2>', '<h2>')
    
    return text

def simplify(raw_text):
    """Main simplification entry point."""
    if not raw_text:
        return ""
    
    # Processing Order: Clean clutter -> Insert headings -> Simplify sentences
    
    # 1. Clean visual clutter (removes table headers, etc.)
    simplified_text = clean_visual_clutter(raw_text)
    
    # 2. Reintroduce headings (fixes structural accessibility report)
    simplified_text = reintroduce_headings(simplified_text)
    
    # 3. Simplify sentences (core cognitive accessibility)
    simplified_text = simplify_text_rule_based(simplified_text)
    
    return simplified_text