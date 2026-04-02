# Secure Authentication Framework for Operating Systems

## Project Overview
This project implements a modular authentication framework for an operating systems academic project. It combines a Python Tkinter user interface, a Python authentication service, and a C-based hashing utility to simulate a secure login flow with password verification, OTP-based multi-factor authentication, and brute-force protection.

## Folder Structure
```text
project/
├── auth.py
├── auth_ui.py
├── hash.c
├── requirements.txt
├── users.json
├── test_auth.py
├── README.md
└── REPORT.md
```

## Features
- Username and password login
- Password hashing through a C program called from Python
- 4-digit OTP verification after correct password entry  from my side  (viksh)
- Account lock after 3 failed password attempts
- JSON-based user storage with hashed passwords only
- Modular design with separated UI, authentication, and hashing layers

## Architecture
- `auth_ui.py`: Tkinter GUI for login and OTP verification
- `auth.py`: core backend logic for user validation, OTP creation, and lockout handling
- `hash.c`: custom hashing utility compiled to an executable and invoked by Python using `subprocess`
- `users.json`: persistent user storage using salts and hashed passwords

## Authentication Flow
```text
+-----------------+
| Start Login UI  |
+-----------------+
         |
         v
+-------------------------+
| Enter Username/Password |
+-------------------------+
         |
         v
+----------------------+
| Validate User Exists |
+----------------------+
         |
         v
+----------------------+
| Hash Entered Password |
| Using C Program       |
+----------------------+
         |
    +----+----+
    |         |
    v         v
 Password   Password
 Correct    Incorrect
    |           |
    v           v
+--------------+  +----------------------+
| Generate OTP |  | Increment Fail Count |
+--------------+  +----------------------+
    |                     |
    v                     v
+------------------+   +------------------+
| Enter 4-Digit OTP|   | Count >= 3 ?     |
+------------------+   +------------------+
    |                     |
    v                     v
+-------------------+   +------------------+
| Verify OTP        |   | Lock Account     |
+-------------------+   +------------------+
    |
 +--+--+
 |     |
 v     v
OTP   OTP
OK    Wrong/Expired
 |        |
 v        v
+--------------+   +----------------------+
| Access Granted|  | Re-enter Login Flow  |
+--------------+   +----------------------+
```

## Default Users
The application seeds these demo accounts automatically when `users.json` does not exist:

- `admin` / `SecurePass123`
- `student` / `OsProject@2026`

Passwords are never stored in plain text. Only the generated salt and hash are stored.

## How to Compile the C Program

### Windows with MinGW GCC
```powershell
gcc hash.c -o hash.exe
```

### Linux or macOS with GCC
```bash
gcc hash.c -o hash
```

## How to Run the Project
1. Compile the C hashing utility first.
2. Run the Tkinter application:

```powershell
python auth_ui.py
```

## How to Run Tests
```powershell
python -m unittest test_auth.py
```

## Sample Test Cases
1. Correct Login
   - Username: `admin`
   - Password: `SecurePass123`
   - Expected: OTP screen appears, correct OTP grants access

2. Wrong Password
   - Username: `admin`
   - Password: `WrongPassword`
   - Expected: error message and remaining attempts decrease

3. Wrong OTP
   - Username: `admin`
   - Password: `SecurePass123`
   - OTP: `0000`
   - Expected: OTP verification failure

4. Account Lock Scenario
   - Username: `student`
   - Password: incorrect password entered three times
   - Expected: account lock message and future logins denied

## Dependencies
- Python 3.10 or above
- GCC compiler for building the C executable
- Tkinter, included with standard Python installations

## GitHub Workflow

### Suggested Commit Messages
1. `Initialize secure authentication project structure`
2. `Add C-based password hashing utility`
3. `Implement Python authentication service and lockout rules`
4. `Build Tkinter login and OTP verification interface`
5. `Add seeded user storage with hashed credentials`
6. `Write automated tests and validation scenarios`
7. `Document architecture, usage, and project report`

### Steps to Push to GitHub
1. Initialize Git:
   ```powershell
   git init
   ```
2. Add files:
   ```powershell
   git add .
   ```
3. Create the first commit:
   ```powershell
   git commit -m "Initialize secure authentication project structure"
   ```
4. Create a GitHub repository from the browser.
5. Connect the local repository to GitHub:
   ```powershell
   git remote add origin https://github.com/your-username/secure-auth-os.git
   ```
6. Push the code:
   ```powershell
   git branch -M main
   git push -u origin main
   ```

## Important Note
This project uses a custom educational hash implemented in C to satisfy the academic systems integration requirement. In a real production environment, a standard password hashing algorithm such as Argon2, bcrypt, or scrypt should be used instead of custom hashing logic........................
