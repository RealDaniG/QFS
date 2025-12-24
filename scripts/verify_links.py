import re
import os
import urllib.parse


def check_links(readme_path):
    base_dir = os.path.dirname(readme_path)
    with open(readme_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Regex for [label](url)
    links = re.findall(r"\[([^\]]+)\]\(([^)]+)\)", content)

    print(f"Checking {len(links)} links in {readme_path}...")

    broken_links = []
    prompt_links = []

    for label, target in links:
        # Skip external links
        if target.startswith("http"):
            continue

        # Check for Prompts
        if "PROMPT" in target.upper() or "PROMPT" in label.upper():
            prompt_links.append((label, target))

        # Check file existence
        # Handle anchors
        file_target = target.split("#")[0]
        if not file_target:
            continue

        full_path = os.path.join(base_dir, file_target)
        # unquote for spaces
        full_path = urllib.parse.unquote(full_path)

        if not os.path.exists(full_path):
            broken_links.append((label, target))
            print(f"[BROKEN] {label} -> {target}")
        else:
            print(f"[OK] {label} -> {target}")

    return broken_links, prompt_links


if __name__ == "__main__":
    broken, prompts = check_links(
        "d:/AI AGENT CODERV1/QUANTUM CURRENCY/QFS/V13/README.md"
    )

    if prompts:
        print("\n--- PROMPT LINKS FOUND (must remove) ---")
        for l, t in prompts:
            print(f"{l} -> {t}")

    if broken:
        print("\n--- BROKEN LINKS FOUND ---")
        for l, t in broken:
            print(f"{l} -> {t}")

    if not broken and not prompts:
        print("\nAll checks passed.")
