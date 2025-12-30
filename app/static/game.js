const gid = window.location.pathname.split("/").pop();
let currentTurn = null;
let myNation = null;

// === Pobierz szczegóły gry ===
async function loadGame() {
  const res = await fetch(`/api/games/${gid}`);
  const data = await res.json();
  if (!data.ok) {
    alert("Failed to load game.");
    return;
  }

  document.getElementById("gameTitle").textContent = data.game.name;
  document.getElementById("status").textContent = data.game.status;
  const playersDiv = document.getElementById("players");
  const joinedPlayers = data.nations.filter(n => n.user_id);
  if (!joinedPlayers.length) {
    playersDiv.innerHTML = "<p>No players joined yet.</p>";
    return;
  }
  playersDiv.innerHTML = joinedPlayers.map(n => `
    <div class="player">
        <strong>${n.name}</strong> — User ID: ${n.user_id}
    </div>`).join("");
  const turns = data.turns;
  currentTurn = turns[turns.length - 1];
  document.getElementById("turn").textContent = `${currentTurn.phase} ${currentTurn.number+1900}`;

  const nationRes = await fetch(`/api/me`);
  const me = await nationRes.json();
  if (me.ok) {
    const nation = data.nations.find(n => n.user_id === me.user.id);
    console.log(nation);
    if (nation) {
      myNation = nation;
      document.getElementById("myNation").textContent = nation.name;
    } else {
      document.getElementById("myNation").textContent = "Fail to find your nation";
    }
  }

  loadOrders();
  loadMessages();
}

// === Rozkazy ===
async function loadOrders() {
  if (!myNation || !currentTurn) return;
  const res = await fetch(`/api/turns/${currentTurn.id}/orders`);
  const data = await res.json();
  if (data.ok) {
    const myOrders = data.orders.filter(o => o.player_id === myNation.id);
    document.getElementById("ordersList").innerHTML =
      myOrders.map(o => `<div>${o.payload}</div>`).join('') || "<p>No orders</p>";
  }
}

document.getElementById("orderForm").onsubmit = async (e) => {
  e.preventDefault();
  if (!myNation || !currentTurn) return alert("Nation or turn not loaded.");
  const payload = orderText.value.trim();
  const res = await fetch(`/api/turns/${currentTurn.id}/orders`, {
    method: "POST",
    headers: {"Content-Type":"application/json"},
    body: JSON.stringify({ player_id: myNation.id, payload })
  });
  const data = await res.json();
  if (data.ok) {
    orderText.value = "";
    loadOrders();
  } else alert(data.error || "Failed to send order.");
};

// === Wiadomości ===
async function loadMessages() {
  const res = await fetch(`/api/games/${gid}/messages`);
  const data = await res.json();
  if (data.ok) {
    const box = document.getElementById("messages");
    box.innerHTML = data.messages.map(m => `
      <div><strong>${m.sender_name}:</strong> ${m.text}</div>
    `).join('') || "<p>No messages</p>";
    box.scrollTop = box.scrollHeight;
  }
}

document.getElementById("msgForm").onsubmit = async (e) => {
  e.preventDefault();
  const text = msgText.value.trim();
  if (!text) return;
  const res = await fetch(`/api/games/${gid}/messages`, {
    method: "POST",
    headers: {"Content-Type":"application/json"},
    body: JSON.stringify({ text, sender_id: myNation?.id })
  });
  const data = await res.json();
  if (data.ok) {
    msgText.value = "";
    loadMessages();
  }
};

function backToLobby() {
  location.href = "/lobby";
}

loadGame();