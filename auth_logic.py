import argparse
import json
import secrets
import sys
import time

from auth import HashService, HashingError


OTP_VALIDITY_SECONDS = 120


def write_json(payload: dict, status: int = 0) -> None:
    print(json.dumps(payload))
    raise SystemExit(status)


def command_generate_salt(args: argparse.Namespace) -> None:
    username = args.username.strip()
    if not username:
        write_json({"ok": False, "error": "Username is required."}, 1)

    write_json({"ok": True, "salt": secrets.token_hex(8)})


def command_hash_password(args: argparse.Namespace) -> None:
    try:
        digest = HashService().hash_password(args.password, args.salt)
    except HashingError as exc:
        write_json({"ok": False, "error": str(exc)}, 1)

    write_json({"ok": True, "passwordHash": digest})


def command_verify_password(args: argparse.Namespace) -> None:
    try:
        digest = HashService().hash_password(args.password, args.salt)
    except HashingError as exc:
        write_json({"ok": False, "error": str(exc)}, 1)

    write_json({"ok": True, "valid": secrets.compare_digest(digest, args.password_hash)})


def command_generate_otp(_args: argparse.Namespace) -> None:
    otp = f"{secrets.randbelow(9000) + 1000}"
    write_json(
        {
            "ok": True,
            "otp": otp,
            "expiresAt": time.time() + OTP_VALIDITY_SECONDS,
            "expiresInSeconds": OTP_VALIDITY_SECONDS,
        }
    )


def command_verify_otp(args: argparse.Namespace) -> None:
    if time.time() > args.expires_at:
        write_json({"ok": True, "valid": False, "expired": True})

    valid = secrets.compare_digest(args.otp.strip(), args.expected_otp.strip())
    write_json({"ok": True, "valid": valid, "expired": False})


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Authentication logic bridge for the web backend.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    salt_parser = subparsers.add_parser("generate-salt")
    salt_parser.add_argument("--username", required=True)
    salt_parser.set_defaults(func=command_generate_salt)

    hash_parser = subparsers.add_parser("hash-password")
    hash_parser.add_argument("--password", required=True)
    hash_parser.add_argument("--salt", required=True)
    hash_parser.set_defaults(func=command_hash_password)

    verify_password_parser = subparsers.add_parser("verify-password")
    verify_password_parser.add_argument("--password", required=True)
    verify_password_parser.add_argument("--salt", required=True)
    verify_password_parser.add_argument("--password-hash", required=True)
    verify_password_parser.set_defaults(func=command_verify_password)

    otp_parser = subparsers.add_parser("generate-otp")
    otp_parser.set_defaults(func=command_generate_otp)

    verify_otp_parser = subparsers.add_parser("verify-otp")
    verify_otp_parser.add_argument("--otp", required=True)
    verify_otp_parser.add_argument("--expected-otp", required=True)
    verify_otp_parser.add_argument("--expires-at", required=True, type=float)
    verify_otp_parser.set_defaults(func=command_verify_otp)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    try:
        args.func(args)
    except Exception as exc:
        write_json({"ok": False, "error": str(exc)}, 1)


if __name__ == "__main__":
    main()
