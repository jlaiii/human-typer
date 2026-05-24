# Human Typer

**Type like a human. Fool the bots.**

[![Website](https://img.shields.io/badge/website-jlaiii.github.io%2Fhuman--typer-58a6ff)](https://jlaiii.github.io/human-typer/)

A Python GUI tool that types text for you with realistic human-like keystroke patterns — variable timing, natural hesitations, realistic mistakes, and anti-detection features to bypass automated bot/tracker detection in browsers and applications.

![Python](https://img.shields.io/badge/python-3.8+-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Platform](https://img.shields.io/badge/platform-Windows-lightgrey)

---

## Features

- **5 skill modes** — Beginner (~30 WPM), Average (~61 WPM), Expert (~88 WPM), Pro (~107 WPM)
- **Human-like typing engine** — variable inter-key delays, speed bursts, mid-word hesitation, sentence pauses
- **Realistic mistakes** — nearby-key typos, word-start fumbles, double-tap errors
- **&ldquo;Leave mistakes&rdquo; toggle** — skip backspace corrections so errors stay (like a real person)
- **Anti-detection** — variable key hold duration, warmup period, speed drift, per-keystroke jitter
- **No console** — hides terminal window automatically; `.pyw` extension
- **Dark GUI** — built with customtkinter

## Installation

```bash
pip install customtkinter keyboard
```

## Usage

```bash
pythonw human_typer.pyw
```

Or double-click `human_typer.pyw`.

1. Paste or type your text into the box
2. Select a mode (Beginner / Average / Expert / Pro / Bot)
3. Toggle &ldquo;Leave mistakes&rdquo; on/off
4. Click **Type It** — a 5-second countdown starts
5. Switch to your target window
6. The text types out with human-like cadence

Press **Esc** or click **Stop** to cancel at any time.

## Mode Breakdown

| Mode | Speed | Typo Rate | Hesitation | Notes |
|---|---|---|---|---|
| Beginner | ~30 WPM | 7.0% | 16% | Heavy pauses, many corrections |
| Average | ~61 WPM | 3.5% | 7% | Everyday typing |
| Expert | ~88 WPM | 1.8% | 3% | Skilled professional |
| Pro | ~107 WPM | 0.7% | 1.2% | Competitive typist |

## How It Works

Instead of pasting or injecting text, Human Typer sends actual keyboard events via the `keyboard` library. Each keystroke uses `press()` → realistic hold duration → `release()`, creating genuine keydown/keyup event pairs that are indistinguishable from physical typing at the OS level.

Bot detection scripts that analyze timing intervals, error rates, and key hold durations will see patterns consistent with human input.

## Requirements

- Python 3.8+
- Windows (keyboard library is Windows-focused)
- `customtkinter` — GUI framework
- `keyboard` — keystroke simulation

## License

MIT — see [LICENSE](LICENSE)

---

Made by [jlaiii](https://github.com/jlaiii)
