#!/usr/bin/env python3
import os
import re

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STANDARD_TEX = os.path.join(BASE_DIR, "standard", "ariel_paulin.tex")
OUTPUT_HTML = os.path.join(BASE_DIR, "standard", "ariel_paulin.html")

def strip_comments(text):
    lines = []
    for line in text.split('\n'):
        line_no_comment = re.sub(r'(?<!\\)%.*', '', line)
        lines.append(line_no_comment)
    return '\n'.join(lines)

def clean_latex(text):
    text = re.sub(r'\\textbf\{([^}]+)\}', r'<strong>\1</strong>', text)
    text = re.sub(r'\\textit\{([^}]+)\}', r'<em>\1</em>', text)
    text = re.sub(r'\\small\{([^}]+)\}', r'\1', text)
    text = re.sub(r'\\href\{([^}]+)\}\{([^}]+)\}', r'<a href="\1" target="_blank" rel="noopener">\2</a>', text)
    text = text.replace(r'\small', '').replace(r'\textit', '').replace(r'\textbf', '')
    text = text.replace(r'\textbar', '|').replace(r'\textasciitilde', '~')
    text = text.replace(r'\quad', '').replace(r'\$', '$').replace(r'\%', '%')
    text = text.replace(r'\&', '&').replace(r'\_', '_').replace(r'\#', '#')
    text = text.replace(r'\\\\', '').replace(r'\\', '')
    text = re.sub(r'\\vspace\{[^}]+\}', '', text)
    text = text.replace('--', '–')
    return text.strip()

def read_tex_with_inputs(file_path):
    dir_name = os.path.dirname(file_path)
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    def replace_input(match):
        input_rel_path = match.group(1)
        if not input_rel_path.endswith('.tex'):
            input_rel_path += '.tex'
        full_path = os.path.normpath(os.path.join(dir_name, input_rel_path))
        if os.path.exists(full_path):
            with open(full_path, 'r', encoding='utf-8') as input_file:
                return input_file.read()
        return f"% Missing input: {input_rel_path}"

    full_content = re.sub(r'\\input\{([^}]+)\}', replace_input, content)
    return strip_comments(full_content)

def parse_resume():
    raw_content = read_tex_with_inputs(STANDARD_TEX)

    # Name
    name_match = re.search(r'\\Huge\s+([^}]+)\}', raw_content)
    name = name_match.group(1).strip() if name_match else "Ariel Paulin"

    # Contact
    email_match = re.search(r'href\{mailto:([^}]+)\}', raw_content)
    email = email_match.group(1).strip() if email_match else ""

    linkedin_match = re.search(r'href\{https://www\.linkedin\.com/in/([^}]+)\}', raw_content)
    linkedin = linkedin_match.group(1).strip() if linkedin_match else ""

    github_match = re.search(r'href\{https://github\.com/([^}]+)\}', raw_content)
    github = github_match.group(1).strip() if github_match else ""

    # Summary
    summary_match = re.search(r'\\begin\{quote\}(.*?)\\end\{quote\}', raw_content, re.DOTALL)
    summary = ""
    if summary_match:
        summary = clean_latex(summary_match.group(1))
        # Remove tags for summary quote
        summary = re.sub(r'<[^>]+>', '', summary).strip()

    # Experience
    experience = []
    exp_block_match = re.search(r'\\section\{Experience\}(.*?)(=\\section|\\section|\\end\{document\})', raw_content, re.DOTALL)
    exp_text = exp_block_match.group(1) if exp_block_match else ""

    subheading_pattern = re.compile(
        r'\\resumeSubheading\s*\{([^}]+)\}\s*\{([^}]+)\}\s*\{([^}]+)\}\s*\{([^}]+)\}'
        r'(.*?)(?=\\resumeSubheading|\\section|\\end\{document\}|\Z)', re.DOTALL
    )

    for match in subheading_pattern.finditer(exp_text):
        title = clean_latex(match.group(1))
        dates = clean_latex(match.group(2))
        company = clean_latex(match.group(3))
        location = clean_latex(match.group(4))
        item_block = match.group(5)

        bullets = []
        for b_match in re.finditer(r'\\resumeItem\{([^}]+)\}', item_block):
            bullets.append(clean_latex(b_match.group(1)))

        experience.append({
            "title": title,
            "company": company,
            "location": location,
            "dates": dates,
            "bullets": bullets
        })

    # Skills
    skills = []
    skills_block_match = re.search(r'\\section\{Skills\}(.*?)(=\\section|\\section|\\end\{document\})', raw_content, re.DOTALL)
    if skills_block_match:
        skills_text = skills_block_match.group(1)
        for line in skills_text.split('\n'):
            if ':' in line and '\\textbf{' in line:
                cleaned_line = line.replace(r'\textbf{', '').replace(r'}', '')
                cleaned_line = cleaned_line.replace(r'\textbar', '|').replace(r'\quad', '')
                cleaned_line = cleaned_line.replace(r'\&', '&').replace(r'\\\\', '').replace(r'\\', '').strip()
                if ':' in cleaned_line:
                    parts = cleaned_line.split(':', 1)
                    category = parts[0].strip()
                    val_raw = parts[1].strip()
                    items = [clean_latex(item).replace('\\', '').strip() for item in val_raw.split('|') if item.strip()]
                    skills.append({"category": category, "items": items})

    # Education
    education = []
    edu_block_match = re.search(r'\\section\{Education\}(.*?)(=\\section|\\section|\\end\{document\})', raw_content, re.DOTALL)
    if edu_block_match:
        edu_text = edu_block_match.group(1)
        for match in subheading_pattern.finditer(edu_text):
            inst = clean_latex(match.group(1))
            loc = clean_latex(match.group(2))
            degree = clean_latex(match.group(3))
            dates = clean_latex(match.group(4))
            education.append({
                "institution": inst,
                "degree": degree,
                "location": loc,
                "dates": dates
            })

    return {
        "name": name,
        "email": email,
        "linkedin": linkedin,
        "github": github,
        "summary": summary,
        "experience": experience,
        "skills": skills,
        "education": education
    }

