import re

def format_editor(text):
    # Split into logical blocks while preserving empty lines
    blocks = [b.strip() for b in re.split(r'\n\s*\n', text) if b.strip()]
    
    final_blocks = []
    synopsis_added = False
    staff_processed = False
    
    for block in blocks:
        # Keep first visual/announcement block
        if re.match(r'^[📓📝📢🎥]', block) and not final_blocks:
            final_blocks.append(block)
            continue
        
        # Keep synopsis blocks
        if block.startswith('💬'):
            final_blocks.append(block)
            synopsis_added = True
            continue
        
        # Process STAFF blocks with different header styles
        if re.match(r'^(📍)?STAFF', block, re.IGNORECASE):
            staff_processed = True
            # Extract studio lines with different bullet styles
            studio_lines = re.findall(
                r'(▪️|\-)\s*(Studio|Animation Studio):\s*(.+)$', 
                block, 
                flags=re.MULTILINE|re.IGNORECASE
            )
            # Rebuild studio lines with original bullet style
            if studio_lines:
                for line in studio_lines:
                    final_blocks.append(f'{line[0]} {line[1]}: {line[2]}'.strip())
            continue
        
        # Remove CAST blocks with different header styles
        if re.match(r'^(📍)?CAST', block, re.IGNORECASE):
            continue
        
        # Preserve other content blocks (source, footer, etc)
        final_blocks.append(block)
    
    # Rebuild the text with proper spacing
    return '\n\n'.join(final_blocks)

