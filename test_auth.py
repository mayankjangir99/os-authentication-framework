import unittest

from auth import AuthenticationManager, BASE_DIR, HashService, UserStore


class AuthenticationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.hash_service = HashService()
        self.user_store = UserStore(file_path=BASE_DIR / "users.json", hash_service=self.hash_service)
        self.user_store.initialize_if_missing()
        self.manager = AuthenticationManager(self.user_store, self.hash_service)
        self.manager.reset_runtime_state()

    def test_correct_login_and_otp(self) -> None:
        result = self.manager.authenticate_password("admin", "SecurePass123")
        self.assertTrue(result.success)
        self.assertTrue(result.requires_otp)

        otp = self.manager.get_current_otp_for_demo("admin")
        otp_result = self.manager.verify_otp("admin", otp)
        self.assertTrue(otp_result.success)

    def test_wrong_password(self) -> None:
        result = self.manager.authenticate_password("admin", "WrongPassword")
        self.assertFalse(result.success)
        self.assertIn("Invalid password", result.message)

    def test_wrong_otp(self) -> None:
        login_result = self.manager.authenticate_password("admin", "SecurePass123")
        self.assertTrue(login_result.success)

        otp_result = self.manager.verify_otp("admin", "0000")
        self.assertFalse(otp_result.success)
        self.assertIn("Incorrect OTP", otp_result.message)

    def test_account_lock_after_three_failures(self) -> None:
        for _ in range(3):
            result = self.manager.authenticate_password("student", "bad-pass")

        self.assertFalse(result.success)
        self.assertTrue(result.locked)
        locked_result = self.manager.authenticate_password("student", "OsProject@2026")
        self.assertTrue(locked_result.locked)


if __name__ == "__main__":
    unittest.main()
