#!/usr/bin/env python3
"""
masao_check.py — Skill quality checker (8-dimension scoring)

Usage:
    python3 masao_check.py <skill-path>          # Single skill
    python3 masao_check.py --all                  # All skills in ~/.claude/skills/
    python3 masao_check.py --all --json           # JSON output for batch
"""

import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import yaml

# --- Constants ---

SKILLS_DIR = Path.home() / ".claude" / "skills"
QUICK_VALIDATE = SKILLS_DIR / ".system" / "skill-creator" / "scripts" / "quick_validate.py"

DIMENSIONS = [
    {"id": 1, "name": "Trigger Precision", "weight": 1.5},
    {"id": 2, "name": "Structure Balance", "weight": 1.0},
    {"id": 3, "name": "Metadata Completeness", "weight": 1.0},
    {"id": 4, "name": "Guardrails & Safety", "weight": 1.5},
    {"id": 5, "name": "Actionability", "weight": 1.0},
    {"id": 6, "name": "Reference Architecture", "weight": 1.0},
    {"id": 7, "name": "Terminology & Language", "weight": 0.5},
    {"id": 8, "name": "Error Handling", "weight": 1.0},
]

MAX_WEIGHTED = sum(3 * d["weight"] for d in DIMENSIONS)  # 25.5, capped to 24


# --- Helpers ---

def parse_frontmatter(content: str) -> Optional[dict]:
    """Extract YAML frontmatter from SKILL.md content."""
    match = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
    if not match:
        return None
    try:
        fm = yaml.safe_load(match.group(1))
        return fm if isinstance(fm, dict) else None
    except yaml.YAMLError:
        return None


def get_body(content: str) -> str:
    """Extract body (after frontmatter) from SKILL.md."""
    match = re.match(r"^---\n.*?\n---\n?(.*)", content, re.DOTALL)
    return match.group(1) if match else content


def count_triggers(description: str) -> int:
    """Count trigger keywords in description by splitting on commas."""
    if not description:
        return 0
    # Remove the leading purpose sentence(s) — triggers often follow "Triggers:" or "Use when"
    triggers_section = description
    for marker in ["Triggers:", "Use when user mentions", "Use when"]:
        idx = description.find(marker)
        if idx >= 0:
            triggers_section = description[idx:]
            break
    # Count comma-separated items
    parts = [p.strip() for p in triggers_section.split(",") if p.strip()]
    return len(parts)


def has_negative_triggers(description: str) -> bool:
    """Check for negative triggers (Do NOT / Do not load)."""
    return bool(re.search(r"Do\s+NOT|Do\s+not\s+load|Do\s+not\s+use", description, re.IGNORECASE))


def has_japanese(text: str) -> bool:
    """Check if text contains Japanese characters (hiragana, katakana, kanji)."""
    return bool(re.search(r"[\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FFF]", text))


def run_quick_validate(skill_path: Path) -> Tuple[bool, str]:
    """Run quick_validate.py and return (passed, message)."""
    if not QUICK_VALIDATE.exists():
        return True, "quick_validate.py not found, skipped"
    try:
        result = subprocess.run(
            [sys.executable, str(QUICK_VALIDATE), str(skill_path)],
            capture_output=True, text=True, timeout=10,
        )
        return result.returncode == 0, result.stdout.strip()
    except Exception as e:
        return False, f"Error running quick_validate: {e}"


# --- Dimension Checkers ---

def check_trigger_precision(fm: dict, body: str, skill_path: Path) -> dict:
    """Dimension 1: Trigger Precision (weight 1.5x)"""
    desc = fm.get("description", "")
    findings = []
    trigger_count = count_triggers(desc)
    neg_triggers = has_negative_triggers(desc)
    bilingual = has_japanese(desc)

    findings.append(f"Trigger count: {trigger_count}")
    findings.append(f"Negative triggers: {'yes' if neg_triggers else 'no'}")
    findings.append(f"Bilingual (JP): {'yes' if bilingual else 'no'}")

    # Auto-score
    if trigger_count == 0 or not desc.strip():
        score = 0
    elif trigger_count < 5 and not neg_triggers:
        score = 1
    elif trigger_count < 10:
        score = 2
    else:
        score = 3 if (neg_triggers and bilingual) else 2

    return {"score": score, "findings": findings}


