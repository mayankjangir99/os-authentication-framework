import tkinter as tk
from tkinter import messagebox, ttk

from auth import HashingError, build_authentication_manager


class SecureAuthApp(tk.Tk):
    """Tkinter user interface for the secure authentication workflow."""

    def __init__(self) -> None:
        super().__init__()
        self.title("Secure Authentication Framework")
        self.geometry("1180x720")
        self.minsize(1020, 640)
        self.configure(bg="#07111f")

        self.current_user = ""
        self.password_visible = False

        try:
            self.auth_manager = build_authentication_manager()
        except HashingError as exc:
            messagebox.showerror("Startup Error", str(exc))
            self.destroy()
            return

        self.palette = {
            "app_bg": "#07111f",
            "hero_bg": "#0d1b2a",
            "hero_panel": "#13263b",
            "card_bg": "#f4f7fb",
            "card_border": "#d5deea",
            "surface": "#ffffff",
            "surface_alt": "#e9eef6",
            "text_dark": "#10233a",
            "text_muted": "#5f7188",
            "accent": "#0f9d8a",
            "accent_dark": "#0b7a6c",
            "accent_soft": "#d8f4ef",
            "warning": "#ef4444",
            "warning_soft": "#fee2e2",
            "success": "#1f9d55",
            "success_soft": "#dcfce7",
            "info": "#2563eb",
            "info_soft": "#dbeafe",
        }

        self._configure_styles()
        self._build_layout()
        self._bind_events()
        self.show_login_frame()

    def _configure_styles(self) -> None:
        style = ttk.Style(self)
        style.theme_use("clam")

        style.configure("App.TFrame", background=self.palette["app_bg"])
        style.configure("Card.TFrame", background=self.palette["card_bg"])
        style.configure("Surface.TFrame", background=self.palette["surface"])
        style.configure(
            "Eyebrow.TLabel",
            background=self.palette["card_bg"],
            foreground=self.palette["accent_dark"],
            font=("Segoe UI Semibold", 10),
        )
        style.configure(
            "Title.TLabel",
            background=self.palette["card_bg"],
            foreground=self.palette["text_dark"],
            font=("Georgia", 26, "bold"),
        )
        style.configure(
            "Body.TLabel",
            background=self.palette["card_bg"],
            foreground=self.palette["text_muted"],
            font=("Segoe UI", 11),
        )
        style.configure(
            "FieldLabel.TLabel",
            background=self.palette["card_bg"],
            foreground=self.palette["text_dark"],
            font=("Segoe UI Semibold", 10),
        )
        style.configure(
            "Primary.TButton",
            background=self.palette["accent"],
            foreground="#ffffff",
            borderwidth=0,
            focusthickness=0,
            focuscolor=self.palette["accent"],
            font=("Segoe UI Semibold", 11),
            padding=(18, 10),
        )
        style.map(
            "Primary.TButton",
            background=[("active", self.palette["accent_dark"])],
            foreground=[("active", "#ffffff")],
        )
        style.configure(
            "Secondary.TButton",
            background=self.palette["surface_alt"],
            foreground=self.palette["text_dark"],
            borderwidth=0,
            focusthickness=0,
            focuscolor=self.palette["surface_alt"],
            font=("Segoe UI Semibold", 10),
            padding=(16, 9),
        )
        style.map(
            "Secondary.TButton",
            background=[("active", "#d8e0eb")],
            foreground=[("active", self.palette["text_dark"])],
        )

    def _build_layout(self) -> None:
        shell = ttk.Frame(self, style="App.TFrame", padding=22)
        shell.pack(fill="both", expand=True)

        main = tk.Frame(shell, bg=self.palette["app_bg"])
        main.pack(fill="both", expand=True)

        self.hero = tk.Frame(main, bg=self.palette["hero_bg"], width=350, padx=26, pady=24)
        self.hero.pack(side="left", fill="y")
        self.hero.pack_propagate(False)

        workspace = tk.Frame(main, bg=self.palette["app_bg"], padx=16, pady=10)
        workspace.pack(side="right", fill="both", expand=True)

        self._build_hero_panel()

        card_outer = tk.Frame(
            workspace,
            bg=self.palette["card_border"],
            highlightthickness=0,
            bd=0,
        )
        card_outer.pack(fill="both", expand=True, padx=8, pady=8)

        self.card = ttk.Frame(card_outer, style="Card.TFrame", padding=24)
        self.card.pack(fill="both", expand=True, padx=1, pady=1)

        topbar = ttk.Frame(self.card, style="Card.TFrame")
        topbar.pack(fill="x")

        self.step_badge = tk.Label(
            topbar,
            text="STEP 01  PASSWORD CHECK",
            bg=self.palette["accent_soft"],
            fg=self.palette["accent_dark"],
            padx=12,
            pady=7,
            font=("Segoe UI Semibold", 9),
        )
        self.step_badge.pack(side="left")

        self.context_note = ttk.Label(
            topbar,
            text="Desktop simulation of a two-step access flow",
            style="Body.TLabel",
            wraplength=280,
            justify="right",
        )
        self.context_note.pack(side="right")

        self.form_host = ttk.Frame(self.card, style="Card.TFrame")
        self.form_host.pack(fill="both", expand=True, pady=(28, 0))

        self.login_frame = ttk.Frame(self.form_host, style="Card.TFrame")
        self.otp_frame = ttk.Frame(self.form_host, style="Card.TFrame")

        self._build_login_frame()
        self._build_otp_frame()

    def _build_hero_panel(self) -> None:
        tk.Label(
            self.hero,
            text="SECURE AUTH",
            bg=self.palette["hero_bg"],
            fg="#93c5fd",
            font=("Segoe UI Semibold", 10),
        ).pack(anchor="w")

        tk.Label(
            self.hero,
            text="Operating Systems\nAuthentication Suite",
            bg=self.palette["hero_bg"],
            fg="#f8fbff",
            justify="left",
            wraplength=250,
            anchor="w",
            font=("Georgia", 20, "bold"),
        ).pack(anchor="w", pady=(14, 12))

        tk.Label(
            self.hero,
            text=(
                "A cleaner control-room interface for password validation, OTP checks, "
                "and lockout feedback without changing the underlying project logic."
            ),
            bg=self.palette["hero_bg"],
            fg="#bfd0e3",
            justify="left",
            wraplength=240,
            font=("Segoe UI", 10),
        ).pack(anchor="w")

        feature_panel = tk.Frame(self.hero, bg=self.palette["hero_panel"], padx=16, pady=16)
        feature_panel.pack(fill="x", pady=(20, 14))

        tk.Label(
            feature_panel,
            text="Security Layers",
            bg=self.palette["hero_panel"],
            fg="#f8fbff",
            font=("Segoe UI Semibold", 12),
        ).pack(anchor="w", pady=(0, 10))

        for item in (
            "Salted password verification via C hashing executable",
            "4-digit OTP challenge generated after valid credentials",
            "Automatic lockout after three failed password attempts",
        ):
            tk.Label(
                feature_panel,
                text=f"•  {item}",
                bg=self.palette["hero_panel"],
                fg="#bfd0e3",
                justify="left",
                wraplength=270,
                font=("Segoe UI", 10),
            ).pack(anchor="w", pady=4)

        self.hero_status = tk.Label(
            self.hero,
            text="System ready. Use one of the seeded demo accounts to sign in.",
            bg=self.palette["hero_bg"],
            fg="#9ae6b4",
            justify="left",
            wraplength=240,
            font=("Segoe UI", 10),
        )
        self.hero_status.pack(anchor="w", pady=(2, 16))

        credentials_panel = tk.Frame(self.hero, bg="#10263d", padx=16, pady=16)
        credentials_panel.pack(fill="x", side="bottom")

        tk.Label(
            credentials_panel,
            text="Demo Credentials",
            bg="#10263d",
            fg="#f8fbff",
            font=("Segoe UI Semibold", 11),
        ).pack(anchor="w")

        tk.Label(
            credentials_panel,
            text="admin  /  SecurePass123\nstudent  /  OsProject@2026",
            bg="#10263d",
            fg="#c7d7e8",
            justify="left",
            font=("Consolas", 10),
        ).pack(anchor="w", pady=(8, 0))

    def _build_login_frame(self) -> None:
        ttk.Label(self.login_frame, text="Credential Checkpoint", style="Eyebrow.TLabel").pack(anchor="w")
        ttk.Label(
            self.login_frame,
            text="Sign in to start the verification sequence",
            style="Title.TLabel",
            wraplength=520,
            justify="left",
        ).pack(anchor="w", pady=(8, 10))
        ttk.Label(
            self.login_frame,
            text="Enter the registered username and password. A valid login will issue a time-limited OTP.",
            style="Body.TLabel",
            wraplength=500,
        ).pack(anchor="w", pady=(0, 22))

        username_group, self.username_entry = self._create_input(
            self.login_frame,
            "Username",
            width=30,
        )
        username_group.pack(fill="x", pady=(0, 14))

        password_group, self.password_entry = self._create_input(
            self.login_frame,
            "Password",
            width=30,
            show="*",
            with_toggle=True,
        )
        password_group.pack(fill="x", pady=(0, 14))

        helper = tk.Frame(self.login_frame, bg=self.palette["card_bg"], pady=8)
        helper.pack(fill="x", pady=(4, 12))

        self.login_hint = tk.Label(
            helper,
            text="Tip: press Enter after typing your password to continue.",
            bg=self.palette["card_bg"],
            fg=self.palette["text_muted"],
            font=("Segoe UI", 10),
        )
        self.login_hint.pack(anchor="w")

        self._create_action_button(
            self.login_frame,
            text="Continue to OTP",
            command=self.handle_login,
            tone="primary",
        ).pack(anchor="w", pady=(8, 18))

        self.login_status = self._create_status_label(self.login_frame)
        self.login_status.pack(fill="x")

    def _build_otp_frame(self) -> None:
        ttk.Label(self.otp_frame, text="Second Factor", style="Eyebrow.TLabel").pack(anchor="w")
        ttk.Label(
            self.otp_frame,
            text="Complete OTP verification",
            style="Title.TLabel",
            wraplength=520,
            justify="left",
        ).pack(anchor="w", pady=(8, 10))
        ttk.Label(
            self.otp_frame,
            text="A 4-digit one-time passcode is required to complete authentication. The demo app shows the OTP after login.",
            style="Body.TLabel",
            wraplength=500,
        ).pack(anchor="w", pady=(0, 22))

        info_strip = tk.Frame(self.otp_frame, bg=self.palette["info_soft"], padx=14, pady=12)
        info_strip.pack(fill="x", pady=(0, 18))

        self.otp_user_label = tk.Label(
            info_strip,
            text="Verifying user: -",
            bg=self.palette["info_soft"],
            fg=self.palette["info"],
            font=("Segoe UI Semibold", 10),
        )
        self.otp_user_label.pack(anchor="w")

        tk.Label(
            info_strip,
            text="OTP validity: 120 seconds from successful password verification.",
            bg=self.palette["info_soft"],
            fg=self.palette["info"],
            font=("Segoe UI", 10),
        ).pack(anchor="w", pady=(6, 0))

        otp_group, self.otp_entry = self._create_input(
            self.otp_frame,
            "One-Time Password",
            width=12,
            justify="center",
            font=("Consolas", 18, "bold"),
        )
        otp_group.pack(fill="x", pady=(0, 18))

        button_row = ttk.Frame(self.otp_frame, style="Card.TFrame")
        button_row.pack(anchor="w", pady=(4, 18))

        self._create_action_button(
            button_row,
            text="Verify Access",
            command=self.handle_otp_verification,
            tone="primary",
        ).pack(side="left", padx=(0, 10))

        self._create_action_button(
            button_row,
            text="Return to Login",
            command=self.show_login_frame,
            tone="secondary",
        ).pack(side="left")

        self.otp_status = self._create_status_label(self.otp_frame)
        self.otp_status.pack(fill="x")

    def _create_input(
        self,
        parent: tk.Widget,
        label_text: str,
        width: int,
        show: str | None = None,
        justify: str = "left",
        font: tuple[str, int] | tuple[str, int, str] = ("Segoe UI", 12),
        with_toggle: bool = False,
    ) -> tuple[tk.Frame, tk.Entry]:
        wrapper = tk.Frame(parent, bg=self.palette["card_bg"])

        ttk.Label(wrapper, text=label_text, style="FieldLabel.TLabel").pack(anchor="w", pady=(0, 7))

        border = tk.Frame(wrapper, bg=self.palette["card_border"], padx=1, pady=1)
        border.pack(fill="x")

        field = tk.Frame(border, bg=self.palette["surface"])
        field.pack(fill="x")

        entry = tk.Entry(
            field,
            relief="flat",
            bd=0,
            bg=self.palette["surface"],
            fg=self.palette["text_dark"],
            insertbackground=self.palette["text_dark"],
            font=font,
            width=width,
            show=show or "",
            justify=justify,
        )
        entry.pack(side="left", fill="x", expand=True, padx=(14, 10), pady=12)
        entry._wrapper = wrapper  # type: ignore[attr-defined]
        entry._border = border  # type: ignore[attr-defined]

        if with_toggle:
            toggle = tk.Button(
                field,
                text="Show",
                relief="flat",
                bd=0,
                bg=self.palette["surface"],
                fg=self.palette["accent_dark"],
                activebackground=self.palette["surface"],
                activeforeground=self.palette["accent_dark"],
                cursor="hand2",
                font=("Segoe UI Semibold", 10),
                command=self._toggle_password_visibility,
            )
            toggle.pack(side="right", padx=(0, 12))
            self.password_toggle = toggle

        return wrapper, entry

    def _create_status_label(self, parent: tk.Widget) -> tk.Label:
        return tk.Label(
            parent,
            text="",
            bg=self.palette["card_bg"],
            fg=self.palette["text_muted"],
            justify="left",
            anchor="w",
            padx=14,
            pady=12,
            font=("Segoe UI", 10),
        )

    def _create_action_button(
        self,
        parent: tk.Widget,
        text: str,
        command,
        tone: str = "primary",
    ) -> tk.Button:
        palette = {
            "primary": {
                "bg": self.palette["accent"],
                "fg": "#ffffff",
                "activebackground": self.palette["accent_dark"],
                "activeforeground": "#ffffff",
            },
            "secondary": {
                "bg": self.palette["surface_alt"],
                "fg": self.palette["text_dark"],
                "activebackground": "#d8e0eb",
                "activeforeground": self.palette["text_dark"],
            },
        }[tone]

        return tk.Button(
            parent,
            text=text,
            command=command,
            relief="flat",
            bd=0,
            highlightthickness=0,
            cursor="hand2",
            padx=18,
            pady=10,
            font=("Segoe UI Semibold", 11 if tone == "primary" else 10),
            **palette,
        )

    def _bind_events(self) -> None:
        self.username_entry.bind("<Return>", lambda _event: self.handle_login())
        self.password_entry.bind("<Return>", lambda _event: self.handle_login())
        self.otp_entry.bind("<Return>", lambda _event: self.handle_otp_verification())

        for entry in (self.username_entry, self.password_entry, self.otp_entry):
            entry.bind("<FocusIn>", lambda event, e=entry: self._highlight_entry(e, active=True))
            entry.bind("<FocusOut>", lambda event, e=entry: self._highlight_entry(e, active=False))

    def _highlight_entry(self, entry: tk.Entry, active: bool) -> None:
        border = entry._border  # type: ignore[attr-defined]
        border.configure(bg=self.palette["accent"] if active else self.palette["card_border"])

    def _toggle_password_visibility(self) -> None:
        self.password_visible = not self.password_visible
        self.password_entry.config(show="" if self.password_visible else "*")
        self.password_toggle.config(text="Hide" if self.password_visible else "Show")

    def _set_status(self, label: tk.Label, message: str, tone: str = "neutral") -> None:
        tones = {
            "neutral": (self.palette["surface_alt"], self.palette["text_muted"]),
            "info": (self.palette["info_soft"], self.palette["info"]),
            "success": (self.palette["success_soft"], self.palette["success"]),
            "error": (self.palette["warning_soft"], self.palette["warning"]),
        }
        bg, fg = tones[tone]
        label.config(text=message, bg=bg, fg=fg)

    def show_login_frame(self) -> None:
        self.otp_frame.pack_forget()
        self.login_frame.pack(fill="both", expand=True)
        self.step_badge.config(text="STEP 01  PASSWORD CHECK", bg=self.palette["accent_soft"], fg=self.palette["accent_dark"])
        self.context_note.config(text="Desktop simulation of a two-step access flow")
        self.hero_status.config(text="System ready. Use one of the seeded demo accounts to sign in.", fg="#9ae6b4")
        self.password_entry.delete(0, tk.END)
        self.otp_entry.delete(0, tk.END)
        self.login_status.config(text="", bg=self.palette["card_bg"])
        self.otp_status.config(text="", bg=self.palette["card_bg"])
        self.password_entry.config(show="" if self.password_visible else "*")
        self.username_entry.focus_set()

    def show_otp_frame(self) -> None:
        self.login_frame.pack_forget()
        self.otp_frame.pack(fill="both", expand=True)
        self.step_badge.config(text="STEP 02  OTP CHALLENGE", bg=self.palette["info_soft"], fg=self.palette["info"])
        self.context_note.config(text="Waiting for the one-time passcode")
        self.hero_status.config(
            text=f"Password accepted for {self.current_user}. Final access now depends on OTP verification.",
            fg="#7dd3fc",
        )
        self.otp_user_label.config(text=f"Verifying user: {self.current_user}")
        self.otp_entry.focus_set()

    def handle_login(self) -> None:
        username = self.username_entry.get().strip()
        password = self.password_entry.get()

        try:
            result = self.auth_manager.authenticate_password(username, password)
        except HashingError as exc:
            messagebox.showerror("Hashing Error", str(exc))
            return

        tone = "success" if result.success else "error"
        if result.success and not result.locked:
            tone = "success"
        elif not result.success and not result.locked and result.remaining_attempts > 0:
            tone = "info"
        self._set_status(self.login_status, result.message, tone)

        if result.locked:
            self.hero_status.config(text="Security lock triggered after repeated failures.", fg="#fca5a5")
            messagebox.showerror("Account Locked", result.message)
            return

        if not result.success:
            self.hero_status.config(text="Credential validation failed. Review the account details and try again.", fg="#fbbf24")
            messagebox.showwarning("Login Failed", result.message)
            return

        self.current_user = username
        current_otp = self.auth_manager.get_current_otp_for_demo(username)
        messagebox.showinfo(
            "OTP Generated",
            f"OTP has been generated for {username}.\nDemo OTP: {current_otp}",
        )
        self.show_otp_frame()

    def handle_otp_verification(self) -> None:
        otp_value = self.otp_entry.get().strip()
        result = self.auth_manager.verify_otp(self.current_user, otp_value)

        self._set_status(self.otp_status, result.message, "success" if result.success else "error")

        if result.success:
            self.hero_status.config(text="Authentication chain complete. Access granted.", fg="#86efac")
            messagebox.showinfo("Access Granted", result.message)
            self.show_login_frame()
            self.username_entry.delete(0, tk.END)
            return

        self.hero_status.config(text="OTP verification failed. The session remains protected.", fg="#fca5a5")
        messagebox.showerror("OTP Verification Failed", result.message)


def main() -> None:
    app = SecureAuthApp()
    app.mainloop()


if __name__ == "__main__":
    main()
