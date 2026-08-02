import json
import os
import re

target_files = [f for f in [
    r'c:\Users\rubaya\Desktop\sTechWise\SDR GROW\blog\best-outbound-systems-recruitment-agencies.html',
    r'c:\Users\rubaya\Desktop\sTechWise\SDR GROW\blog\_drafts\001-best-outbound-systems-recruitment-agencies.html'
] if os.path.exists(f)]

new_title = "What Outbound Costs a Recruitment Agency (2026 Breakdown)"
meta_title = "What Outbound Costs a Recruitment Agency (2026 Breakdown) — SDR GROW"
new_desc = "What outbound actually costs a recruitment agency: tools, labour, SDR hire, and done-for-you compared. The real monthly math for 2026."

sections_to_insert = """

<h2>How Do Outbound Agencies Charge?</h2>
<p>Outbound agencies charge in three models. Retainer, the most common, runs 2,000 to 10,000 dollars a month depending on volume and whether calling is included. Pay-per-meeting runs 150 to 500 dollars per booked meeting, which looks cheap until you count no-shows and unqualified meetings. Pay-per-lead runs 30 to 100 dollars per contact, cheapest per unit and lowest quality. For recruitment agencies specifically, retainer pricing dominates because the work is ongoing pipeline, not a one-off list. A vertical system like SDR GROW sits below the agency retainer at 1,200 dollars a month plus a 1,997 dollar setup, because one person operates it instead of an agency team.</p>

<h2>Is It Worth Paying 10,000 Dollars a Month for an Outbound Agency?</h2>
<p>For most recruitment agencies under 2M revenue, no. A 10,000 dollar a month outbound agency makes sense when you have a proven offer, a high average deal value, and no time to touch the process at all. Below that, you are paying agency overhead and margin for work a vertical system does for a fraction. The honest comparison: a 10,000 dollar agency, a 4,000 to 6,000 dollar in-house SDR, a 1,500 dollar self-run tool stack plus 100 or more hours of labour, or a 1,200 dollar a month system one person runs. The agency is the most hands-off and the most expensive. The system is the best cost-to-outcome for most agencies at this stage.</p>"""

q1 = {
    "@type": "Question",
    "name": "How do outbound agencies charge?",
    "acceptedAnswer": {
        "@type": "Answer",
        "text": "Outbound agencies charge by retainer (2,000 to 10,000 dollars a month), per meeting (150 to 500 dollars), or per lead (30 to 100 dollars). Retainer pricing dominates for recruitment agencies because outbound is ongoing pipeline work."
    }
}

q2 = {
    "@type": "Question",
    "name": "Is it worth paying 10,000 dollars a month for an outbound agency?",
    "acceptedAnswer": {
        "@type": "Answer",
        "text": "For most recruitment agencies under 2M revenue, no. A 10,000 dollar agency suits proven offers with high deal value and no time to run the process. Below that, a vertical system one person runs delivers similar outcomes at a fraction of the cost."
    }
}

for filepath in target_files:
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Update Title tags
    content = re.sub(r'<title>.*?</title>', f'<title>{meta_title}</title>', content)
    content = re.sub(r'<meta property="og:title" content=".*?">', f'<meta property="og:title" content="{new_title}">', content)
    content = re.sub(r'<meta name="twitter:title" content=".*?">', f'<meta name="twitter:title" content="{new_title}">', content)
    content = re.sub(r'<h1>.*?</h1>', f'<h1>{new_title}</h1>', content)

    # 2. Update Meta Description tags
    content = re.sub(r'<meta name="description" content=".*?">', f'<meta name="description" content="{new_desc}">', content)
    content = re.sub(r'<meta property="og:description" content=".*?">', f'<meta property="og:description" content="{new_desc}">', content)
    content = re.sub(r'<meta name="twitter:description" content=".*?">', f'<meta name="twitter:description" content="{new_desc}">', content)

    # 3. Insert new sections after intro paragraph
    intro_target = '<p>So here is the comparison done properly: what it costs to replicate a full outbound operation, module by module, counting both the subscription and the labour it leaves behind.</p>'
    if intro_target in content and '<h2>How Do Outbound Agencies Charge?</h2>' not in content:
        content = content.replace(intro_target, intro_target + sections_to_insert)
        print(f'Inserted sections in {filepath}')

    # 4. Update JSON-LD schema FAQPage
    ld_json_match = re.search(r'<script type="application/ld\+json">(.*?)</script>', content, re.DOTALL)
    if ld_json_match:
        json_str = ld_json_match.group(1)
        schema_data = json.loads(json_str)
        graph = schema_data.get('@graph', [])
        for obj in graph:
            if obj.get('@type') == 'Article':
                obj['headline'] = new_title
                obj['description'] = new_desc
            elif obj.get('@type') == 'FAQPage':
                main_entity = obj.get('mainEntity', [])
                q_names = [q.get('name') for q in main_entity]
                if q1['name'] not in q_names:
                    main_entity.append(q1)
                if q2['name'] not in q_names:
                    main_entity.append(q2)
                obj['mainEntity'] = main_entity
        new_json_str = json.dumps(schema_data, ensure_ascii=False)
        content = content.replace(ld_json_match.group(0), f'<script type="application/ld+json">{new_json_str}</script>')
        print(f'Updated JSON-LD schema in {filepath}')

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

print('Prompt 1 Execution Complete.')
