const loginForm = document.querySelector("#loginForm");
const otpForm = document.querySelector("#otpForm");
const loginMessage = document.querySelector("#loginMessage");
const otpMessage = document.querySelector("#otpMessage");
const otpDemo = document.querySelector("#otpDemo");
const passwordStep = document.querySelector("#passwordStep");
const otpStep = document.querySelector("#otpStep");
const dashboardStep = document.querySelector("#dashboardStep");
const connectionStatus = document.querySelector("#connectionStatus");
const togglePassword = document.querySelector("#togglePassword");
const passwordInput = document.querySelector("#password");
const usernameInput = document.querySelector("#username");
const otpInput = document.querySelector("#otp");
const backToLogin = document.querySelector("#backToLogin");
const dashboardCard = document.querySelector("#dashboardCard");
const dashboardWelcome = document.querySelector("#dashboardWelcome");
const dashboardStatus = document.querySelector("#dashboardStatus");
const protectedMessage = document.querySelector("#protectedMessage");
const jwtToken = document.querySelector("#jwtToken");
const tokenExpiry = document.querySelector("#tokenExpiry");
const copyToken = document.querySelector("#copyToken");
const logoutButton = document.querySelector("#logoutButton");

let activeUsername = "";

async function requestJson(url, options = {}) {
  const { headers: optionHeaders = {}, ...restOptions } = options;
  const response = await fetch(url, {
    headers: { "Content-Type": "application/json", ...optionHeaders },
    ...restOptions,
  });
  const contentType = response.headers.get("content-type") || "";

  if (!contentType.includes("application/json")) {
    throw new Error("Server returned the app page instead of API data. Restart the Node server and try again.");
  }

  const payload = await response.json().catch(() => ({}));

  if (!response.ok) {
    throw new Error(payload.message || "Request failed.");
  }

  return payload;
}

function setMessage(element, text, tone = "") {
  element.textContent = text;
  element.className = `message ${tone}`.trim();
}

function showLogin() {
  otpForm.classList.add("hidden");
  dashboardCard.classList.add("hidden");
  loginForm.classList.remove("hidden");
  passwordStep.classList.add("is-active");
  otpStep.classList.remove("is-active");
  dashboardStep.classList.remove("is-active");
  otpInput.value = "";
  setMessage(otpMessage, "");
  usernameInput.focus();
}

function showOtp() {
  loginForm.classList.add("hidden");
  dashboardCard.classList.add("hidden");
  otpForm.classList.remove("hidden");
  passwordStep.classList.remove("is-active");
  otpStep.classList.add("is-active");
  dashboardStep.classList.remove("is-active");
  otpInput.focus();
}

function showDashboard() {
  loginForm.classList.add("hidden");
  otpForm.classList.add("hidden");
  dashboardCard.classList.remove("hidden");
  passwordStep.classList.remove("is-active");
  otpStep.classList.remove("is-active");
  dashboardStep.classList.add("is-active");
}

function formatUnixTime(seconds) {
  if (!Number.isFinite(Number(seconds))) {
    return "Not available";
  }

  return new Date(seconds * 1000).toLocaleString();
}

async function loadDashboard(token) {
  if (!token || token === "undefined" || token.split(".").length !== 3) {
    localStorage.removeItem("secureAuthJwt");
    throw new Error("No valid JWT token found. Please verify OTP again.");
  }

  setMessage(dashboardStatus, "Opening secure dashboard...", "info");

  const dashboard = await requestJson("/api/dashboard", {
    headers: { Authorization: `Bearer ${token}` },
  });

  if (!dashboard.ok || !dashboard.username || !dashboard.expiresAt) {
    localStorage.removeItem("secureAuthJwt");
    throw new Error("Dashboard response was missing JWT session details. Please log in again.");
  }

  dashboardWelcome.textContent = `Welcome, ${dashboard.username}`;
  protectedMessage.textContent = dashboard.message || "Secure dashboard loaded.";
  tokenExpiry.textContent = formatUnixTime(dashboard.expiresAt);
  jwtToken.value = token;
  showDashboard();
  setMessage(
    dashboardStatus,
    `JWT scope: ${dashboard.scope || "dashboard:read"}. Issued at ${formatUnixTime(dashboard.issuedAt)}.`,
    "success"
  );
}

async function checkHealth() {
  try {
    const health = await requestJson("/api/health");
    connectionStatus.textContent = `Backend ready. MongoDB is ${health.database}.`;
    connectionStatus.className = "status-strip ok";
  } catch (error) {
    connectionStatus.textContent = error.message;
    connectionStatus.className = "status-strip error";
  }
}

togglePassword.addEventListener("click", () => {
  const visible = passwordInput.type === "text";
  passwordInput.type = visible ? "password" : "text";
  togglePassword.textContent = visible ? "Show" : "Hide";
});

backToLogin.addEventListener("click", showLogin);

copyToken.addEventListener("click", async () => {
  try {
    await navigator.clipboard.writeText(jwtToken.value);
    setMessage(dashboardStatus, "JWT token copied.", "success");
  } catch (error) {
    jwtToken.select();
    setMessage(dashboardStatus, "Token selected. Press Ctrl+C to copy it.", "info");
  }
});

logoutButton.addEventListener("click", () => {
  localStorage.removeItem("secureAuthJwt");
  activeUsername = "";
  jwtToken.value = "";
  passwordInput.value = "";
  showLogin();
  setMessage(loginMessage, "Logged out. Please sign in again.", "info");
});

loginForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  setMessage(loginMessage, "Checking credentials...", "info");

  const username = usernameInput.value.trim();
  const password = passwordInput.value;

  try {
    const result = await requestJson("/api/login", {
      method: "POST",
      body: JSON.stringify({ username, password }),
    });

    activeUsername = result.username;
    setMessage(loginMessage, result.message, "success");
    otpDemo.textContent = `Demo OTP for ${result.username}: ${result.demoOtp}. It expires in ${result.expiresInSeconds} seconds.`;
    showOtp();
  } catch (error) {
    setMessage(loginMessage, error.message, "error");
  }
});

otpForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  setMessage(otpMessage, "Verifying OTP...", "info");

  try {
    const result = await requestJson("/api/verify-otp", {
      method: "POST",
      body: JSON.stringify({ username: activeUsername, otp: otpInput.value }),
    });

    if (!result.token || result.token.split(".").length !== 3) {
      throw new Error("OTP verified, but the server did not return a JWT token. Restart the Node server and try again.");
    }

    localStorage.setItem("secureAuthJwt", result.token);
    setMessage(otpMessage, result.message, "success");
    passwordInput.value = "";
    await loadDashboard(result.token);
  } catch (error) {
    setMessage(otpMessage, error.message, "error");
  }
});

checkHealth();

const savedToken = localStorage.getItem("secureAuthJwt");
if (savedToken && savedToken !== "undefined") {
  loadDashboard(savedToken).catch((error) => {
    localStorage.removeItem("secureAuthJwt");
    setMessage(loginMessage, error.message, "error");
    showLogin();
  });
} else {
  localStorage.removeItem("secureAuthJwt");
}
