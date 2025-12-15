# Signal Systems & Addons

> **Multidimensional content scoring without economic tampering.**

## 📡 What is a Signal?

In QFS, a "Signal" is a pure-function evaluation of content quality, context, or community reception. Signals are **advisory**. They do not move money directly. They output normalized scores that the **Economics Engine** filters through **Policy** to determine rewards.

## 🎭 The Humor Signal Addon

The first major signal implementation is the **HumorSignalAddon**, which measures comedic value across 7 dimensions.

### The 7 Dimensions

1. **Chronos:** Timing and pacing.
2. **Lexicon:** Wordplay and linguistic creativity.
3. **Surreal:** Absurdity and unexpectedness.
4. **Empathy:** Relatability and emotional resonance.
5. **Critique:** Satire and social commentary.
6. **Slapstick:** Physical or visual humor.
7. **Meta:** Self-referential or layered humor.

### Architecture

1. **Input:** Text Content + Ledger Context (Views, Laughs, Saves).
2. **Processing:** Deterministic Matrix Multiplication (Weights × Context).
3. **Output:** `SignalResult` (Vector + Confidence Score).

## 🛡️ Isolation

* **No Treasury Access:** Signal code cannot import `TreasuryEngine` or `TokenStateBundle`.
* **Bounded Output:** Scores are strictly normalized `[0, 1]`.
* **Deterministic:** Same input context → Same score, forever.

## 🔌 Creating New Signals

Developers can implement the `ISignalAddon` interface to add new signals (e.g., "Educational Value", "Scientific Rigor"). All new signals must pass the Zero-Sim test suite.
