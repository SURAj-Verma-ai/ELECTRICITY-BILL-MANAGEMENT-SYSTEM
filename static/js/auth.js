// Mirrors src/utils/validators.py rules for instant client-side feedback.
// The server re-validates everything; this is UX only, not a security boundary.

document.addEventListener("DOMContentLoaded", () => {
    const passwordInput = document.getElementById("password");
    const rulesList = document.getElementById("pw-rules");

    if (passwordInput && rulesList) {
        const rules = {
            length: (v) => v.length >= 8 && v.length <= 64,
            lower: (v) => /[a-z]/.test(v),
            upper: (v) => /[A-Z]/.test(v),
            digit: (v) => /[0-9]/.test(v),
            special: (v) => /[!@#$%^&*()_+\-=[\]{};':"\\|,.<>/?]/.test(v),
        };

        passwordInput.addEventListener("input", () => {
            const value = passwordInput.value;
            for (const [key, test] of Object.entries(rules)) {
                const li = rulesList.querySelector(`[data-rule="${key}"]`);
                if (li) li.classList.toggle("valid", test(value));
            }
        });
    }

    const usernameInput = document.getElementById("username");
    if (usernameInput) {
        usernameInput.setAttribute("maxlength", "20");
        usernameInput.addEventListener("input", () => {
            usernameInput.value = usernameInput.value.slice(0, 20);
        });
    }

    const confirmInput = document.getElementById("confirm_password");
    const form = document.querySelector("form[data-validate='register']");
    if (form && confirmInput) {
        form.addEventListener("submit", (e) => {
            if (passwordInput.value !== confirmInput.value) {
                e.preventDefault();
                alert("Passwords do not match.");
            }
        });
    }
});
