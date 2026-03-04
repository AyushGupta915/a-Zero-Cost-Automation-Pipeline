# Clara AI – Zero-Cost Onboarding Automation Pipeline

Built by **Ayush Gupta**

---

# Overview

This project automates the Clara AI onboarding workflow using **local AI models and automation tools**.

The system converts call transcripts into structured onboarding data and generates **Retell AI agent specifications automatically**.

The pipeline processes:

• Demo call transcripts → **Account Memo + Agent Spec (v1)**
• Onboarding call transcripts → **Updated Memo + Agent Spec (v2) + Changelog**

The entire system runs **locally with zero API cost** using Ollama.

---

# Architecture

Pipeline flow:

```
n8n Workflow
      ↓
Flask API Trigger
      ↓
Batch Runner (Python)
      ↓
Ollama LLM (Llama 3.2)
      ↓
Memo Extraction
      ↓
Agent Spec Generation
      ↓
Versioned Outputs
```

---

# Folder Structure

```
a-Zero-Cost-Automation-Pipeline
│
├── inputs
│   ├── demos
│   │   ├── demo_acme_fire_protection.txt
│   │   ├── demo_apex_hvac.txt
│   │   ├── demo_elite_electrical.txt
│   │   ├── demo_guardian_alarm.txt
│   │   └── demo_swift_sprinkler.txt
│   │
│   └── onboardings
│       ├── onboarding_acme_fire_protection.txt
│       ├── onboarding_apex_hvac.txt
│       ├── onboarding_elite_electrical.txt
│       ├── onboarding_guardian_alarm.txt
│       └── onboarding_swift_sprinkler.txt
│
├── prompts
│   ├── memo-extractor.txt
│   └── agent-spec-generator.txt
│
├── outputs
│   └── accounts
│       ├── acme_fire_protection
│       ├── apex_hvac
│       ├── elite_electrical
│       ├── guardian_alarm
│       └── swift_sprinkler
│
├── scripts
│   ├── batch_runner.py
│   └── flask_api.py
│
├── clara-n8n-only.json
└── README.md
```

---

# How the Pipeline Works

### Step 1 – Demo Call Processing

Demo transcripts are processed first.

The system:

1. Reads demo transcripts
2. Extracts structured data using the **Memo Extractor prompt**
3. Generates a **Retell Agent Specification**
4. Saves the results as **Version 1**

Output:

```
outputs/accounts/<account_id>/v1/
memo.json
agent-spec.json
```

---

### Step 2 – Onboarding Call Processing

Onboarding transcripts update the account configuration.

The system:

1. Extracts new information
2. Merges it with the existing memo
3. Generates **Version 2 agent spec**
4. Creates a changelog

Output:

```
outputs/accounts/<account_id>/v2/
memo.json
agent-spec.json
changelog.md
```

---

# Running the Project

## 1. Install Python Dependencies

```
pip install flask ollama
```

---

# 2. Install Ollama

Download Ollama:

https://ollama.com

---

# 3. Download the LLM Model

```
ollama pull llama3.2
```

Verify:

```
ollama list
```

---

# 4. Start Ollama

```
ollama serve
```

---

# 5. Start the Flask API

From the project root:

```
python scripts/flask_api.py
```

The API will run on:

```
http://127.0.0.1:5000
```

---

# 6. Test the API

Check if the API is running:

```
http://127.0.0.1:5000/health
```

Expected response:

```
{"status":"Clara API running"}
```

---

# 7. Run the Pipeline

You can run the pipeline in two ways.

### Option 1 – Direct Execution

```
python scripts/batch_runner.py
```

This processes all transcripts immediately.

---

### Option 2 – Via n8n

1. Start n8n
2. Import the workflow `clara-n8n-only.json`
3. Run the workflow
4. It triggers:

```
http://127.0.0.1:5000/run_clara
```

---

# Generated Outputs

Example output structure:

```
outputs/accounts/apex_hvac/

v1/
memo.json
agent-spec.json

v2/
memo.json
agent-spec.json
changelog.md
```

Each company receives a **versioned AI agent configuration**.

---

# Prompt Design

Two prompts power the system.

### Memo Extractor

Strict JSON extractor that converts transcripts into structured account data.

Extracts:

• Company name
• Business hours
• Services supported
• Emergency routing rules
• Call transfer policies
• Integration constraints

---

### Agent Spec Generator

Generates a **Retell AI voice agent configuration** including:

• Business hours flow
• After-hours emergency flow
• Call transfer protocol
• Fallback handling

The system ensures **strict prompt hygiene**:

• No hallucinated fields
• Only transcript-derived data
• Exact call-flow requirements

---

# Technologies Used

Python
Ollama (Llama 3.2)
Flask API
n8n Automation
JSON-based data storage

All components run **locally with zero API cost**.

---

# Known Limitations

• Uses text transcripts instead of audio
• No direct Retell API integration
• Outputs require manual import into Retell

---

# Future Improvements

With additional resources this system could include:

• Automatic transcription from call recordings
• Retell API integration
• Real-time webhook processing
• Dashboard for viewing generated agents
• Database-backed storage

---

# Author

Ayush Gupta

Clara AI Automation Pipeline – Technical Assignment
