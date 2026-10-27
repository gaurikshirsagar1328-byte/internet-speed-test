
import tkinter as tk
from tkinter import messagebox
import threading
import queue
import math
import time

try:
    import speedtest
except ImportError:
    speedtest = None


# ---------- APP SETTINGS ----------
APP_NAME = "NEXUS | Internet Speed Test"

BG = "#0B1020"
PANEL = "#121A2B"
PANEL_LIGHT = "#19243A"
WHITE = "#F1F5F9"
MUTED = "#8D9BB3"
BLUE = "#45B8FF"
PURPLE = "#A78BFA"
GREEN = "#4ADE80"
ORANGE = "#FBBF24"
RED = "#FB7185"

MAX_SPEED = 100


class InternetSpeedTest:
    def __init__(self, root):
        self.root = root
        self.root.title(APP_NAME)
        self.root.geometry("900x700")
        self.root.minsize(760, 650)
        self.root.configure(bg=BG)

        self.events = queue.Queue()
        self.testing = False
        self.animation_running = True
        self.current_speed = 0.0
        self.target_speed = 0.0
        self.animation_phase = 0.0

        self.build_ui()
        self.draw_gauge()
        self.animate_needle()
        self.poll_events()

        self.root.protocol("WM_DELETE_WINDOW", self.close_app)

    # ---------- USER INTERFACE ----------
    def build_ui(self):
        header = tk.Frame(self.root, bg=BG)
        header.pack(fill="x", padx=30, pady=(22, 10))

        tk.Label(
            header, text="NEXUS", bg=BG, fg=BLUE,
            font=("Segoe UI", 23, "bold")
        ).pack(side="left")

        tk.Label(
            header, text="  INTERNET SPEED TEST",
            bg=BG, fg=WHITE, font=("Segoe UI", 12, "bold")
        ).pack(side="left", pady=(8, 0))

        self.status_label = tk.Label(
            self.root, text="● READY TO TEST",
            bg=BG, fg=GREEN, font=("Segoe UI", 10, "bold")
        )
        self.status_label.pack(pady=(4, 0))

        # Main speedometer
        self.gauge_canvas = tk.Canvas(
            self.root, width=520, height=330,
            bg=BG, highlightthickness=0
        )
        self.gauge_canvas.pack(pady=(0, 0))

        # Results cards
        cards = tk.Frame(self.root, bg=BG)
        cards.pack(fill="x", padx=35, pady=(0, 18))
        cards.grid_columnconfigure((0, 1, 2), weight=1)

        self.download_value = self.make_card(
            cards, 0, "DOWNLOAD", "↓", BLUE
        )
        self.upload_value = self.make_card(
            cards, 1, "UPLOAD", "↑", GREEN
        )
        self.ping_value = self.make_card(
            cards, 2, "PING", "◉", ORANGE
        )

        # Progress bar
        self.progress = tk.Canvas(
            self.root, height=5, bg=PANEL,
            highlightthickness=0
        )
        self.progress.pack(fill="x", padx=45, pady=(0, 10))
        self.progress_width = 0
        self.progress.bind("<Configure>", self.reset_progress)

        self.message_label = tk.Label(
            self.root,
            text="Ready when you are. Check your connection!",
            bg=BG, fg=MUTED, font=("Segoe UI", 10),
            wraplength=650
        )
        self.message_label.pack(pady=(0, 12))

        self.test_button = tk.Button(
            self.root, text="▶   START SPEED TEST",
            command=self.start_test,
            bg=BLUE, fg="#06111F",
            activebackground="#8AD5FF",
            activeforeground="#06111F",
            font=("Segoe UI", 12, "bold"),
            relief="flat", bd=0, cursor="hand2",
            padx=28, pady=12
        )
        self.test_button.pack()

        tk.Label(
            self.root,
            text="REAL-TIME NETWORK DIAGNOSTICS  •  POWERED BY PYTHON",
            bg=BG, fg="#53627A",
            font=("Segoe UI", 8)
        ).pack(side="bottom", pady=14)

    def make_card(self, parent, column, title, symbol, color):
        card = tk.Frame(parent, bg=PANEL, padx=12, pady=13)
        card.grid(
            row=0, column=column, sticky="nsew",
            padx=7, ipady=3
        )

        tk.Label(
            card, text=f"{symbol}  {title}",
            bg=PANEL, fg=color,
            font=("Segoe UI", 10, "bold")
        ).pack()

        value = tk.Label(
            card, text="--",
            bg=PANEL, fg=WHITE,
            font=("Segoe UI", 22, "bold")
        )
        value.pack(pady=(7, 0))

        unit = "ms" if title == "PING" else "Mbps"
        tk.Label(
            card, text=unit, bg=PANEL, fg=MUTED,
            font=("Segoe UI", 9)
        ).pack()

        return value

    # ---------- ANIMATED SPEEDOMETER ----------
    def draw_gauge(self):
        c = self.gauge_canvas
        c.delete("gauge")

        cx, cy, radius = 260, 205, 145

        # Background glow rings
        for r, color in [(155, "#111C30"), (150, "#16233A")]:
            c.create_arc(
                cx-r, cy-r, cx+r, cy+r,
                start=150, extent=240,
                style="arc", outline=color,
                width=13, tags="gauge"
            )

        # Colored speed range, drawn as smooth segments
        colors = [BLUE, "#4AABFF", PURPLE, ORANGE, RED]
        segments = 120

        for i in range(segments):
            p1 = i / segments
            p2 = (i + 1) / segments
            a1 = math.radians(210 - p1 * 240)
            a2 = math.radians(210 - p2 * 240)

            x1 = cx + radius * math.cos(a1)
            y1 = cy - radius * math.sin(a1)
            x2 = cx + radius * math.cos(a2)
            y2 = cy - radius * math.sin(a2)

            color = colors[min(int(p1 * len(colors)), len(colors)-1)]
            c.create_line(
                x1, y1, x2, y2, fill=color,
                width=5, capstyle=tk.ROUND, tags="gauge"
            )

        # Tick marks and labels
        for value in range(0, 101, 10):
            angle = math.radians(210 - value * 2.4)

            x1 = cx + 119 * math.cos(angle)
            y1 = cy - 119 * math.sin(angle)
            x2 = cx + 132 * math.cos(angle)
            y2 = cy - 132 * math.sin(angle)

            c.create_line(
                x1, y1, x2, y2,
                fill="#D6E3F5", width=2, tags="gauge"
            )

            tx = cx + 105 * math.cos(angle)
            ty = cy - 105 * math.sin(angle)

            c.create_text(
                tx, ty, text=str(value),
                fill=MUTED, font=("Segoe UI", 8),
                tags="gauge"
            )

        # Main speed reading
        c.create_text(
            cx, cy-12, text="0.0",
            fill=WHITE, font=("Segoe UI", 35, "bold"),
            tags="speed_text"
        )
        c.create_text(
            cx, cy+23, text="Mbps",
            fill=BLUE, font=("Segoe UI", 12, "bold"),
            tags="gauge"
        )
        c.create_text(
            cx, cy+53, text="DOWNLOAD SPEED",
            fill=MUTED, font=("Segoe UI", 9),
            tags="gauge"
        )

        # Needle pivot
        c.create_oval(
            cx-9, cy-9, cx+9, cy+9,
            fill=WHITE, outline=BLUE, width=3,
            tags="gauge"
        )

        self.update_needle(0)

    def update_needle(self, speed):
        c = self.gauge_canvas
        c.delete("needle")

        cx, cy = 260, 205
        ratio = min(max(speed / MAX_SPEED, 0), 1)
        angle = math.radians(210 - ratio * 240)

        length = 105
        x = cx + length * math.cos(angle)
        y = cy - length * math.sin(angle)

        c.create_line(
            cx, cy, x, y,
            fill=BLUE, width=4, capstyle=tk.ROUND,
            tags="needle"
        )
        c.create_oval(
            cx-7, cy-7, cx+7, cy+7,
            fill=WHITE, outline=BLUE, width=2,
            tags="needle"
        )

    def animate_needle(self):
        if not self.animation_running:
            return

        difference = self.target_speed - self.current_speed

        if abs(difference) > 0.15:
            self.current_speed += difference * 0.12
        else:
            self.current_speed = self.target_speed

        self.update_needle(self.current_speed)

        self.gauge_canvas.itemconfigure(
            "speed_text",
            text=f"{self.current_speed:.1f}"
        )

        self.animation_phase += 0.08
        self.root.after(25, self.animate_needle)

    # ---------- SPEED TEST ----------
    def start_test(self):
        if self.testing:
            return

        if speedtest is None:
            messagebox.showerror(
                "Missing dependency",
                "speedtest-cli is not installed.\n\n"
                "Open the VS Code terminal and run:\n"
                "python -m pip install speedtest-cli"
            )
            return

        self.testing = True
        self.target_speed = 0
        self.current_speed = 0
        self.download_value.config(text="--")
        self.upload_value.config(text="--")
        self.ping_value.config(text="--")

        self.status_label.config(
            text="● TEST IN PROGRESS",
            fg=ORANGE
        )
        self.message_label.config(
            text="Connecting to a suitable test server..."
        )
        self.test_button.config(
            state="disabled", text="⏳  TESTING..."
        )
        self.set_progress(0.05)

        threading.Thread(
            target=self.run_test, daemon=True
        ).start()

    def run_test(self):
        """Run network operations away from the Tkinter UI thread."""
        try:
            self.events.put(("status", "Finding the best server..."))

            tester = speedtest.Speedtest(timeout=15)
            tester.get_best_server()

            ping = tester.results.ping

            self.events.put(("status", "Measuring download speed..."))
            download = tester.download() / 1_000_000

            self.events.put(("download", download))
            self.events.put(("status", "Measuring upload speed..."))

            upload = tester.upload() / 1_000_000

            self.events.put((
                "success",
                {
                    "download": download,
                    "upload": upload,
                    "ping": ping
                }
            ))

        except Exception as error:
            self.events.put(("error", str(error)))

    def poll_events(self):
        try:
            while True:
                event, data = self.events.get_nowait()

                if event == "status":
                    self.message_label.config(text=data)
                    if "download" in data.lower():
                        self.set_progress(0.35)
                    elif "upload" in data.lower():
                        self.set_progress(0.70)

                elif event == "download":
                    self.target_speed = min(
                        float(data), MAX_SPEED
                    )
                    self.set_progress(0.55)

                elif event == "success":
                    self.show_results(data)

                elif event == "error":
                    self.show_error(data)

        except queue.Empty:
            pass

        self.root.after(100, self.poll_events)

    def show_results(self, results):
        download = results["download"]
        upload = results["upload"]
        ping = results["ping"]

        self.download_value.config(text=f"{download:.2f}")
        self.upload_value.config(text=f"{upload:.2f}")
        self.ping_value.config(text=f"{ping:.0f}")

        self.target_speed = min(download, MAX_SPEED)
        self.status_label.config(
            text="● TEST COMPLETED",
            fg=GREEN
        )
        self.message_label.config(
            text="Speed test completed successfully!"
        )
        self.set_progress(1.0)
        self.finish_test()

    def show_error(self, error):
        self.status_label.config(
            text="● TEST FAILED", fg=RED
        )
        self.message_label.config(
            text="Could not complete the speed test. Check your connection."
        )
        self.set_progress(0)

        # Print details for troubleshooting without overwhelming the UI.
        print("Speed test error:", error)

        self.finish_test()

        messagebox.showwarning(
            "Speed Test Failed",
            "The test could not be completed.\n\n"
            "Check your internet connection and try again.\n"
            "If the issue continues, check the VS Code terminal "
            "for the error details."
        )

    def finish_test(self):
        self.testing = False
        self.test_button.config(
            state="normal", text="↻  TEST AGAIN"
        )

    # ---------- PROGRESS BAR ----------
    def reset_progress(self, event=None):
        self.set_progress(0)

    def set_progress(self, fraction):
        self.progress.delete("bar")
        width = self.progress.winfo_width()

        if width > 1 and fraction > 0:
            self.progress.create_rectangle(
                0, 0, width * min(fraction, 1), 5,
                fill=BLUE, outline="", tags="bar"
            )

    def close_app(self):
        self.animation_running = False
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = InternetSpeedTest(root)
    root.mainloop()