def check_structure_balance(fm: dict, body: str, skill_path: Path) -> dict:
    """Dimension 2: Structure Balance (weight 1.0x)"""
    skill_md = skill_path / "SKILL.md"
    content = skill_md.read_text()
    line_count = len(content.splitlines())
    headings = len(re.findall(r"^#{1,3}\s+", content, re.MULTILINE))
    has_refs = (skill_path / "references").is_dir()

    findings = []
    findings.append(f"SKILL.md lines: {line_count}")
    findings.append(f"Headings count: {headings}")
    findings.append(f"references/ exists: {'yes' if has_refs else 'no'}")

    if line_count > 500 or headings == 0:
        score = 0
    elif line_count > 200 and not has_refs:
        score = 1
    elif line_count > 200 and has_refs:
        score = 2  # Splitting attempted but SKILL.md still long
    elif has_refs:
        score = 3 if headings >= 4 else 2
    else:
        score = 2 if headings >= 3 else 1

    return {"score": score, "findings": findings}


def check_metadata_completeness(fm: dict, body: str, skill_path: Path) -> dict:
    """Dimension 3: Metadata Completeness (weight 1.0x)"""
    has_tools = "allowed-tools" in fm
    metadata = fm.get("metadata", {})
    skillport = metadata.get("skillport", {}) if isinstance(metadata, dict) else {}
    has_category = "category" in skillport
    has_tags = "tags" in skillport
    has_always_apply = "alwaysApply" in skillport

    findings = []
    findings.append(f"allowed-tools: {'yes' if has_tools else 'no'}")
    findings.append(f"skillport.category: {'yes' if has_category else 'no'}")
    findings.append(f"skillport.tags: {'yes' if has_tags else 'no'}")
    findings.append(f"skillport.alwaysApply: {'yes' if has_always_apply else 'no'}")

    if not has_tools:
        score = 0
    elif not has_category and not has_tags:
        score = 1
    elif has_category and has_tags and has_always_apply:
        score = 3
    else:
        score = 2

    return {"score": score, "findings": findings}


def check_guardrails(fm: dict, body: str, skill_path: Path) -> dict:
    """Dimension 4: Guardrails & Safety (weight 1.5x)"""
    content = body.lower()
    guardrail_patterns = ["禁止", "forbidden", "guardrail", "ガードレール", "⚠️", "最優先"]
    found_patterns = [p for p in guardrail_patterns if p in content or p in body]

    has_guardrail_section = bool(re.search(
        r"^#{1,3}\s+.*(禁止|guardrail|ガードレール|safety|安全).*$",
        body, re.MULTILINE | re.IGNORECASE
    ))
    has_table = bool(re.search(r"^\|.*\|.*\|", body, re.MULTILINE))
    has_guardrail_table = has_guardrail_section and has_table

    findings = []
    findings.append(f"Guardrail keywords found: {found_patterns or 'none'}")
    findings.append(f"Dedicated section: {'yes' if has_guardrail_section else 'no'}")
    findings.append(f"Table format: {'yes' if has_guardrail_table else 'no'}")

    if not found_patterns:
        score = 0
    elif not has_guardrail_section:
        score = 1
    elif has_guardrail_table:
        score = 3
    else:
        score = 2

    return {"score": score, "findings": findings}


def check_actionability(fm: dict, body: str, skill_path: Path) -> dict:
    """Dimension 5: Actionability (weight 1.0x)"""
    code_blocks = len(re.findall(r"```", body))
    has_scripts = (skill_path / "scripts").is_dir()
    script_count = len(list((skill_path / "scripts").glob("*"))) if has_scripts else 0

    findings = []
    findings.append(f"Code blocks: {code_blocks // 2}")
    findings.append(f"scripts/ dir: {'yes' if has_scripts else 'no'}")
    if has_scripts:
        findings.append(f"Script files: {script_count}")

    # AI judgment needed for "defaults" and "step-by-step" quality
    if code_blocks == 0 and not has_scripts:
        score = 0
    elif code_blocks >= 2 and has_scripts and script_count > 0:
        score = 3
    elif code_blocks >= 2 or has_scripts:
        score = 2
    else:
        score = 1

    return {"score": score, "findings": findings}


