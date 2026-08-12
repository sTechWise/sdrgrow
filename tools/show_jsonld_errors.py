import json
import re
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
    
    blocks = re.findall(r'(<script\s+type="application/ld\+json">)(.*?)(</script>)', content, re.DOTALL)
    
    print(f"\n{'='*70}")
    print(f"FILE: {f}")
    print(f"{'='*70}")
    print(f"Total JSON-LD blocks found: {len(blocks)}")
    
    for i, (open_tag, block, close_tag) in enumerate(blocks):
        block = block.strip()
        print(f"\n--- Block {i+1} ---")
        try:
            parsed = json.loads(block)
            print(f"VALID - Type: {parsed.get('@type', parsed.get('@graph', 'unknown'))}")
        except json.JSONDecodeError as e:
            print(f"BROKEN at: {e}")
            # Show the problematic area (chars around the error)
            pos = e.pos
            start = max(0, pos - 100)
            end = min(len(block), pos + 100)
            print(f"\nContext around error position {pos}:")
            print(f"...{block[start:pos]}<<<ERROR HERE>>>{block[pos:end]}...")
            print(f"\nLast 200 chars of block:")
            print(block[-200:])
