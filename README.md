# TalentIQ × Eightfold AI
### Internal Talent Intelligence Platform

Built at the IIT Kanpur Techkriti’26 × Eightfold AI Hackathon  
🏆 1st Place Winner

---

## Overview

TalentIQ is an AI-powered internal talent intelligence platform designed to rethink hiring beyond static resumes and keyword matching.

Instead of relying on traditional ATS systems, TalentIQ evaluates:
- verified engineering activity
- skill adjacency and learning velocity
- GitHub contribution signals
- explainable weighted scoring

The platform helps organizations discover hidden internal talent before opening external hiring pipelines.

Built in just **6 hours** during the hackathon.

---

# Problem Statement

Modern hiring systems fail because:
- AI-generated resumes create noisy applications
- Internal talent remains undiscovered
- Skills evolve faster than static job descriptions
- Black-box AI scoring lacks transparency

The challenge by Eightfold AI:
> Build an AI-powered Talent Intelligence system that verifies capability, predicts learning trajectories, and surfaces hidden internal talent.

---

# Key Features

## Skill Adjacency Graph
Missing skills are treated as *learning distance*, not rejection.

Examples:
- Docker → Kubernetes
- SQL → Spark
- PyTorch → TensorFlow
- FastAPI → gRPC

Partial matching enables intelligent internal mobility recommendations.

---

## GitHub Capability Verification

Instead of trusting resumes alone, TalentIQ uses:
- commit activity
- active programming languages
- open-source PR contributions

to validate practical engineering capability.

---

## Explainable Scoring Engine

Every score is fully auditable.

### Final Score Formula

```python
FINAL_SCORE =
Skill Match (0–70)
+ Semantic Alignment (0–15)
+ GitHub Boost (0–15)
```

No black-box ranking models.

---

## Bias-Resistant Evaluation

The scoring engine explicitly ignores:
- gender
- university tier
- age
- demographics

Anonymous scoring checks ensure fairness consistency.

---

## Dual Portal System

### Employee Portal
- Role recommendations
- Skill gap analysis
- One-click applications
- Learning roadmap

### Admin Portal
- Candidate discovery
- Explainability waterfall
- Analytics dashboard
- Skill gap matrix
- Diversity insights

---

# Technical Architecture

## 1. Signal Extraction Layer
- GitHub commits
- Active languages
- OSS pull requests
- Self-reported skills

## 2. Skill Adjacency Graph
- Graph traversal for adjacent skills
- Half-credit scoring for learnable transitions
- Time-to-learn estimation

## 3. Weighted Scoring Engine
- Skill match scoring
- Semantic alignment scoring
- GitHub credibility boost

## 4. LLM Integration Layer

Powered using:
- Groq API
- Llama 3.1 8B Instant

Used for:
- AI hiring recommendations
- Personalized outreach emails
- Plain-English explanations

---

# Tech Stack

| Component | Technology |
|---|---|
| Frontend | Streamlit |
| Core Logic | Python |
| LLM | Groq + Llama 3.1 |
| Scoring Engine | Pure Python |
| Skill Graph | Python Dictionary Graph |
| Deployment | Streamlit |

---

# Impact

- 🏆 1st Place Winner
- ⚡ Built in 6 hours
- 👥 18 employees scored
- 💼 3 role simulations
- 🔗 20 skill adjacency edges implemented
- 💰 Estimated ₹5L hiring savings per role
- 📈 Real-time explainable scoring in under 2 seconds

---

# Future Scope

## Phase 1
- Live GitHub API integration
- GitLab & Bitbucket support
- Jira productivity signals

## Phase 2
- PM and non-tech role support
- Figma activity scoring
- Stakeholder performance insights

## Phase 3
- Dynamic AI-learned skill adjacency graphs
- Workforce skill forecasting
- Personalized learning velocity prediction

---

# Achievement

🏆 Winner — Eightfold AI Hackathon at IIT Kanpur Techkriti’26  
💰 Prize: ₹75,000 + Meta AI Glasses

---

# Philosophy

> No resume. No keyword matching. No black box.

TalentIQ believes the best candidate for a role is often already inside the company — just undiscovered.
