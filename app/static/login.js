document.getElementById("loginForm").onsubmit = async (e) => {
  e.preventDefault();
  const res = await fetch("/api/login", {
    method: "POST",
    headers: {"Content-Type":"application/json"},
    body: JSON.stringify({
      username: username.value,
      password: password.value
    })
  });
  const data = await res.json();
  if (data.ok) {
    location.href = "/lobby";
  } else {
    msg.textContent = data.error || "Login failed";
  }
};