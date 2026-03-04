import json
import re
from pathlib import Path
import ollama
from datetime import datetime
from multiprocessing import Pool

PROJECT_ROOT = Path(__file__).resolve().parents[1]

# LOAD PROMPTS GLOBALLY (IMPORTANT FOR MULTIPROCESSING)
memo_prompt = (PROJECT_ROOT / "prompts/memo-extractor.txt").read_text(encoding="utf-8")
agent_prompt = (PROJECT_ROOT / "prompts/agent-spec-generator.txt").read_text(encoding="utf-8")


def clean_json_response(text: str) -> str:
    text = text.strip()
    text = re.sub(r'```json\s*|\s*```', '', text)
    start = text.find('{')
    end = text.rfind('}')
    if start != -1 and end != -1:
        text = text[start:end+1]
    return text

def generate_changelog(old, new):
    changes = []

    for key in new:
        if key not in old:
            changes.append(f"Added {key}")
        elif old[key] != new[key]:
            changes.append(f"Updated {key}")

    if not changes:
        changes.append("No structural changes detected")

    return changes

def get_account_id(filename):
    return filename.replace("demo_", "").replace("onboarding_", "").replace(".txt", "").lower().replace(" ", "_").replace("-", "_")


def process_demo(demo_path):

    try:
        print(f"\nProcessing DEMO: {demo_path.name}", flush=True)

        text = demo_path.read_text(encoding="utf-8")

        memo_str = ollama.chat(
            model="llama3.2",
            messages=[{
                "role": "user",
                "content": memo_prompt.replace("{{transcript}}", text)
            }],
            format="json"
        )['message']['content']

        memo = json.loads(clean_json_response(memo_str))

        account_id = get_account_id(demo_path.name)
        memo["account_id"] = account_id

        agent_str = ollama.chat(
            model="llama3.2",
            messages=[{
                "role": "user",
                "content": agent_prompt.replace("{{transcript}}", json.dumps(memo))
            }],
            format="json"
        )['message']['content']

        agent = json.loads(clean_json_response(agent_str))
        agent["version"] = "v1"

        v1_folder = PROJECT_ROOT / f"outputs/accounts/{account_id}/v1"
        v1_folder.mkdir(parents=True, exist_ok=True)

        with open(v1_folder / "memo.json", "w", encoding="utf-8") as f:
            json.dump(memo, f, indent=2)

        with open(v1_folder / "agent-spec.json", "w", encoding="utf-8") as f:
            json.dump(agent, f, indent=2)

        print(f"✅ DEMO COMPLETE → {account_id}", flush=True)

    except Exception as e:
        print(f"❌ DEMO FAILED {demo_path.name}: {e}", flush=True)


def process_onboarding(onboard_path):

    try:
        print(f"\nProcessing ONBOARDING: {onboard_path.name}", flush=True)

        text = onboard_path.read_text(encoding="utf-8")

        memo_str = ollama.chat(
            model="llama3.2",
            messages=[{
                "role": "user",
                "content": memo_prompt.replace("{{transcript}}", text)
            }],
            format="json"
        )['message']['content']

        memo_v2 = json.loads(clean_json_response(memo_str))

        account_id = get_account_id(onboard_path.name)
        memo_v2["account_id"] = account_id

        v1_path = PROJECT_ROOT / f"outputs/accounts/{account_id}/v1/memo.json"

        if v1_path.exists():
            with open(v1_path) as f:
                memo_v1 = json.load(f)
            merged = {**memo_v1, **memo_v2}
        else:
            merged = memo_v2

        agent_str = ollama.chat(
            model="llama3.2",
            messages=[{
                "role": "user",
                "content": agent_prompt.replace("{{transcript}}", json.dumps(merged))
            }],
            format="json"
        )['message']['content']

        agent_v2 = json.loads(clean_json_response(agent_str))
        agent_v2["version"] = "v2"

        v2_folder = PROJECT_ROOT / f"outputs/accounts/{account_id}/v2"
        v2_folder.mkdir(parents=True, exist_ok=True)

        with open(v2_folder / "memo.json", "w", encoding="utf-8") as f:
            json.dump(merged, f, indent=2)

        with open(v2_folder / "agent-spec.json", "w", encoding="utf-8") as f:
            json.dump(agent_v2, f, indent=2)

        changes = generate_changelog(memo_v1 if v1_path.exists() else {}, merged)

        changelog = "# Changelog\n\n"
        changelog += f"## v2 - {datetime.now():%Y-%m-%d %H:%M}\n\n"

        for c in changes:
            changelog += f"- {c}\n"

        with open(v2_folder / "changelog.md", "w", encoding="utf-8") as f:
            f.write(changelog)

        print(f"✅ ONBOARDING COMPLETE → {account_id}", flush=True)

    except Exception as e:
        print(f"❌ ONBOARD FAILED {onboard_path.name}: {e}", flush=True)


if __name__ == "__main__":

    print("=== CLARA BATCH STARTED ===", flush=True)
    print("Project root:", PROJECT_ROOT, flush=True)

    demo_files = sorted((PROJECT_ROOT / "inputs/demos").glob("*.txt"))
    onboard_files = sorted((PROJECT_ROOT / "inputs/onboardings").glob("*.txt"))

    print(f"Found {len(demo_files)} demo files and {len(onboard_files)} onboarding files", flush=True)

    print("\n🚀 Running DEMO batch", flush=True)

    with Pool(2) as pool:
        pool.map(process_demo, demo_files)

    print("\n🚀 Running ONBOARDING batch", flush=True)

    with Pool(2) as pool:
        pool.map(process_onboarding, onboard_files)

    print("\n🎉 CLARA BATCH COMPLETE!", flush=True)