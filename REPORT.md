# Project Report: Secure Authentication Framework for Operating Systems

## 1. Project Overview
The Secure Authentication Framework for Operating Systems is an academic project designed to demonstrate how modern authentication features can be integrated into an operating-system-inspired security workflow. The project combines three layers:

- a graphical user interface built with Python Tkinter
- an authentication engine implemented in Python
- a system-level hashing module written in C

The goal is to simulate a secure login process that verifies user credentials, generates a one-time password for multi-factor authentication, and protects accounts from brute-force attacks through login attempt restrictions.

## 2. Module-Wise Breakdown

### 2.1 User Interface Module
The user interface is implemented in `auth_ui.py` using Tkinter and `ttk`. It provides:

- a login screen for username and password input
- an OTP verification screen for second-factor validation
- success, warning, and error messages
- a simple modern layout with separate content areas

### 2.2 Authentication Module
The authentication logic is implemented in `auth.py`. This module is responsible for:

- loading and storing user data in JSON format
- validating usernames and passwords
- invoking the C hashing executable through `subprocess`
- generating a random 4-digit OTP
- verifying OTP values
- tracking failed login attempts
- locking accounts after 3 incorrect password entries

### 2.3 Security Module
The security module is implemented in `hash.c`. This module:

- receives a password and salt from Python
- applies a custom iterative hashing process
- returns a fixed hexadecimal digest
- acts as the low-level hashing component in the project

Although the hashing logic is custom and educational, it demonstrates cross-language integration between Python and C, which supports the operating-system level simulation requirement of the project.

## 3. Functionalities
The project supports the following core functionalities:

- secure login using username and password
- password hashing with salt instead of plain-text password storage
- OTP-based second-factor authentication
- failure notifications for invalid credentials
- runtime lockout after 3 failed password attempts
- modular separation of frontend, business logic, and low-level security logic

## 4. Technologies Used
- Python 3
- Tkinter for graphical user interface
- JSON for simple user record persistence
- C language for hashing implementation
- GCC for compiling the C program
- `subprocess` module for Python-to-C execution
- `unittest` for backend testing

## 5. Flow Diagram
```text
[Login Screen]
      |
      v
[Enter Username + Password]
      |
      v
[Check Username Exists]
      |
      v
[Send Password + Salt to C Hash Program]
      |
      v
[Compare Computed Hash with Stored Hash]
      |
 +----+----+
 |         |
 v         v
Yes        No
 |          |
 v          v
[Generate OTP]   [Increase Failed Attempts]
 |               |
 v               v
[OTP Screen]   [Attempts >= 3 ?]
 |               |
 v               v
[Verify OTP]   [Lock Account]
 | 
 +----+----+
 |         |
 v         v
Yes        No
 |          |
 v          v
[Access Granted] [Authentication Failed]
```

## 6. Conclusion
This project demonstrates a complete and modular authentication workflow suitable for an academic operating systems project. It brings together user interface development, authentication logic, secure storage practices, low-level systems programming, and software testing. The project is intentionally simple enough for student understanding while still showing important concepts such as password hashing, OTP verification, and brute-force protection.

## 7. Future Scope
The project can be extended in several ways:

- replace the custom hashing algorithm with Argon2 or bcrypt
- store users in SQLite or PostgreSQL instead of JSON
- send OTP values through email or SMS APIs
- implement time-based OTP using authenticator apps
- persist account lock status across application restarts
- add audit logging for security monitoring
- package the UI as a desktop installer

## Execution Guide

### Compile the Hashing Module
```powershell
gcc hash.c -o hash.exe
```

### Run the Application
```powershell
python auth_ui.py
```

### Run Test Cases
```powershell
python -m unittest test_auth.py
```

## Testing Summary

### Test Case 1: Correct Login
- Input: valid username and password
- Expected Result: OTP is generated and correct OTP grants access

### Test Case 2: Wrong Password
- Input: valid username and wrong password
- Expected Result: failure message with remaining attempts

### Test Case 3: Wrong OTP
- Input: valid password and invalid OTP
- Expected Result: OTP verification fails and access is denied

### Test Case 4: Account Lock Scenario
- Input: wrong password entered three times
- Expected Result: account is locked and further login attempts are rejected
