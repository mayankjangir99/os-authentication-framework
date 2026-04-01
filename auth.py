import json
import random
import subprocess
import sys
import time
from dataclasses import dataclass
from json import JSONDecodeError
from pathlib import Path
from typing import Dict, Optional, Tuple


BASE_DIR = Path(__file__).resolve().parent
USERS_FILE = BASE_DIR / "users.json"
HASH_EXECUTABLE = BASE_DIR / ("hash.exe" if sys.platform.startswith("win") else "hash")


class HashingError(Exception):
    """Raised when the hashing service cannot process a password."""


class HashService:
    """Wraps the C hashing executable used by the authentication layer."""

    def __init__(self, executable_path: Path = HASH_EXECUTABLE) -> None:
        self.executable_path = executable_path

    def is_available(self) -> bool:
        return self.executable_path.exists()

    def hash_password(self, password: str, salt: str) -> str:
        if not self.is_available():
            raise HashingError(
                f"Hash executable not found at {self.executable_path}. Compile hash.c first."
            )

        try:
            completed = subprocess.run(
                [str(self.executable_path), password, salt],
                check=True,
                capture_output=True,
                text=True,
            )
        except subprocess.CalledProcessError as exc:
            raise HashingError(exc.stderr.strip() or "Failed to hash password.") from exc
        except OSError as exc:
            raise HashingError(str(exc)) from exc

        return completed.stdout.strip()


class UserStore:
    """Stores and retrieves user authentication records from a JSON file."""

    DEFAULT_USERS = {
        "admin": "SecurePass123",
        "student": "OsProject@2026",
    }

    def __init__(self, file_path: Path, hash_service: HashService) -> None:
        self.file_path = file_path
        self.hash_service = hash_service

    def initialize_if_missing(self) -> None:
        if self.file_path.exists():
            existing_users = self._read_users()
            if existing_users:
                return

        users: Dict[str, Dict[str, str]] = {}
        for username, plain_password in self.DEFAULT_USERS.items():
            salt = self._generate_salt(username)
            users[username] = {
                "salt": salt,
                "password_hash": self.hash_service.hash_password(plain_password, salt),
            }

        self._write_users(users)

    def get_user(self, username: str) -> Optional[Dict[str, str]]:
        data = self._read_users()
        return data.get(username)

    def _read_users(self) -> Dict[str, Dict[str, str]]:
        if not self.file_path.exists():
            return {}
        try:
            with self.file_path.open("r", encoding="utf-8") as file:
                data = json.load(file)
                return data if isinstance(data, dict) else {}
        except JSONDecodeError:
            return {}

    def _write_users(self, users: Dict[str, Dict[str, str]]) -> None:
        with self.file_path.open("w", encoding="utf-8") as file:
            json.dump(users, file, indent=2)

    @staticmethod
    def _generate_salt(username: str) -> str:
        seed = f"{username}-auth-salt"
        return seed.encode("utf-8").hex()[:12]


@dataclass
class AuthResult:
    success: bool
    message: str
    requires_otp: bool = False
    locked: bool = False
    remaining_attempts: int = 0


class AuthenticationManager:
    """Coordinates password validation, OTP generation, and lockout rules."""

    def __init__(self, user_store: UserStore, hash_service: HashService) -> None:
        self.user_store = user_store
        self.hash_service = hash_service
        self.max_attempts = 3
        self.otp_validity_seconds = 120
        self.failed_attempts: Dict[str, int] = {}
        self.locked_accounts: Dict[str, bool] = {}
        self.pending_otps: Dict[str, Tuple[str, float]] = {}

    def authenticate_password(self, username: str, password: str) -> AuthResult:
        username = username.strip()
        if not username or not password:
            return AuthResult(False, "Username and password are required.")

        if self.locked_accounts.get(username, False):
            return AuthResult(False, "Account is locked after 3 failed attempts.", locked=True)

        user = self.user_store.get_user(username)
        if user is None:
            return AuthResult(False, "User does not exist.")

        hashed_input = self.hash_service.hash_password(password, user["salt"])
        if hashed_input != user["password_hash"]:
            attempt_count = self.failed_attempts.get(username, 0) + 1
            self.failed_attempts[username] = attempt_count
            remaining = self.max_attempts - attempt_count

            if attempt_count >= self.max_attempts:
                self.locked_accounts[username] = True
                return AuthResult(
                    False,
                    "Invalid password. Account has been locked.",
                    locked=True,
                    remaining_attempts=0,
                )

            return AuthResult(
                False,
                f"Invalid password. {remaining} attempt(s) remaining.",
                remaining_attempts=remaining,
            )

        self.failed_attempts[username] = 0
        otp = self._generate_otp()
        self.pending_otps[username] = (otp, time.time() + self.otp_validity_seconds)
        return AuthResult(True, "Password verified. OTP has been generated.", requires_otp=True)

    def get_current_otp_for_demo(self, username: str) -> Optional[str]:
        otp_record = self.pending_otps.get(username)
        if not otp_record:
            return None
        return otp_record[0]

    def verify_otp(self, username: str, otp_input: str) -> AuthResult:
        record = self.pending_otps.get(username)
        if record is None:
            return AuthResult(False, "No active OTP session. Please log in again.")

        otp_value, expires_at = record
        if time.time() > expires_at:
            self.pending_otps.pop(username, None)
            return AuthResult(False, "OTP expired. Please log in again.")

        if otp_input.strip() != otp_value:
            return AuthResult(False, "Incorrect OTP. Please try again.")

        self.pending_otps.pop(username, None)
        return AuthResult(True, "Authentication successful. Access granted.")

    def reset_runtime_state(self) -> None:
        self.failed_attempts.clear()
        self.locked_accounts.clear()
        self.pending_otps.clear()

    @staticmethod
    def _generate_otp() -> str:
        return f"{random.randint(1000, 9999)}"


def build_authentication_manager() -> AuthenticationManager:
    hash_service = HashService()
    user_store = UserStore(USERS_FILE, hash_service)
    user_store.initialize_if_missing()
    return AuthenticationManager(user_store, hash_service)


if __name__ == "__main__":
    manager = build_authentication_manager()
    print("Authentication backend initialized successfully.")
