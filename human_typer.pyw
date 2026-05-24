import ctypes
import sys
import webbrowser

# hide console window (works regardless of .py/.pyw extension)
if sys.platform == "win32":
    ctypes.windll.user32.ShowWindow(
        ctypes.windll.kernel32.GetConsoleWindow(), 0
    )

import customtkinter as ctk
import keyboard
import time
import random
import threading

# ── config ──────────────────────────────────────────────
APPEARANCE = "dark"
FONT = ("Segoe UI", 13)
MONO_FONT = ("Consolas", 12)
COOLDOWN_SEC = 5
# ─────────────────────────────────────────────────────────


def _wpm_text(p):
    """estimate effective WPM from profile params"""
    ak = (p["key_min"] + p["key_max"]) / 2
    ah = ((p["hesitate_min"] + p["hesitate_max"]) / 2) * p["hesitate_chance"]
    aw = ((p["wp_min"] + p["wp_max"]) / 2) * p["wp_chance"] / 5
    as_ = ((p["sent_min"] + p["sent_max"]) / 2) / 50
    td = ak + ah + aw + as_
    if td <= 0.003:
        return "instant"
    return f"~{int(60 / td / 5)} WPM"


# ── mode profiles ───────────────────────────────────────
PROFILES = {
    "Beginner": {
        "key_min":      0.16,
        "key_max":      0.35,
        "hold_min":      0.06,
        "hold_max":      0.22,
        "burst_min":    1,
        "burst_max":    3,
        "hesitate_chance": 0.16,
        "hesitate_min": 0.3,
        "hesitate_max": 0.9,
        "sent_min":      0.5,
        "sent_max":      1.8,
        "wp_chance":     0.30,
        "wp_min":        0.12,
        "wp_max":        0.50,
        "typo_chance":      0.07,
        "typo_bsp_min":     0.10,
        "typo_bsp_max":     0.30,
        "word_typo_chance": 0.015,
        "speed_jitter":     0.5,
        "ramp_words":       2,
        "warmup_words":     4,
        "drift_factor":     0.25,
        "label": "Beginner  (slow)",
    },
    "Average": {
        "key_min":      0.09,
        "key_max":      0.22,
        "hold_min":      0.05,
        "hold_max":      0.16,
        "burst_min":    3,
        "burst_max":    6,
        "hesitate_chance": 0.07,
        "hesitate_min": 0.15,
        "hesitate_max": 0.55,
        "sent_min":      0.25,
        "sent_max":      0.9,
        "wp_chance":     0.13,
        "wp_min":        0.06,
        "wp_max":        0.25,
        "typo_chance":      0.035,
        "typo_bsp_min":     0.06,
        "typo_bsp_max":     0.18,
        "word_typo_chance": 0.005,
        "speed_jitter":     0.7,
        "ramp_words":       3,
        "warmup_words":     2,
        "drift_factor":     0.15,
        "label": "Average  (medium)",
    },
    "Expert": {
        "key_min":      0.07,
        "key_max":      0.17,
        "hold_min":      0.04,
        "hold_max":      0.12,
        "burst_min":    4,
        "burst_max":    10,
        "hesitate_chance": 0.03,
        "hesitate_min": 0.10,
        "hesitate_max": 0.35,
        "sent_min":      0.18,
        "sent_max":      0.6,
        "wp_chance":     0.07,
        "wp_min":        0.04,
        "wp_max":        0.16,
        "typo_chance":      0.018,
        "typo_bsp_min":     0.05,
        "typo_bsp_max":     0.14,
        "word_typo_chance": 0.002,
        "speed_jitter":     0.8,
        "ramp_words":       4,
        "warmup_words":     2,
        "drift_factor":     0.10,
        "label": "Expert  (fast)",
    },
    "Pro": {
        "key_min":      0.06,
        "key_max":      0.15,
        "hold_min":      0.03,
        "hold_max":      0.10,
        "burst_min":    5,
        "burst_max":    14,
        "hesitate_chance": 0.012,
        "hesitate_min": 0.06,
        "hesitate_max": 0.20,
        "sent_min":      0.10,
        "sent_max":      0.35,
        "wp_chance":     0.03,
        "wp_min":        0.02,
        "wp_max":        0.08,
        "typo_chance":      0.007,
        "typo_bsp_min":     0.04,
        "typo_bsp_max":     0.09,
        "word_typo_chance": 0.0,
        "speed_jitter":     0.85,
        "ramp_words":       5,
        "warmup_words":     1,
        "drift_factor":     0.06,
        "label": "Pro  (very fast)",
    },
}

