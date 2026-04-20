const loginForm = document.querySelector("#loginForm");
const otpForm = document.querySelector("#otpForm");
const loginMessage = document.querySelector("#loginMessage");
const otpMessage = document.querySelector("#otpMessage");
const otpDemo = document.querySelector("#otpDemo");
const passwordStep = document.querySelector("#passwordStep");
const otpStep = document.querySelector("#otpStep");
const connectionStatus = document.querySelector("#connectionStatus");
const togglePassword = document.querySelector("#togglePassword");
const passwordInput = document.querySelector("#password");
const usernameInput = document.querySelector("#username");
const otpInput = document.querySelector("#otp");
const backToLogin = document.querySelector("#backToLogin");

let activeUsername = "";

async function requestJson(url, options = {}) {
  const response = await fetch(url, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
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
  loginForm.classList.remove("hidden");
  passwordStep.classList.add("is-active");
  otpStep.classList.remove("is-active");
  otpInput.value = "";
  setMessage(otpMessage, "");
  usernameInput.focus();
}

function showOtp() {
  loginForm.classList.add("hidden");
  otpForm.classList.remove("hidden");
  passwordStep.classList.remove("is-active");
  otpStep.classList.add("is-active");
  otpInput.focus();
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

    setMessage(otpMessage, result.message, "success");
    passwordInput.value = "";
    window.setTimeout(showLogin, 900);
  } catch (error) {
    setMessage(otpMessage, error.message, "error");
  }
});

checkHealth();
