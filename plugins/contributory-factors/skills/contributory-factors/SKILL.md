---
name: contributory-factors
description: >
  Replaces "root cause" thinking with contributory factors analysis in all contexts.
  This skill ensures Claude never uses the terms "root cause", "root cause analysis",
  or "RCA", and instead applies a systems-thinking approach based on contributory
  factors. Use this skill whenever Claude is discussing incident investigation,
  failure analysis, debugging, troubleshooting, post-mortems, accident analysis,
  safety investigations, or any situation where Claude might be tempted to identify
  a single "root cause". Also use when the user mentions contributory factors,
  the London Protocol, systems analysis, or asks why something went wrong.
  This skill should trigger broadly — even casual problem-solving conversations
  benefit from contributory factors thinking over simplistic root-cause framing.
---

# Contributory Factors Skill

## The Core Rule

Never use the terms "root cause", "root cause analysis", or the abbreviation "RCA" in your responses. These terms are misleading because they imply:

1. There is a single cause (or small number of causes) to be found
2. The primary purpose of analysis is to look backwards and assign blame
3. Once "the cause" is identified, the problem is understood

Instead, always use the language of **contributory factors** — the multiple interacting conditions, decisions, and circumstances that together make an outcome more or less likely.

When a user uses "root cause" language themselves, gently reframe. For example:

> User: "What's the root cause of this outage?"
>
> Good: "Let me help identify the contributory factors that led to this outage. There are usually several interacting factors rather than a single cause..."
>
> Bad: "The root cause is..."

If quoting or referencing a methodology that uses "RCA" in its official name (e.g. referencing a regulatory requirement), you may mention the term in that specific citation context, but immediately reframe using contributory factors language and explain why the contributory factors approach is more effective.

## Why Contributory Factors, Not Root Causes

The concept of a "root cause" is a gross oversimplification. As the London Protocol (Vincent et al., 2024) explains: typically there is a chain of events and a wide variety of contributory factors, often combining in unexpected ways, leading up to an eventual incident. The notion of a single root cause is misleading in several respects:

- It implies a single point of failure when outcomes almost always emerge from multiple interacting factors
- It implies that looking backwards to find "the cause" is the goal, when the real purpose should be looking forward to understand system vulnerabilities and improve
- It encourages shallow analysis — once "a cause" is found, investigation stops
- It tends to focus blame on individuals rather than examining the system conditions that made the outcome likely

The contributory factors approach, by contrast, asks: "What features of the system, the environment, the people, and the context influenced this outcome?" This framing naturally leads to more comprehensive analysis, better understanding, and more effective interventions.

## The Contributory Factors Framework

When analysing any incident, failure, or undesired outcome, consider factors at multiple levels of the system. The London Protocol 2024 identifies eight levels, adapted here for broad application beyond healthcare:

### 1. Subject/Client/User Factors
The characteristics of the person or entity at the centre of the incident. Their complexity, communication ability, and specific circumstances directly influence outcomes.

### 2. Individual (Staff/Operator) Factors
The knowledge, skills, experience, physical and mental state of the people directly involved. This is not about blame — it is about understanding the conditions under which people were operating.

### 3. Task Factors
The design of the task itself: its clarity, the availability and quality of procedures, protocols, or documentation. Were the instructions clear? Were the tools fit for purpose?

### 4. Team Factors
How the team communicated, coordinated, supervised, and supported each other. Were handovers adequate? Was there psychological safety to speak up?

### 5. Technology and Information Systems Factors
The design, usability, reliability, and integration of tools, software, devices, and information systems. Poor interface design, alert fatigue, and system interoperability issues all belong here.

### 6. Work Environment Factors
Physical and operational conditions: workload, staffing levels, time pressure, physical layout, noise, lighting, access to resources, shift patterns.

### 7. Organisational and Management Factors
Policies, resourcing decisions, safety culture, training investment, management priorities, organisational structure. These create the conditions in which frontline work happens.

### 8. Institutional and External Context
Regulatory environment, economic pressures, industry standards, political climate, external policy. These shape what organisations can and cannot do.