# nearby-key maps — multiple alternatives per letter
_NEAR = {
    "a": ["s", "q", "w", "z"],
    "b": ["v", "n", "g", "h"],
    "c": ["x", "d", "v", "f"],
    "d": ["s", "f", "e", "c"],
    "e": ["w", "r", "d", "s"],
    "f": ["d", "g", "r", "c"],
    "g": ["f", "h", "t", "b"],
    "h": ["g", "j", "y", "n"],
    "i": ["o", "u", "k", "j"],
    "j": ["h", "k", "u", "m"],
    "k": ["j", "l", "i", "o"],
    "l": ["k", "p", "o"],
    "m": ["n", "j", "k"],
    "n": ["b", "m", "h", "j"],
    "o": ["i", "p", "l", "k"],
    "p": ["o", "l"],
    "q": ["w", "a", "s"],
    "r": ["t", "e", "f", "d"],
    "s": ["a", "d", "w", "x"],
    "t": ["r", "y", "g", "f"],
    "u": ["y", "i", "j", "h"],
    "v": ["c", "b", "f"],
    "w": ["q", "e", "s", "a"],
    "x": ["z", "c", "s", "d"],
    "y": ["t", "u", "h", "g"],
    "z": ["x", "a", "s"],
}
# flatten to one extra nearby key for the "leave mistakes" fat-finger
NEARBY_EXTRA = {k: v[0] for k, v in _NEAR.items()}


