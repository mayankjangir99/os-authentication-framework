const express = require("express");
const mongoose = require("mongoose");
const path = require("path");
const crypto = require("crypto");
const { spawn } = require("child_process");

const app = express();
const PORT = Number(process.env.PORT || 3000);
const MONGODB_URI = process.env.MONGODB_URI || "mongodb://127.0.0.1:27017/secure_auth_os";
const PYTHON_BIN = process.env.PYTHON_BIN || "python";
const PYTHON_LOGIC = path.join(__dirname, "auth_logic.py");
const JWT_SECRET = process.env.JWT_SECRET || "secure-auth-os-demo-secret-change-me";
const JWT_EXPIRES_IN_SECONDS = Number(process.env.JWT_EXPIRES_IN_SECONDS || 3600);
const MAX_ATTEMPTS = 3;

const defaultUsers = [
  { username: "admin", password: "SecurePass123" },
  { username: "student", password: "OsProject@2026" },
];

const userSchema = new mongoose.Schema(
  {
    username: { type: String, unique: true, required: true, trim: true },
    salt: { type: String, required: true },
    passwordHash: { type: String, required: true },
    failedAttempts: { type: Number, default: 0 },
    locked: { type: Boolean, default: false },
    pendingOtp: { type: String, default: "" },
    otpExpiresAt: { type: Date, default: null },
  },
  { timestamps: true }
);

const User = mongoose.model("User", userSchema);

app.use(express.json());
app.use(express.static(path.join(__dirname, "public")));

