#!/usr/bin/env python3
import os
import re
import json

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STANDARD_TEX = os.path.join(BASE_DIR, "standard", "ariel_paulin.tex")
OUTPUT_JSON = os.path.join(BASE_DIR, "standard", "ariel_paulin.json")
OUTPUT_TXT = os.path.join(BASE_DIR, "standard", "ariel_paulin.txt")

def strip_comments(text):
    lines = []
    for line in text.split('\n'):
        line_no_comment = re.sub(r'(?<!\\)%.*', '', line)
        lines.append(line_no_comment)
    return '\n'.join(lines)

def clean_latex(text):
    text = re.sub(r'\\textbf\{([^}]+)\}', r'\1', text)
    text = re.sub(r'\\textit\{([^}]+)\}', r'\1', text)
    text = re.sub(r'\\small\{([^}]+)\}', r'\1', text)
    text = re.sub(r'\\href\{[^}]+\}\{([^}]+)\}', r'\1', text)
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

    # Extract name
    name_match = re.search(r'\\Huge\s+([^}]+)\}', raw_content)
    name = name_match.group(1).strip() if name_match else "Ariel Paulin"

    # Extract contact info
    email_match = re.search(r'href\{mailto:([^}]+)\}', raw_content)
    email = email_match.group(1).strip() if email_match else ""

    linkedin_match = re.search(r'href\{https://www\.linkedin\.com/in/([^}]+)\}', raw_content)
    linkedin = f"https://www.linkedin.com/in/{linkedin_match.group(1).strip()}" if linkedin_match else ""

    github_match = re.search(r'href\{https://github\.com/([^}]+)\}', raw_content)
    github = f"https://github.com/{github_match.group(1).strip()}" if github_match else ""

    # Extract summary
    summary_match = re.search(r'\\begin\{quote\}(.*?)\\end\{quote\}', raw_content, re.DOTALL)
    summary = ""
    if summary_match:
        summary = clean_latex(summary_match.group(1))

    # Parse Experience
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

        start_date, end_date = dates.split('–') if '–' in dates else (dates, "")

        experience.append({
            "title": title,
            "company": company,
            "location": location,
            "start": start_date.strip(),
            "end": end_date.strip(),
            "bullets": bullets
        })

    # Parse Skills
    skills = {}
    skills_block_match = re.search(r'\\section\{Skills\}(.*?)(=\\section|\\section|\\end\{document\})', raw_content, re.DOTALL)
    if skills_block_match:
        skills_text = skills_block_match.group(1)
        for line in skills_text.split('\n'):
            if ':' in line and '\\textbf{' in line:
                cleaned_line = line.replace(r'\textbf{', '').replace(r'}', '')
                cleaned_line = cleaned_line.replace(r'\textbar', '|').replace(r'\quad', '')
                cleaned_line = cleaned_line.replace(r'\&', '&').replace(r'\\\\', '').replace(r'\\', '')
                cleaned_line = cleaned_line.strip()
                if ':' in cleaned_line:
                    parts = cleaned_line.split(':', 1)
                    key_raw = parts[0].strip()
                    val_raw = parts[1].strip()

                    key_map = {
                        "Languages": "languages",
                        "Frameworks & Libraries": "frameworks_and_libraries",
                        "Cloud & DevOps": "cloud_and_devops",
                        "Technical Leadership": "technical_leadership"
                    }

                    key = key_map.get(key_raw, key_raw.lower().replace(' ', '_').replace('&', 'and'))
                    raw_items = val_raw.split('|')
                    cleaned_items = []
                    for item in raw_items:
                        item_clean = clean_latex(item).replace('\\', '').strip()
                        if item_clean:
                            cleaned_items.append(item_clean)
                    skills[key] = cleaned_items

    # Parse Education
    education = []
    edu_block_match = re.search(r'\\section\{Education\}(.*?)(=\\section|\\section|\\end\{document\})', raw_content, re.DOTALL)
    if edu_block_match:
        edu_text = edu_block_match.group(1)
        for match in subheading_pattern.finditer(edu_text):
            inst = clean_latex(match.group(1))
            loc = clean_latex(match.group(2))
            degree = clean_latex(match.group(3))
            dates = clean_latex(match.group(4))

            start_date, end_date = dates.split('–') if '–' in dates else (dates, "")

            education.append({
                "institution": inst,
                "degree": degree,
                "location": loc,
                "start": start_date.strip(),
                "end": end_date.strip()
            })

    data = {
        "name": name,
        "contact": {
            "email": email,
            "linkedin": linkedin,
            "github": github
        },
        "summary": summary,
        "experience": experience,
        "skills": skills,
        "education": education
    }

    return data

def generate_txt(data):
    lines = []
    lines.append(data["name"])
    contact_parts = []
    if data["contact"]["email"]:
        contact_parts.append(data["contact"]["email"])
    if data["contact"]["linkedin"]:
        contact_parts.append(data["contact"]["linkedin"].replace("https://www.", "").replace("https://", ""))
    if data["contact"]["github"]:
        contact_parts.append(data["contact"]["github"].replace("https://", ""))
    lines.append(" | ".join(contact_parts))
    lines.append("")
    if data["summary"]:
        lines.append(data["summary"])
        lines.append("")

    lines.append("─────────────────────────────────────────")
    lines.append("EXPERIENCE")
    lines.append("─────────────────────────────────────────")
    lines.append("")

    for exp in data["experience"]:
        header_left = f"{exp['title']} | {exp['company']} | {exp['location']}"
        header_right = f"{exp['start']} – {exp['end']}"
        spaces = max(2, 80 - len(header_left) - len(header_right))
        lines.append(f"{header_left}{' ' * spaces}{header_right}")
        for b in exp["bullets"]:
            lines.append(f"  • {b}")
        lines.append("")

    lines.append("─────────────────────────────────────────")
    lines.append("SKILLS")
    lines.append("─────────────────────────────────────────")
    lines.append("")

    skill_titles = {
        "languages": "Languages:",
        "frameworks_and_libraries": "Frameworks & Libraries:",
        "cloud_and_devops": "Cloud & DevOps:",
        "technical_leadership": "Technical Leadership:"
    }

    for k, v in data["skills"].items():
        title = skill_titles.get(k, f"{k.replace('_', ' ').title()}:")
        val_str = " | ".join(v)
        lines.append(f"{title:<24}{val_str}")

    lines.append("")
    lines.append("─────────────────────────────────────────")
    lines.append("EDUCATION")
    lines.append("─────────────────────────────────────────")
    lines.append("")

    for edu in data["education"]:
        header_left = f"{edu['institution']} | {edu['degree']}"
        header_right = f"{edu['start']} – {edu['end']}"
        spaces = max(2, 80 - len(header_left) - len(header_right))
        lines.append(f"{header_left}{' ' * spaces}{header_right}")
        lines.append(edu["location"])

    return "\n".join(lines) + "\n"

def main():
    data = parse_resume()

    with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)

    txt_content = generate_txt(data)
    with open(OUTPUT_TXT, 'w', encoding='utf-8') as f:
        f.write(txt_content)

    print(f"Generated {OUTPUT_JSON} and {OUTPUT_TXT}")

if __name__ == "__main__":
    main()