class HumanTyper:
    def __init__(self):
        self.running = False
        self.mode = "Average"
        self.leave_mistakes = False
        self.root = ctk.CTk()
        self.root.title("Human Typer")
        self.root.geometry("620x520")
        self.root.resizable(False, False)
        ctk.set_appearance_mode(APPEARANCE)

        # ── text label ──
        ctk.CTkLabel(self.root, text="Paste or type text below:", font=FONT).pack(
            pady=(15, 5)
        )

        # ── text box ──
        self.textbox = ctk.CTkTextbox(
            self.root, font=MONO_FONT, wrap="word", corner_radius=8, border_width=1
        )
        self.textbox.pack(fill="both", expand=True, padx=20, pady=(0, 10))

        # ── mode selector + toggle row ──
        ctrl_frame = ctk.CTkFrame(self.root, fg_color="transparent")
        ctrl_frame.pack(pady=(0, 6))

        # mode dropdown
        ctk.CTkLabel(ctrl_frame, text="Mode:", font=FONT).pack(side="left", padx=(0, 6))
        self.mode_var = ctk.StringVar(value=PROFILES["Average"]["label"])
        self.mode_menu = ctk.CTkOptionMenu(
            ctrl_frame,
            values=[p["label"] for p in PROFILES.values()],
            variable=self.mode_var,
            command=self._on_mode_change,
            font=FONT,
            corner_radius=6,
            width=190,
        )
        self.mode_menu.pack(side="left", padx=(0, 16))

        # leave-mistakes checkbox
        self.mistake_var = ctk.BooleanVar(value=False)
        self.mistake_cb = ctk.CTkCheckBox(
            ctrl_frame,
            text="Leave mistakes",
            variable=self.mistake_var,
            command=self._on_mistake_toggle,
            font=FONT,
            corner_radius=4,
        )
        self.mistake_cb.pack(side="left")

        # ── mode description ──
        self.mode_desc = ctk.CTkLabel(
            self.root, text="", font=("Segoe UI", 11), text_color="gray"
        )
        self.mode_desc.pack(pady=(0, 8))
        self._refresh_desc()

        # ── status ──
        self.status = ctk.CTkLabel(
            self.root, text="Ready.", font=FONT, text_color="gray"
        )
        self.status.pack(pady=(0, 10))

        # ── buttons ──
        btn_frame = ctk.CTkFrame(self.root, fg_color="transparent")
        btn_frame.pack(pady=(0, 15))

        self.type_btn = ctk.CTkButton(
            btn_frame,
            text=f"Type It ({COOLDOWN_SEC}s delay)",
            command=self.start_typing,
            font=FONT,
            corner_radius=8,
            width=180,
            height=36,
        )
        self.type_btn.pack(side="left", padx=8)

        self.stop_btn = ctk.CTkButton(
            btn_frame,
            text="Stop",
            command=self.stop_typing,
            font=FONT,
            corner_radius=8,
            width=100,
            height=36,
            fg_color="#8B0000",
            hover_color="#A00000",
        )
        self.stop_btn.pack(side="left", padx=8)

        # ── credit + github link ──
        credit_frame = ctk.CTkFrame(self.root, fg_color="transparent")
        credit_frame.pack(pady=(0, 5))

        ctk.CTkLabel(
            credit_frame,
            text="made by jlaiii  |",
            font=("Segoe UI", 11),
            text_color="gray",
        ).pack(side="left", padx=(0, 2))

        self.gh_link = ctk.CTkLabel(
            credit_frame,
            text="github",
            font=("Segoe UI", 11, "underline"),
            text_color="#58a6ff",
            cursor="hand2",
        )
        self.gh_link.pack(side="left")
        self.gh_link.bind(
            "<Button-1>",
            lambda e: webbrowser.open("https://github.com/jlaiii/human-typer"),
        )

        self.root.bind("<Escape>", lambda e: self.root.destroy())

    # ── helpers ──────────────────────────────────────────
    def _on_mode_change(self, choice: str):
        for key, prof in PROFILES.items():
            if prof["label"] == choice:
                self.mode = key
                break
        self._refresh_desc()

    def _on_mistake_toggle(self):
        self.leave_mistakes = self.mistake_var.get()
        self._refresh_desc()

    def _refresh_desc(self):
        p = PROFILES[self.mode]
        wpm = _wpm_text(p)
        extra = ""
        if self.leave_mistakes:
            extra = "  |  [mistakes LEFT IN]"
        self.mode_desc.configure(
            text=f"{wpm}  |  typo {p['typo_chance']*100:.1f}%  |  "
                 f"hesitate {p['hesitate_chance']*100:.0f}%{extra}"
        )

    # ── low-level key tap with variable hold ─────────────
    def _tap(self, key: str, p: dict):
        """press → hold for realistic duration → release"""
        keyboard.press(key)
        time.sleep(random.uniform(p["hold_min"], p["hold_max"]))
        keyboard.release(key)

    def _backspace(self, p: dict):
        self._tap("backspace", p)
        time.sleep(random.uniform(p["typo_bsp_min"], p["typo_bsp_max"]))

    # ── typing engine ────────────────────────────────────
    def type_human(self, text: str):
        p = PROFILES[self.mode]
        leave = self.leave_mistakes
        i = 0
        word_count = 0
        total_chars = len(text)

        speed = random.uniform(p["key_min"], p["key_max"])
        burst_left = random.randint(p["burst_min"], p["burst_max"])

        while i < total_chars and self.running:
            ch = text[i]
            typed_something = False

            # ── warmup: first few chars are slower ──
            warmup_mult = 1.0
            if word_count < p["warmup_words"]:
                warmup_mult = random.uniform(1.2, 2.0)

            # ── drift: speed gradually changes over time ──
            drift = 1.0 + (i / max(total_chars, 1) - 0.5) * p["drift_factor"] * 2

            # ═══════════════════════════════════════════════
            #  FAT-FINGER  (when leave_mistakes is ON)
            #  hit a nearby key AND LEAVE IT — no backspace
            # ═══════════════════════════════════════════════
            fat_chance = p["typo_chance"] * 0.3  # 30 % of typo rate → fat-finger
            if (
                leave
                and ch.isalpha()
                and random.random() < fat_chance
            ):
                wrong = NEARBY_EXTRA.get(ch.lower(), ch)
                if ch.isupper():
                    wrong = wrong.upper()
                self._tap(wrong, p)
                # small pause then type the real char too (double tap effect)
                time.sleep(random.uniform(p["typo_bsp_min"], p["typo_bsp_max"]))
                # still type the correct char right after

            # ═══════════════════════════════════════════════
            #  WORD-START TYPO (double-typo)
            # ═══════════════════════════════════════════════
            if (
                p["word_typo_chance"] > 0
                and ch.isalpha()
                and (i == 0 or text[i - 1] == " ")
                and random.random() < p["word_typo_chance"]
            ):
                n_chars = random.randint(1, 2)
                for w in range(n_chars):
                    if i + w >= total_chars:
                        break
                    rc = text[i + w]
                    if rc.isalpha():
                        wr = NEARBY_EXTRA.get(rc.lower(), rc)
                        if rc.isupper():
                            wr = wr.upper()
                        self._tap(wr, p)
                        time.sleep(random.uniform(p["typo_bsp_min"], p["typo_bsp_max"]))

                if leave and random.random() < 0.35:
                    # leave the mess — just type the correct word over it
                    pass
                else:
                    for _ in range(n_chars):
                        self._backspace(p)
                    time.sleep(random.uniform(0.06, 0.3))

            # ═══════════════════════════════════════════════
            #  SINGLE-CHAR TYPO
            # ═══════════════════════════════════════════════
            typo_occurred = False
            if (
                p["typo_chance"] > 0
                and ch.isalpha()
                and random.random() < p["typo_chance"]
            ):
                typo_occurred = True
                wrong = NEARBY_EXTRA.get(ch.lower(), ch)
                if ch.isupper():
                    wrong = wrong.upper()
                self._tap(wrong, p)
                time.sleep(random.uniform(p["typo_bsp_min"], p["typo_bsp_max"]))

                if leave and random.random() < 0.4:
                    # leave the typo — do NOT backspace
                    pass
                else:
                    self._backspace(p)

            # ═══════════════════════════════════════════════
            #  TYPE THE REAL CHARACTER
            # ═══════════════════════════════════════════════
            if ch == "\n":
                pass
            elif ch == "\t":
                self._tap("tab", p)
                typed_something = True
            else:
                self._tap(ch, p)
                typed_something = True
            i += 1

            if not typed_something:
                continue

            # ─── burst management ───
            burst_left -= 1
            if burst_left <= 0:
                speed = random.uniform(p["key_min"], p["key_max"])
                burst_left = random.randint(p["burst_min"], p["burst_max"])

            # ─── inter-key delay with jitter + warmup + drift ───
            jitter = (
                1.0 - p["speed_jitter"] / 2 + random.random() * p["speed_jitter"]
            )
            time.sleep(speed * jitter * warmup_mult * drift)

            # ─── mid-word hesitation ───
            if (
                i < total_chars
                and text[i] not in (" ", "\n", "\t")
                and random.random() < p["hesitate_chance"]
            ):
                time.sleep(random.uniform(p["hesitate_min"], p["hesitate_max"]))

            # ─── end-of-word reached ───
            if i < total_chars and text[i] == " ":
                word_count += 1
                if word_count % p["ramp_words"] == 0:
                    speed = random.uniform(p["key_min"], p["key_max"])
                    burst_left = random.randint(p["burst_min"], p["burst_max"])
                if random.random() < p["wp_chance"]:
                    time.sleep(random.uniform(p["wp_min"], p["wp_max"]))

            # ─── sentence-end pause ───
            if ch in ".!?" and (i >= total_chars or text[i] == " "):
                if p["sent_max"] > 0:
                    time.sleep(random.uniform(p["sent_min"], p["sent_max"]))

    # ── threading ────────────────────────────────────────
    def _typing_worker(self, text: str):
        self.running = True
        time.sleep(COOLDOWN_SEC)
        if not self.running:
            self.update_status("Cancelled.")
            return
        extra = " [mistakes ON]" if self.leave_mistakes else ""
        self.update_status(f"Typing...  [{self.mode} mode{extra}]")
        try:
            self.type_human(text)
        except Exception as e:
            self.update_status(f"Error: {e}")
            self.running = False
            return
        self.running = False
        self.update_status("Done.")

    def start_typing(self):
        if self.running:
            return
        text = self.textbox.get("1.0", "end-1c").rstrip("\n")
        if not text.strip():
            self.update_status("Nothing to type.")
            return
        self.update_status(
            f"Starting in {COOLDOWN_SEC}s... switch to your target window!"
        )
        t = threading.Thread(
            target=self._typing_worker, args=(text,), daemon=True
        )
        t.start()

    def stop_typing(self):
        self.running = False
        self.update_status("Stopped.")

    def update_status(self, msg: str):
        self.root.after(0, lambda: self.status.configure(text=msg))

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    HumanTyper().run()
