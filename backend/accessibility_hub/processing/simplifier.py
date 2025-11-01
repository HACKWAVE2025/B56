import re

def simplify_text_rule_based(text, sentence_limit=15):
    """
    Applies initial rule-based simplification for cognitive accessibility.
    
    1. Breaks long sentences.
    2. Placeholder for replacing complex words.
    """
    
    simplified_segments = []
    
    # Split text into paragraphs
    paragraphs = text.split('\n\n')

    for para in paragraphs:
        if not para.strip():
            continue
            
        # Basic sentence splitting (using regex)
        sentences = re.split(r'(?<=[.?!])\s+', para.strip())
        
        simplified_para = []
        
        for sentence in sentences:
            # Rule 1: Break very long sentences (rough word count check)
            if len(sentence.split()) > sentence_limit and ' and ' in sentence:
                # Simple splitting at 'and' for complex coordination
                sub_sentences = sentence.split(' and ', 1) 
                simplified_para.append(sub_sentences[0].strip() + '.')
                # If there's a second part, re-add it as a sentence
                if len(sub_sentences) > 1:
                    simplified_para.append(sub_sentences[1].strip())
            else:
                simplified_para.append(sentence.strip())

        # Join the simplified sentences back into a paragraph
        simplified_segments.append(' '.join(simplified_para))
        
    # Join simplified paragraphs with structure preserved
    return '\n\n'.join(simplified_segments)

def simplify(raw_text):
    """Main simplification entry point."""
    if not raw_text:
        return ""
    
    # Start with rule-based approach (as per MVP)
    simplified_text = simplify_text_rule_based(raw_text)
    
    # Future steps: apply word substitution, grammar fixes, etc.
    
    return simplified_text