def generate_html(data):
    html_parts = []
    html_parts.append(f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{data['name']} — Resume</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Roboto:ital,wght@0,400;0,500;0,700;1,400&display=swap" rel="stylesheet">
    <style>
        :root {{
            --primary: #0395DE;
            --primary-dark: #027BB8;
            --text-heading: #0f172a;
            --text-body: #334155;
            --text-muted: #64748b;
            --bg-page: #f8fafc;
            --bg-card: #ffffff;
            --border-color: #e2e8f0;
        }}

        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }}

        body {{
            font-family: 'Roboto', 'Inter', -apple-system, sans-serif;
            background-color: var(--bg-page);
            color: var(--text-body);
            line-height: 1.5;
            padding: 40px 16px;
            display: flex;
            justify-content: center;
        }}

        .resume-card {{
            background: var(--bg-card);
            width: 100%;
            max-width: 840px;
            padding: 48px 56px;
            border-radius: 12px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.05), 0 1px 3px rgba(0, 0, 0, 0.03);
            border: 1px solid var(--border-color);
        }}

        /* Header */
        header {{
            text-align: center;
            margin-bottom: 24px;
        }}

        header h1 {{
            font-family: 'Inter', sans-serif;
            font-size: 32px;
            font-weight: 800;
            color: var(--text-heading);
            letter-spacing: -0.02em;
            margin-bottom: 6px;
        }}

        .contact-bar {{
            font-size: 13.5px;
            color: var(--text-muted);
            display: flex;
            justify-content: center;
            align-items: center;
            gap: 12px;
            flex-wrap: wrap;
        }}

        .contact-bar a {{
            color: var(--primary);
            text-decoration: none;
            font-weight: 500;
            transition: color 0.15s ease;
        }}

        .contact-bar a:hover {{
            color: var(--primary-dark);
            text-decoration: underline;
        }}

        .contact-bar .sep {{
            color: #cbd5e1;
        }}

        .summary-box {{
            font-style: italic;
            font-size: 13.5px;
            color: #475569;
            text-align: center;
            margin-top: 14px;
            line-height: 1.5;
        }}

        /* Sections */
        section {{
            margin-bottom: 24px;
        }}

        .section-title {{
            font-family: 'Inter', sans-serif;
            font-size: 16px;
            font-weight: 700;
            color: var(--primary);
            text-transform: uppercase;
            letter-spacing: 0.04em;
            padding-bottom: 6px;
            border-bottom: 2px solid var(--primary);
            margin-bottom: 16px;
        }}

        /* Experience Item */
        .exp-item {{
            margin-bottom: 18px;
        }}

        .exp-header {{
            display: flex;
            justify-content: space-between;
            align-items: baseline;
            margin-bottom: 6px;
            flex-wrap: wrap;
            gap: 4px;
        }}

        .exp-title-group {{
            font-size: 14.5px;
            color: var(--text-heading);
        }}

        .exp-title {{
            font-weight: 700;
        }}

        .exp-company {{
            font-weight: 600;
            color: var(--text-heading);
        }}

        .exp-location {{
            font-style: italic;
            color: var(--primary);
            font-size: 13px;
        }}

        .exp-dates {{
            font-family: 'Inter', sans-serif;
            font-size: 12.5px;
            font-weight: 600;
            color: #64748b;
            background: #f1f5f9;
            padding: 2px 8px;
            border-radius: 4px;
            white-space: nowrap;
        }}

        .exp-bullets {{
            margin-top: 6px;
            padding-left: 20px;
        }}

        .exp-bullets li {{
            font-size: 13px;
            color: var(--text-body);
            margin-bottom: 4px;
            line-height: 1.45;
        }}

        .exp-bullets li::marker {{
            color: var(--primary);
        }}

        /* Skills */
        .skills-grid {{
            display: flex;
            flex-direction: column;
            gap: 8px;
        }}

        .skill-group {{
            display: flex;
            font-size: 13px;
            line-height: 1.5;
        }}

        .skill-cat {{
            font-weight: 700;
            color: var(--text-heading);
            width: 190px;
            flex-shrink: 0;
        }}

        .skill-tags {{
            display: flex;
            flex-wrap: wrap;
            gap: 6px;
        }}

        .skill-tag {{
            background: #f1f5f9;
            color: #334155;
            padding: 2px 9px;
            border-radius: 6px;
            font-size: 12.5px;
            font-weight: 500;
            border: 1px solid #e2e8f0;
        }}

        /* Print Optimization */
        @media print {{
            body {{
                background: #ffffff;
                padding: 0;
            }}
            .resume-card {{
                box-shadow: none;
                border: none;
                padding: 0;
                max-width: 100%;
            }}
        }}

        @media (max-width: 640px) {{
            body {{
                padding: 16px 8px;
            }}
            .resume-card {{
                padding: 24px 18px;
            }}
            .exp-header {{
                flex-direction: column;
                align-items: flex-start;
            }}
            .skill-group {{
                flex-direction: column;
                gap: 4px;
            }}
            .skill-cat {{
                width: 100%;
            }}
        }}
    </style>