function base64Url(input) {
  return Buffer.from(input)
    .toString("base64")
    .replace(/=/g, "")
    .replace(/\+/g, "-")
    .replace(/\//g, "_");
}

function decodeBase64Url(input) {
  const padded = input.padEnd(input.length + ((4 - (input.length % 4)) % 4), "=");
  return Buffer.from(padded.replace(/-/g, "+").replace(/_/g, "/"), "base64").toString("utf8");
}

function signJwt(payload, expiresInSeconds = JWT_EXPIRES_IN_SECONDS) {
  const issuedAt = Math.floor(Date.now() / 1000);
  const header = { alg: "HS256", typ: "JWT" };
  const body = {
    ...payload,
    iat: issuedAt,
    exp: issuedAt + expiresInSeconds,
  };
  const unsignedToken = `${base64Url(JSON.stringify(header))}.${base64Url(JSON.stringify(body))}`;
  const signature = crypto.createHmac("sha256", JWT_SECRET).update(unsignedToken).digest("base64url");

  return {
    token: `${unsignedToken}.${signature}`,
    expiresAt: body.exp,
  };
}

function verifyJwt(token) {
  const parts = String(token || "").split(".");
  if (parts.length !== 3) {
    throw new Error("Invalid token format.");
  }

  const [encodedHeader, encodedPayload, signature] = parts;
  const unsignedToken = `${encodedHeader}.${encodedPayload}`;
  const expectedSignature = crypto.createHmac("sha256", JWT_SECRET).update(unsignedToken).digest("base64url");

  if (
    signature.length !== expectedSignature.length ||
    !crypto.timingSafeEqual(Buffer.from(signature), Buffer.from(expectedSignature))
  ) {
    throw new Error("Invalid token signature.");
  }

  const payload = JSON.parse(decodeBase64Url(encodedPayload));
  if (!payload.exp || Math.floor(Date.now() / 1000) >= payload.exp) {
    throw new Error("Token has expired.");
  }

  return payload;
}

function authenticateJwt(request, response, next) {
  const authHeader = request.headers.authorization || "";
  const [scheme, token] = authHeader.split(" ");

  if (scheme !== "Bearer" || !token) {
    response.status(401).json({ ok: false, message: "JWT token is required." });
    return;
  }

  try {
    request.auth = verifyJwt(token);
    next();
  } catch (error) {
    response.status(401).json({ ok: false, message: error.message });
  }
}

function runPython(command, args = {}) {
  const cliArgs = [PYTHON_LOGIC, command];

  for (const [key, value] of Object.entries(args)) {
    cliArgs.push(`--${key}`);
    cliArgs.push(String(value));
  }

  return new Promise((resolve, reject) => {
    const child = spawn(PYTHON_BIN, cliArgs, { cwd: __dirname });
    let stdout = "";
    let stderr = "";

    child.stdout.on("data", (chunk) => {
      stdout += chunk.toString();
    });

    child.stderr.on("data", (chunk) => {
      stderr += chunk.toString();
    });

    child.on("error", reject);
    child.on("close", (code) => {
      let payload;
      try {
        payload = JSON.parse(stdout.trim() || "{}");
      } catch (error) {
        reject(new Error(stderr.trim() || "Python logic returned invalid JSON."));
        return;
      }

      if (code !== 0 || payload.ok === false) {
        reject(new Error(payload.error || stderr.trim() || "Python logic failed."));
        return;
      }

      resolve(payload);
    });
  });
}

async function seedDefaultUsers() {
  for (const account of defaultUsers) {
    const existing = await User.findOne({ username: account.username });
    if (existing) {
      continue;
    }

    const saltResult = await runPython("generate-salt", { username: account.username });
    const hashResult = await runPython("hash-password", {
      password: account.password,
      salt: saltResult.salt,
    });

    await User.create({
      username: account.username,
      salt: saltResult.salt,
      passwordHash: hashResult.passwordHash,
    });
  }
}

app.get("/api/health", (_request, response) => {
  response.json({
    ok: true,
    service: "secure-auth-os-web",
    database: mongoose.connection.readyState === 1 ? "connected" : "disconnected",
  });
});

app.post("/api/login", async (request, response) => {
  try {
    const username = String(request.body.username || "").trim();
    const password = String(request.body.password || "");

    if (!username || !password) {
      response.status(400).json({ ok: false, message: "Username and password are required." });
      return;
    }

    const user = await User.findOne({ username });
    if (!user) {
      response.status(404).json({ ok: false, message: "User does not exist." });
      return;
    }

    if (user.locked) {
      response.status(423).json({ ok: false, locked: true, message: "Account is locked after 3 failed attempts." });
      return;
    }

    const verifyResult = await runPython("verify-password", {
      password,
      salt: user.salt,
      "password-hash": user.passwordHash,
    });

    if (!verifyResult.valid) {
      user.failedAttempts += 1;

      if (user.failedAttempts >= MAX_ATTEMPTS) {
        user.locked = true;
        await user.save();
        response.status(423).json({
          ok: false,
          locked: true,
          remainingAttempts: 0,
          message: "Invalid password. Account has been locked.",
        });
        return;
      }

      await user.save();
      response.status(401).json({
        ok: false,
        remainingAttempts: MAX_ATTEMPTS - user.failedAttempts,
        message: `Invalid password. ${MAX_ATTEMPTS - user.failedAttempts} attempt(s) remaining.`,
      });
      return;
    }

    const otpResult = await runPython("generate-otp");
    user.failedAttempts = 0;
    user.pendingOtp = otpResult.otp;
    user.otpExpiresAt = new Date(otpResult.expiresAt * 1000);
    await user.save();

    response.json({
      ok: true,
      requiresOtp: true,
      username: user.username,
      demoOtp: otpResult.otp,
      expiresInSeconds: otpResult.expiresInSeconds,
      message: "Password verified. OTP has been generated.",
    });
  } catch (error) {
    response.status(500).json({ ok: false, message: error.message });
  }
});

app.post("/api/verify-otp", async (request, response) => {
  try {
    const username = String(request.body.username || "").trim();
    const otp = String(request.body.otp || "").trim();

    if (!username || !otp) {
      response.status(400).json({ ok: false, message: "Username and OTP are required." });
      return;
    }

    const user = await User.findOne({ username });
    if (!user || !user.pendingOtp || !user.otpExpiresAt) {
      response.status(400).json({ ok: false, message: "No active OTP session. Please log in again." });
      return;
    }

    const verifyResult = await runPython("verify-otp", {
      otp,
      "expected-otp": user.pendingOtp,
      "expires-at": user.otpExpiresAt.getTime() / 1000,
    });

    if (verifyResult.expired) {
      user.pendingOtp = "";
      user.otpExpiresAt = null;
      await user.save();
      response.status(401).json({ ok: false, expired: true, message: "OTP expired. Please log in again." });
      return;
    }

    if (!verifyResult.valid) {
      response.status(401).json({ ok: false, message: "Incorrect OTP. Please try again." });
      return;
    }

    user.pendingOtp = "";
    user.otpExpiresAt = null;
    await user.save();

    const jwt = signJwt({
      sub: user.id,
      username: user.username,
      scope: "dashboard:read",
    });

    response.json({
      ok: true,
      message: "Authentication successful. Access granted.",
      token: jwt.token,
      tokenType: "Bearer",
      expiresAt: jwt.expiresAt,
      expiresInSeconds: JWT_EXPIRES_IN_SECONDS,
      username: user.username,
    });
  } catch (error) {
    response.status(500).json({ ok: false, message: error.message });
  }
});

app.get("/api/dashboard", authenticateJwt, async (request, response) => {
  const user = await User.findById(request.auth.sub).select("username failedAttempts locked updatedAt createdAt");

  if (!user) {
    response.status(404).json({ ok: false, message: "Token user no longer exists." });
    return;
  }

  response.json({
    ok: true,
    username: user.username,
    issuedAt: request.auth.iat,
    expiresAt: request.auth.exp,
    scope: request.auth.scope,
    message: "Secure dashboard loaded with JWT authentication.",
  });
});

app.get("*", (_request, response) => {
  response.sendFile(path.join(__dirname, "public", "index.html"));
});

async function start() {
  await mongoose.connect(MONGODB_URI);
  await seedDefaultUsers();

  app.listen(PORT, () => {
    console.log(`Secure Auth web app running at http://localhost:${PORT}`);
  });
}

start().catch((error) => {
  console.error(error);
  process.exit(1);
});
