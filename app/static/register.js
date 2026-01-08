document.getElementById("registerForm").onsubmit = async (e) => {
  e.preventDefault();
  const res = await fetch("/api/register", {
    method: "POST",
    headers: {"Content-Type":"application/json"},
    body: JSON.stringify({
      username: username.value,
      password: password.value
    })
  });
  const data = await res.json();
  if (data.ok) {
    location.href = "/login";
  } else {
    msg.textContent = data.error || "Registration failed";
  }
};