const params = new URLSearchParams(window.location.search);

const email = params.get("email") || "unknown@email.com";
const otpValue = params.get("otp") || "";
const otpLength = otpValue.length;

// show email
document.getElementById("emailDisplay").textContent = email;

// build OTP inputs
const otpContainer = document.getElementById("otpContainer");

for (let i = 0; i < otpLength; i++) {
  const input = document.createElement("input");
  input.className = "otp-box";
  input.maxLength = 1;

  input.addEventListener("input", (e) => {
    if (e.target.value && e.target.nextElementSibling) {
      e.target.nextElementSibling.focus();
    }
  });

  otpContainer.appendChild(input);
}

// toggle password
document.getElementById("togglePassword").addEventListener("change", function () {
  const input = document.getElementById("newPassword");
  input.type = this.checked ? "text" : "password";
});

// save button
document.getElementById("saveBtn").addEventListener("click", () => {
  const inputs = document.querySelectorAll(".otp-box");

  let otp = "";
  inputs.forEach(i => otp += i.value);

  const password = document.getElementById("newPassword").value;

  handleSave(otp, password);
});

function handleSave(otp, password) {
  // backend logic later
}