def check_reference_architecture(fm: dict, body: str, skill_path: Path) -> dict:
    """Dimension 6: Reference Architecture (weight 1.0x)"""
    refs_dir = skill_path / "references"
    has_refs = refs_dir.is_dir()
    skill_md = skill_path / "SKILL.md"
    content = skill_md.read_text()
    line_count = len(content.splitlines())

    findings = []

    if has_refs:
        ref_files = list(refs_dir.glob("*"))
        findings.append(f"references/ files: {len(ref_files)}")

        # Check nesting depth
        nested = [f for f in refs_dir.rglob("*") if f.is_file() and f.parent != refs_dir]
        if nested:
            findings.append(f"WARNING: Nested files found: {[str(f.relative_to(refs_dir)) for f in nested]}")

        # Check internal links — extract clean filenames from markdown links
        ref_links_raw = re.findall(r"references/([^\s\)\]\"'`]+)", content)
        # Clean up any trailing markdown artifacts
        ref_links = [link.rstrip(")].") for link in ref_links_raw]
        # Deduplicate
        ref_links = list(dict.fromkeys(ref_links))
        broken = [link for link in ref_links if not (refs_dir / link).exists()]
        if broken:
            findings.append(f"Broken references: {broken}")
        else:
            findings.append(f"Internal links: all valid ({len(ref_links)} found)")

        # Check for navigation table
        has_nav = bool(re.search(r"リソース|resources|参照", content, re.IGNORECASE))
        findings.append(f"Navigation section: {'yes' if has_nav else 'no'}")

        if nested:
            score = 1
        elif has_nav and len(ref_files) > 0 and not broken:
            score = 3
        else:
            score = 2
    else:
        findings.append("references/ does not exist")
        if line_count > 200:
            findings.append(f"SKILL.md is {line_count} lines — consider splitting")
            score = 0
        else:
            score = 1

    return {"score": score, "findings": findings}


def check_terminology(fm: dict, body: str, skill_path: Path) -> dict:
    """Dimension 7: Terminology & Language (weight 0.5x)"""
    full_content = (skill_path / "SKILL.md").read_text()
    findings = []

    # Check for TODO/FIXME/HACK
    todos = re.findall(r"\b(TODO|FIXME|HACK|XXX)\b", full_content)
    if todos:
        findings.append(f"Found markers: {todos}")
    else:
        findings.append("No TODO/FIXME/HACK found")

    # Check for time-dependent info
    time_patterns = re.findall(r"(最新|現在|今年|202[0-9]年|latest\s+version)", full_content, re.IGNORECASE)
    if time_patterns:
        findings.append(f"Time-dependent terms: {time_patterns}")
    else:
        findings.append("No time-dependent terms found")

    # Check bilingual quality
    jp_in_body = has_japanese(body)
    findings.append(f"Japanese in body: {'yes' if jp_in_body else 'no'}")

    # Score (partial — AI judgment needed for full assessment)
    if todos:
        score = 0
    elif time_patterns:
        score = 1
    elif jp_in_body:
        score = None  # Needs AI judgment for consistency quality
    else:
        score = None  # Needs AI judgment

    return {"score": score, "findings": findings}


def check_error_handling(fm: dict, body: str, skill_path: Path) -> dict:
    """Dimension 8: Error Handling (weight 1.0x)"""
    content_lower = body.lower()
    error_patterns = ["エラー", "error", "troubleshoot", "トラブル", "fallback", "フォールバック"]
    found = [p for p in error_patterns if p in content_lower or p in body]

    has_error_section = bool(re.search(
        r"^#{1,3}\s+.*(エラー|error|troubleshoot|トラブル).*$",
        body, re.MULTILINE | re.IGNORECASE
    ))
    has_error_table = has_error_section and bool(re.search(
        r"^\|.*(?:症状|原因|対処|error|cause|fix).*\|",
        body, re.MULTILINE | re.IGNORECASE
    ))

    findings = []
    findings.append(f"Error keywords found: {found or 'none'}")
    findings.append(f"Dedicated section: {'yes' if has_error_section else 'no'}")
    findings.append(f"Error table: {'yes' if has_error_table else 'no'}")

    if not found:
        score = 0
    elif not has_error_section:
        score = 1
    elif has_error_table:
        score = 3
    else:
        score = 2

    return {"score": score, "findings": findings}


# --- Main Logic ---

