import json
import os
import re
from pathlib import Path
import ollama
from datetime import datetime

# Auto-detect project root
PROJECT_ROOT = Path(__file__).parent.parent
DEMO_PATH = PROJECT_ROOT / "inputs/demos/demo_acme_fire_protection.txt"
ONBOARD_PATH = PROJECT_ROOT / "inputs/onboardings/onboarding_acme_fire_protection.txt"

def clean_json_response(text: str) -> str:
    """Remove any extra text/markdown and extract only the JSON part"""
    text = text.strip()
    # Remove markdown code blocks
    text = re.sub(r'```json\s*|\s*```', '', text)
    # Find the first { and last }
    start = text.find('{')
    end = text.rfind('}')
    if start != -1 and end != -1:
        text = text[start:end+1]
    return text

def call_ollama(prompt_template_path, input_text):
    with open(prompt_template_path, "r", encoding="utf-8") as f:
        prompt = f.read().replace("{{transcript}}", input_text)
    response = ollama.chat(model="llama3.2", messages=[{"role": "user", "content": prompt}])
    raw = response['message']['content'].strip()

    print("\n----- RAW LLM RESPONSE -----")
    print(raw)
    print("----- END RESPONSE -----\n")

    cleaned = clean_json_response(raw)
    return cleaned

def main():
    print(f"📍 Project root: {PROJECT_ROOT}")
    
    if not DEMO_PATH.exists() or not ONBOARD_PATH.exists():
        print("❌ Missing transcript files! Please create them as in previous steps.")
        return

    with open(DEMO_PATH, "r", encoding="utf-8") as f: demo_text = f.read()
    with open(ONBOARD_PATH, "r", encoding="utf-8") as f: onboard_text = f.read()

    print("\n🔄 Generating v1 from demo call...")
    memo_v1_str = call_ollama(PROJECT_ROOT / "prompts/memo-extractor.txt", demo_text)
    memo_v1 = json.loads(memo_v1_str)
    
    agent_v1_str = call_ollama(PROJECT_ROOT / "prompts/agent-spec-generator.txt", memo_v1_str)
    agent_v1 = json.loads(agent_v1_str)   # now cleaned

    account_id = memo_v1["account_id"]
    v1_folder = PROJECT_ROOT / f"outputs/accounts/{account_id}/v1"
    v1_folder.mkdir(parents=True, exist_ok=True)

    json.dump(memo_v1, open(v1_folder / "memo.json", "w"), indent=2)
    json.dump(agent_v1, open(v1_folder / "agent-spec.json", "w"), indent=2)
    print(f"✅ v1 created for {account_id}")

    print("\n🔄 Generating v2 from onboarding call...")
    memo_v2_str = call_ollama(PROJECT_ROOT / "prompts/memo-extractor.txt", onboard_text)
    memo_v2 = json.loads(memo_v2_str)
    merged_memo = {**memo_v1, **memo_v2}

    agent_v2_str = call_ollama(PROJECT_ROOT / "prompts/agent-spec-generator.txt", json.dumps(merged_memo))
    agent_v2_str = agent_v2_str.replace('"version": "v1"', '"version": "v2"')
    agent_v2 = json.loads(agent_v2_str)

    v2_folder = PROJECT_ROOT / f"outputs/accounts/{account_id}/v2"
    v2_folder.mkdir(parents=True, exist_ok=True)

    json.dump(merged_memo, open(v2_folder / "memo.json", "w"), indent=2)
    json.dump(agent_v2, open(v2_folder / "agent-spec.json", "w"), indent=2)

    changelog = f"# Changelog for {account_id}\n\n## v2 - {datetime.now():%Y-%m-%d %H:%M}\n- Updated from onboarding call\n- Business hours, address, emergency routing, and constraints confirmed\n- v1 data preserved where not overridden"
    (v2_folder / "changelog.md").write_text(changelog)
    print(f"✅ v2 + changelog created!")

    print("\n🎉 SUCCESS! Open the outputs/ folder to see everything.")

if __name__ == "__main__":
    main()