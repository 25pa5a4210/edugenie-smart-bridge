/**
 * Handles the login and registration forms. Included on both pages;
 * each block checks for its form's existence before wiring up.
 */
(function () {
  // If already logged in, skip straight to dashboard
  if (EduGenieAPI.getToken()) {
    window.location.href = "dashboard.html";
    return;
  }

  function setLoading(btn, textEl, loading, loadingLabel, defaultLabel) {
    btn.disabled = loading;
    textEl.innerHTML = loading
      ? `<span class="spinner"></span> ${loadingLabel}`
      : defaultLabel;
  }

  // ---------------- Login ----------------
  const loginForm = document.getElementById("loginForm");
  if (loginForm) {
    loginForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      document.getElementById("formError").textContent = "";
      const email = document.getElementById("email").value.trim();
      const password = document.getElementById("password").value;

      if (!email || !password) {
        document.getElementById("formError").textContent = "Please enter your email and password.";
        return;
      }

      const btn = document.getElementById("submitBtn");
      const textEl = document.getElementById("submitText");
      setLoading(btn, textEl, true, "Logging in...", "Log In");

      try {
        const data = await EduGenieAPI.login({ email, password });
        EduGenieAPI.setToken(data.access_token);
        EduGenieAPI.setUser(data.user);
        EduGenieUI.toast("Welcome back!", "success");
        window.location.href = "dashboard.html";
      } catch (err) {
        document.getElementById("formError").textContent = err.message;
        setLoading(btn, textEl, false, "", "Log In");
      }
    });
  }

  // ---------------- Register ----------------
  const registerForm = document.getElementById("registerForm");
  if (registerForm) {
    const passwordInput = document.getElementById("password");
    const strengthFill = document.getElementById("strengthFill");

    passwordInput.addEventListener("input", () => {
      const val = passwordInput.value;
      let score = 0;
      if (val.length >= 8) score++;
      if (/[A-Z]/.test(val)) score++;
      if (/[0-9]/.test(val)) score++;
      if (/[^A-Za-z0-9]/.test(val)) score++;

      const pct = (score / 4) * 100;
      const colors = ["#E8735F", "#E8735F", "#F2B84B", "#4FB6A8", "#5FBF7A"];
      strengthFill.style.width = `${pct}%`;
      strengthFill.style.background = colors[score];
    });

    registerForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      ["full_nameError", "emailError", "academic_levelError", "confirm_passwordError", "formError"].forEach(
        (id) => (document.getElementById(id).textContent = "")
      );

      const full_name = document.getElementById("full_name").value.trim();
      const email = document.getElementById("email").value.trim();
      const academic_level = document.getElementById("academic_level").value;
      const password = document.getElementById("password").value;
      const confirm_password = document.getElementById("confirm_password").value;

      let hasError = false;
      if (full_name.length < 2) {
        document.getElementById("full_nameError").textContent = "Please enter your full name.";
        hasError = true;
      }
      if (!/^\S+@\S+\.\S+$/.test(email)) {
        document.getElementById("emailError").textContent = "Please enter a valid email address.";
        hasError = true;
      }
      if (!academic_level) {
        document.getElementById("academic_levelError").textContent = "Please select your academic level.";
        hasError = true;
      }
      if (password !== confirm_password) {
        document.getElementById("confirm_passwordError").textContent = "Passwords do not match.";
        hasError = true;
      }
      if (hasError) return;

      const btn = document.getElementById("submitBtn");
      const textEl = document.getElementById("submitText");
      setLoading(btn, textEl, true, "Creating account...", "Create Account");

      try {
        const data = await EduGenieAPI.register({
          full_name,
          email,
          password,
          confirm_password,
          academic_level,
        });
        EduGenieAPI.setToken(data.access_token);
        EduGenieAPI.setUser(data.user);
        EduGenieUI.toast("Account created! Welcome to EduGenie.", "success");
        window.location.href = "dashboard.html";
      } catch (err) {
        document.getElementById("formError").textContent = err.message;
        setLoading(btn, textEl, false, "", "Create Account");
      }
    });
  }
})();
