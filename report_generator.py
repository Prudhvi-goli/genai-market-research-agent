import os
from datetime import datetime

REPORTS_DIR = "./reports"
os.makedirs(REPORTS_DIR, exist_ok=True)

def generate_markdown_report(query, summary, use_cases, resources, genai_solutions):
    date = datetime.now().strftime("%Y-%m-%d")
    filename = f"{REPORTS_DIR}/{query.replace(' ', '_')}_GenAI_Report_{date}.md"

    with open(filename, "w", encoding="utf-8") as f:
        f.write(f"# GenAI Market Research Report for {query}\n")
        f.write(f"**Date:** {date}\n\n")

        f.write("## Industry Summary\n")
        f.write(summary + "\n\n")

        f.write("## Use Case Proposals\n")
        for uc in use_cases:
            f.write(uc + "\n\n")

        f.write("## Relevant Datasets\n")
        for title, links in resources.items():
            f.write(f"**{title}**\n")
            for platform, url in links.items():
                f.write(f"- [{platform.capitalize()}]({url})\n")
            f.write("\n")

        f.write("## Suggested GenAI Solutions\n")
        for sol in genai_solutions:
            f.write(f"- {sol}\n")

    print(f"Report saved to {filename}")
