"""Fix JSON-LD syntax errors in 4 broken blog files.
Two issues per file:
1. Author object missing closing } before the comma
2. Each FAQ Question object missing closing } 
"""
import re
import json
import os

blog_dir = r'c:\Users\rubaya\Desktop\sTechWise\SDR GROW\blog'
broken_files = [
    'how-do-recruitment-agencies-get-new-clients.html',
    'client-acquisition-system-for-recruitment-agencies.html',
    'done-for-you-outbound-for-recruitment-agencies.html',
    'alternative-to-hiring-an-sdr-for-recruitment-agencies.html',
]

for f in broken_files:
    filepath = os.path.join(blog_dir, f)
    with open(filepath, 'r', encoding='utf-8') as fh:
        content = fh.read()
    
    original = content
    
    # Fix 1: Author object — missing closing } for the Person object
    # BROKEN:  "worksFor": {"@type": "Organization", "name": "SDR GROW"},
    # FIXED:   "worksFor": {"@type": "Organization", "name": "SDR GROW"}},
    content = content.replace(
        '"worksFor": {"@type": "Organization", "name": "SDR GROW"},',
        '"worksFor": {"@type": "Organization", "name": "SDR GROW"}},'
    )
    
    # Fix 2: FAQ Question objects — missing closing } for each Question
    # BROKEN:  "acceptedAnswer": {"@type": "Answer", "text": "..."},
    # FIXED:   "acceptedAnswer": {"@type": "Answer", "text": "..."}},
    # Use regex to match the pattern (handles varying text content)
    content = re.sub(
        r'("acceptedAnswer":\s*\{"@type":\s*"Answer",\s*"text":\s*"[^"]*"\}),',
        r'\1},',
        content
    )
    
    # Fix 3: Last FAQ Question (no trailing comma, just missing closing })
    # BROKEN:  "acceptedAnswer": {"@type": "Answer", "text": "..."}
    # FIXED:   "acceptedAnswer": {"@type": "Answer", "text": "..."}}
    # Only match the last one before the closing ]
    content = re.sub(
        r'("acceptedAnswer":\s*\{"@type":\s*"Answer",\s*"text":\s*"[^"]*"\})\s*\n(\s*\])',
        r'\1}\n\2',
        content
    )
    
    if content != original:
        # Validate the JSON-LD blocks
        blocks = re.findall(r'<script\s+type="application/ld\+json">\s*(.*?)\s*</script>', content, re.DOTALL)
        all_valid = True
        for i, block in enumerate(blocks):
            try:
                json.loads(block)
            except json.JSONDecodeError as e:
                print(f"  ERROR: Block {i+1} still broken after fix: {e}")
                all_valid = False
        
        if all_valid:
            with open(filepath, 'w', encoding='utf-8') as fh:
                fh.write(content)
            print(f"FIXED: {f} ({len(blocks)} blocks all valid)")
        else:
            print(f"SKIPPED: {f} — fix did not resolve all issues")
    else:
        print(f"NO CHANGE: {f}")
