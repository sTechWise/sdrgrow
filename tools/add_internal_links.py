import os

link_edits = [
    {
        "file": r"c:\Users\rubaya\Desktop\sTechWise\SDR GROW\blog\done-for-you-outbound-for-recruitment-agencies.html",
        "target": "This page covers what done-for-you actually includes, what it costs, when it beats doing it yourself, and when it does not.",
        "replacement": 'This page covers what done-for-you actually includes, <a href="/blog/best-outbound-systems-recruitment-agencies">what outbound actually costs</a>, when it beats doing it yourself, and when it does not.'
    },
    {
        "file": r"c:\Users\rubaya\Desktop\sTechWise\SDR GROW\blog\alternative-to-hiring-an-sdr-for-recruitment-agencies.html",
        "target": "<p><strong>Cost:</strong> roughly $1,500 a month in software at the tiers that handle real volume. The honest cost is the labour: over 100 hours a month across list building, sequence writing, deliverability management, content and monitoring. That is more than half a full time person, forever.</p>",
        "replacement": '<p><strong>Cost:</strong> roughly $1,500 a month in software at the tiers that handle real volume. For <a href="/blog/best-outbound-systems-recruitment-agencies">the full cost breakdown</a>, the honest cost is the labour: over 100 hours a month across list building, sequence writing, deliverability management, content and monitoring. That is more than half a full time person, forever.</p>'
    },
    {
        "file": r"c:\Users\rubaya\Desktop\sTechWise\SDR GROW\blog\how-do-recruitment-agencies-get-new-clients.html",
        "target": "This page ranks all seven by how controllable and scalable each one actually is, with the honest costs and timelines, so you can decide where your next client actually comes from instead of waiting for the phone.",
        "replacement": 'This page ranks all seven by how controllable and scalable each one actually is, with <a href="/blog/best-outbound-systems-recruitment-agencies">what each channel costs</a> and timelines, so you can decide where your next client actually comes from instead of waiting for the phone.'
    },
    {
        "file": r"c:\Users\rubaya\Desktop\sTechWise\SDR GROW\blog\sdr-grow-vs-hiring-an-sdr.html",
        "target": "<p>When a recruitment agency decides to take client acquisition seriously, the instinct is to hire: a business development rep, an SDR, someone to \"do outbound.\" Sometimes that's right. Often it's an expensive way to discover you didn't have a system for them to run. Here's the honest math.</p>",
        "replacement": '<p>When a recruitment agency decides to take client acquisition seriously, the instinct is to hire: a business development rep, an SDR, someone to "do outbound." Sometimes that\'s right. Often it\'s an expensive way to discover you didn\'t have a system for them to run. Here\'s <a href="/blog/best-outbound-systems-recruitment-agencies">the real cost comparison</a> and honest math.</p>'
    },
    {
        "file": r"c:\Users\rubaya\Desktop\sTechWise\SDR GROW\blog\client-acquisition-system-for-recruitment-agencies.html",
        "target": "<p><strong>Building it yourself</strong> means roughly $1,500 a month in tools at working tiers: a data source, enrichment, a sender with warming, LinkedIn tooling, monitoring. Plus the real cost, which is over 100 hours a month of labour across list building, sequence writing, content and monitoring. It works if you have a person who owns it and enjoys it. Most agencies do not, which is why the DIY stack usually gets abandoned by week three.</p>",
        "replacement": '<p><strong>Building it yourself</strong> means roughly $1,500 a month in tools at working tiers. When calculating <a href="/blog/best-outbound-systems-recruitment-agencies">what a client acquisition system costs</a>, the real cost is over 100 hours a month of labour across list building, sequence writing, content and monitoring. It works if you have a person who owns it and enjoys it. Most agencies do not, which is why the DIY stack usually gets abandoned by week three.</p>'
    }
]

for item in link_edits:
    filepath = item["file"]
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        if item["target"] in content:
            content = content.replace(item["target"], item["replacement"])
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"Successfully added link to {os.path.basename(filepath)}")
        else:
            print(f"Target text not found in {os.path.basename(filepath)}")
    else:
        print(f"File not found: {filepath}")

print("Prompt 2 Execution Complete.")