def check_skill(skill_path: Path) -> dict:
    """Run all checks on a single skill and return results."""
    skill_md = skill_path / "SKILL.md"
    if not skill_md.exists():
        return {"error": f"SKILL.md not found at {skill_path}", "skill": skill_path.name}

    content = skill_md.read_text()
    fm = parse_frontmatter(content)
    if fm is None:
        return {"error": "Failed to parse frontmatter", "skill": skill_path.name}

    body = get_body(content)

    # Run quick_validate first
    qv_passed, qv_message = run_quick_validate(skill_path)

    checkers = [
        check_trigger_precision,
        check_structure_balance,
        check_metadata_completeness,
        check_guardrails,
        check_actionability,
        check_reference_architecture,
        check_terminology,
        check_error_handling,
    ]

    results = []
    total_weighted = 0.0
    has_null = False

    for dim, checker in zip(DIMENSIONS, checkers):
        result = checker(fm, body, skill_path)
        score = result["score"]
        weight = dim["weight"]
        weighted = round(score * weight, 1) if score is not None else None

        if score is not None:
            total_weighted += weighted
        else:
            has_null = True

        results.append({
            "id": dim["id"],
            "name": dim["name"],
            "weight": weight,
            "score": score,
            "max_score": 3,
            "weighted": weighted,
            "findings": result["findings"],
        })

    # Grade calculation (cap at 24)
    capped_max = 24.0
    if has_null:
        grade = "?"
        grade_label = "Incomplete (AI judgment needed)"
    else:
        total = min(total_weighted, capped_max)
        if total >= 22:
            grade, grade_label = "S", "Excellent"
        elif total >= 18:
            grade, grade_label = "A", "Good"
        elif total >= 14:
            grade, grade_label = "B", "Acceptable"
        elif total >= 10:
            grade, grade_label = "C", "Needs Work"
        else:
            grade, grade_label = "D", "Poor"

    return {
        "skill": skill_path.name,
        "path": str(skill_path),
        "quick_validate": {"passed": qv_passed, "message": qv_message},
        "dimensions": results,
        "total_weighted": round(total_weighted, 1),
        "max_weighted": capped_max,
        "grade": grade,
        "grade_label": grade_label,
    }


def get_all_skill_paths() -> List[Path]:
    """Get all skill directories (excluding .system and symlinks)."""
    if not SKILLS_DIR.is_dir():
        return []
    paths = []
    for p in sorted(SKILLS_DIR.iterdir()):
        if p.is_dir() and not p.name.startswith(".") and not p.is_symlink():
            if (p / "SKILL.md").exists():
                paths.append(p)
    return paths


def print_batch_summary(results: List[dict]):
    """Print a summary table for batch mode."""
    print("\n## Masao Batch Summary\n")
    print("| # | Skill | Grade | Score | Key Issue |")
    print("|---|-------|-------|-------|-----------|")

    # Sort by grade (S > A > B > C > D > ?)
    grade_order = {"S": 0, "A": 1, "B": 2, "C": 3, "D": 4, "?": 5}
    sorted_results = sorted(results, key=lambda r: (grade_order.get(r.get("grade", "?"), 5), r.get("skill", "")))

    for i, r in enumerate(sorted_results, 1):
        if "error" in r:
            print(f"| {i} | {r['skill']} | ERR | - | {r['error']} |")
            continue

        # Find lowest-scoring dimension for "key issue"
        dims = r.get("dimensions", [])
        scorable = [d for d in dims if d["score"] is not None]
        key_issue = ""
        if scorable:
            worst = min(scorable, key=lambda d: d["score"])
            if worst["score"] < 3:
                key_issue = f"{worst['name']}: {worst['score']}/3"

        grade = r.get("grade", "?")
        total = r.get("total_weighted", 0)
        max_w = r.get("max_weighted", 24)
        print(f"| {i} | {r['skill']} | {grade} | {total}/{max_w} | {key_issue} |")

    print(f"\nTotal skills checked: {len(results)}")


def main():
    args = sys.argv[1:]

    if not args:
        print("Usage:")
        print("  python3 masao_check.py <skill-path>")
        print("  python3 masao_check.py --all [--json]")
        sys.exit(1)

    json_output = "--json" in args
    batch_mode = "--all" in args

    if batch_mode:
        paths = get_all_skill_paths()
        if not paths:
            print("No skills found in ~/.claude/skills/")
            sys.exit(1)

        results = [check_skill(p) for p in paths]

        if json_output:
            print(json.dumps(results, ensure_ascii=False, indent=2))
        else:
            print_batch_summary(results)
    else:
        skill_path = Path(args[0]).expanduser().resolve()
        if not skill_path.is_dir():
            print(f"Error: {skill_path} is not a directory")
            sys.exit(1)

        result = check_skill(skill_path)
        print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