</head>
<body>

<main class="resume-card">
    <header>
        <h1>{data['name']}</h1>
        <div class="contact-bar">
            <a href="mailto:{data['email']}">{data['email']}</a>
            <span class="sep">•</span>
            <a href="https://www.linkedin.com/in/{data['linkedin']}" target="_blank" rel="noopener">linkedin.com/in/{data['linkedin']}</a>
            <span class="sep">•</span>
            <a href="https://github.com/{data['github']}" target="_blank" rel="noopener">github.com/{data['github']}</a>
        </div>
        {f'<div class="summary-box">{data["summary"]}</div>' if data['summary'] else ''}
    </header>

    <section>
        <h2 class="section-title">Experience</h2>
""")

    for exp in data['experience']:
        bullets_html = "\n".join([f"            <li>{b}</li>" for b in exp['bullets']])
        html_parts.append(f"""
        <article class="exp-item">
            <div class="exp-header">
                <div class="exp-title-group">
                    <span class="exp-title">{exp['title']}</span> <span class="sep">|</span> <span class="exp-company">{exp['company']}</span> <span class="sep">|</span> <span class="exp-location">{exp['location']}</span>
                </div>
                <div class="exp-dates">{exp['dates']}</div>
            </div>
            <ul class="exp-bullets">
{bullets_html}
            </ul>
        </article>
""")

    html_parts.append("""
    </section>

    <section>
        <h2 class="section-title">Skills</h2>
        <div class="skills-grid">
""")

    for sk in data['skills']:
        tags_html = "".join([f'<span class="skill-tag">{item}</span>' for item in sk['items']])
        html_parts.append(f"""
            <div class="skill-group">
                <div class="skill-cat">{sk['category']}:</div>
                <div class="skill-tags">
                    {tags_html}
                </div>
            </div>
""")

    html_parts.append("""
        </div>
    </section>

    <section>
        <h2 class="section-title">Education</h2>
""")

    for edu in data['education']:
        html_parts.append(f"""
        <article class="exp-item">
            <div class="exp-header">
                <div class="exp-title-group">
                    <span class="exp-title">{edu['institution']}</span> <span class="sep">|</span> <span class="exp-company">{edu['degree']}</span> <span class="sep">|</span> <span class="exp-location">{edu['location']}</span>
                </div>
                <div class="exp-dates">{edu['dates']}</div>
            </div>
        </article>
""")

    html_parts.append("""
    </section>
</main>

</body>
</html>
""")

    return "".join(html_parts)

def main():
    data = parse_resume()
    html_content = generate_html(data)
    with open(OUTPUT_HTML, 'w', encoding='utf-8') as f:
        f.write(html_content)
    print(f"Generated clean modern HTML at {OUTPUT_HTML}")

if __name__ == "__main__":
    main()
