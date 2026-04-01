import tkinter as tk
from tkinter import messagebox, ttk

from auth import HashingError, build_authentication_manager


class SecureAuthApp(tk.Tk):
    """Tkinter user interface for the secure authentication workflow."""

    def __init__(self) -> None:
        super().__init__()
        self.title("Secure Authentication Framework")
        self.geometry("760x480")
        self.resizable(False, False)
        self.configure(bg="#0f172a")

        self.current_user = ""
        try:
            self.auth_manager = build_authentication_manager()
        except HashingError as exc:
            messagebox.showerror("Startup Error", str(exc))
            self.destroy()
            return

        self._configure_styles()
        self._build_layout()
        self.show_login_frame()

    def _configure_styles(self) -> None:
        style = ttk.Style(self)
        style.theme_use("clam")

        style.configure("Card.TFrame", background="#e2e8f0")
        style.configure("Title.TLabel", background="#e2e8f0", foreground="#0f172a", font=("Segoe UI", 22, "bold"))
        style.configure("Body.TLabel", background="#e2e8f0", foreground="#334155", font=("Segoe UI", 11))
        style.configure("Field.TLabel", background="#e2e8f0", foreground="#0f172a", font=("Segoe UI", 11, "bold"))
        style.configure("Status.TLabel", background="#e2e8f0", foreground="#1d4ed8", font=("Segoe UI", 10))
        style.configure("Primary.TButton", font=("Segoe UI", 11, "bold"), padding=10)
        style.configure("Secondary.TButton", font=("Segoe UI", 10), padding=8)
        style.map("Primary.TButton", background=[("active", "#1d4ed8")], foreground=[("active", "#ffffff")])

    def _build_layout(self) -> None:
        outer = tk.Frame(self, bg="#0f172a")
        outer.pack(fill="both", expand=True, padx=30, pady=30)

        sidebar = tk.Frame(outer, bg="#1e293b", width=240)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        tk.Label(
            sidebar,
            text="Secure\nAuthentication\nFramework",
            bg="#1e293b",
            fg="#f8fafc",
            justify="left",
            font=("Segoe UI", 24, "bold"),
        ).pack(anchor="nw", padx=24, pady=(36, 16))

        tk.Label(
            sidebar,
            text="Academic project for operating system level authentication simulation.",
            bg="#1e293b",
            fg="#cbd5e1",
            justify="left",
            wraplength=180,
            font=("Segoe UI", 11),
        ).pack(anchor="nw", padx=24)

        self.content = ttk.Frame(outer, style="Card.TFrame", padding=30)
        self.content.pack(side="right", fill="both", expand=True)

        self.login_frame = ttk.Frame(self.content, style="Card.TFrame")
        self.otp_frame = ttk.Frame(self.content, style="Card.TFrame")

        self._build_login_frame()
        self._build_otp_frame()

    def _build_login_frame(self) -> None:
        ttk.Label(self.login_frame, text="Sign In", style="Title.TLabel").pack(anchor="w")
        ttk.Label(
            self.login_frame,
            text="Enter your credentials to continue to OTP verification.",
            style="Body.TLabel",
        ).pack(anchor="w", pady=(4, 22))

        ttk.Label(self.login_frame, text="Username", style="Field.TLabel").pack(anchor="w")
        self.username_entry = ttk.Entry(self.login_frame, font=("Segoe UI", 11), width=34)
        self.username_entry.pack(anchor="w", pady=(6, 16))

        ttk.Label(self.login_frame, text="Password", style="Field.TLabel").pack(anchor="w")
        self.password_entry = ttk.Entry(self.login_frame, font=("Segoe UI", 11), width=34, show="*")
        self.password_entry.pack(anchor="w", pady=(6, 20))

        ttk.Button(
            self.login_frame,
            text="Login",
            style="Primary.TButton",
            command=self.handle_login,
        ).pack(anchor="w")

        ttk.Label(
            self.login_frame,
            text="Default users: admin / SecurePass123 and student / OsProject@2026",
            style="Status.TLabel",
        ).pack(anchor="w", pady=(18, 8))

        self.login_status = ttk.Label(self.login_frame, text="", style="Status.TLabel")
        self.login_status.pack(anchor="w")

    def _build_otp_frame(self) -> None:
        ttk.Label(self.otp_frame, text="OTP Verification", style="Title.TLabel").pack(anchor="w")
        ttk.Label(
            self.otp_frame,
            text="A 4-digit OTP is required after successful password verification.",
            style="Body.TLabel",
        ).pack(anchor="w", pady=(4, 22))

        ttk.Label(self.otp_frame, text="Enter OTP", style="Field.TLabel").pack(anchor="w")
        self.otp_entry = ttk.Entry(self.otp_frame, font=("Segoe UI", 16), width=12, justify="center")
        self.otp_entry.pack(anchor="w", pady=(8, 18))

        button_row = ttk.Frame(self.otp_frame, style="Card.TFrame")
        button_row.pack(anchor="w")

        ttk.Button(
            button_row,
            text="Verify OTP",
            style="Primary.TButton",
            command=self.handle_otp_verification,
        ).pack(side="left", padx=(0, 10))

        ttk.Button(
            button_row,
            text="Back to Login",
            style="Secondary.TButton",
            command=self.show_login_frame,
        ).pack(side="left")

        self.otp_status = ttk.Label(self.otp_frame, text="", style="Status.TLabel")
        self.otp_status.pack(anchor="w", pady=(18, 0))

    def show_login_frame(self) -> None:
        self.otp_frame.pack_forget()
        self.login_frame.pack(fill="both", expand=True)
        self.password_entry.delete(0, tk.END)
        self.otp_entry.delete(0, tk.END)
        self.login_status.config(text="")
        self.otp_status.config(text="")

    def show_otp_frame(self) -> None:
        self.login_frame.pack_forget()
        self.otp_frame.pack(fill="both", expand=True)
        self.otp_entry.focus_set()

    def handle_login(self) -> None:
        username = self.username_entry.get().strip()
        password = self.password_entry.get()

        try:
            result = self.auth_manager.authenticate_password(username, password)
        except HashingError as exc:
            messagebox.showerror("Hashing Error", str(exc))
            return

        self.login_status.config(text=result.message)

        if result.locked:
            messagebox.showerror("Account Locked", result.message)
            return

        if not result.success:
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
        self.otp_status.config(text=result.message)

        if result.success:
            messagebox.showinfo("Access Granted", result.message)
            self.show_login_frame()
            self.username_entry.delete(0, tk.END)
            return

        messagebox.showerror("OTP Verification Failed", result.message)


def main() -> None:
    app = SecureAuthApp()
    app.mainloop()


if __name__ == "__main__":
    main()