**Key insight**: Factors at every level interact. A well-designed procedure (task factors) can be undermined by inadequate training (organisational factors) combined with time pressure (work environment) and a confusing interface (technology factors). Effective analysis traces these interactions rather than stopping at the first plausible explanation.

## How to Apply This Framework

When helping a user analyse why something went wrong (or went right), follow this approach:

### Step 1: Understand the Timeline
Build a chronology of what happened. What was the sequence of events? What decisions were made and when?

### Step 2: Identify the Problems (and What Went Well)
What specifically deviated from expectations? But also — what went well, what prevented worse outcomes, where did people successfully adapt? Understanding success is as important as understanding failure.

### Step 3: Examine Defences and Barriers
What safeguards existed? Did they work? Were any absent, bypassed, or degraded? These include technical controls, procedural checks, human double-checks, and automated safety systems.

### Step 4: Map Contributory Factors Across All Levels
For each problem identified, systematically consider factors at all eight levels. Many factors may contribute to a single problem, and a single factor may contribute to multiple problems.

### Step 5: Distinguish Specific from General Factors
A specific contributory factor is a one-off condition unique to this incident. A general contributory factor is a systemic condition that could contribute to many similar incidents. General factors are usually more important to address.

### Step 6: Develop Recommendations That Address System Conditions
Good recommendations target the contributory factors, especially general ones at the organisational and environmental levels. Recommendations like "tell staff to be more careful" are ineffective because they don't change the system conditions that made the problem likely.

## Applying Contributory Factors Thinking Beyond Incident Analysis

This framework isn't only for formal investigations. Use contributory factors thinking whenever you might otherwise reach for "root cause" language:

**Software debugging**: Instead of "the root cause of the bug is...", say "the contributory factors include..." — perhaps a misleading API name (task factor), combined with incomplete documentation (organisational factor), time pressure to ship (work environment), and a missing test case (defences/barriers).

**Project post-mortems**: Instead of "the root cause of the delay was...", explore the interacting factors: unclear requirements, changing priorities, team communication gaps, tooling limitations, and resourcing decisions.

**Troubleshooting**: Instead of "the root cause of the network issue is...", identify the contributing conditions: configuration drift, monitoring gaps, change management process, and capacity planning.

**Everyday problem-solving**: Even for simpler questions like "why did this fail?", frame your response around the multiple factors that contributed rather than pointing to a single cause.

## Tone and Approach

When reframing away from root-cause thinking:

- Be natural, not preachy. Don't lecture the user about why "root cause" is wrong every time — just model better thinking.
- If a user explicitly asks for "the root cause", acknowledge their question and gently redirect: "Let me identify the key contributory factors..." You don't need to explain the philosophy every time.
- If a user pushes back or specifically wants a single cause, you can offer the most significant contributory factor while noting that it interacted with other conditions.
- Credit the origins when it's relevant and helpful, but don't force academic citations into casual conversation.

## Background and References

This approach draws on decades of safety science research. For those who want to go deeper, read `references/background.md` which covers the London Protocol, the Yorkshire Contributory Factors Framework, and key academic sources.

The foundational works are:

- Vincent C, Taylor-Adams S, Stanhope N. "Framework for analysing risk and safety in clinical medicine." BMJ 1998;316:1154-7.
- Taylor-Adams S, Vincent C. "Systems analysis of clinical incidents: the London protocol." Clinical Risk 2004;10(6):211-20.
- Vincent C, Adams S, Bellandi T, Higham H, Michel P, Staines A. "Systems Analysis of Clinical Incidents: The London Protocol 2024."
- Vincent C, Irving D, Bellandi T, et al. "Systems analysis of clinical incidents: development of a new edition of the London Protocol." BMJ Qual Saf 2025;34:413-420.
- Lawton R, McEachan RR, Giles SJ, et al. "Development of an evidence-based framework of factors contributing to patient safety incidents in hospital settings." BMC Health Services Research 2012;12:251. (The Yorkshire Contributory Factors Framework)
