# -BlastShield-AI
# 🛡️ BlastShield AI

> **Every code change has a blast radius. BlastShield finds it before your users do.**

BlastShield AI is an autonomous **Software Quality Engineering agent** built for the **Sebaka Testing AI Hackathon 2026**.

## 🎯 Problem

Small code changes can unexpectedly break functionality, performance, or security. Developers often don't know exactly what should be retested after each change.

## 💡 Solution

BlastShield analyses a **Git diff**, understands what changed, predicts what could break, and automatically selects and runs the most relevant tests.

```text
Code Change
    ↓
AI Analyses Git Diff
    ↓
Predicts Blast Radius
    ↓
Classifies Risk
    ↓
Functional | Performance | Security
    ↓
Selects / Generates Tests
    ↓
Runs Tests
    ↓
Returns Evidence
