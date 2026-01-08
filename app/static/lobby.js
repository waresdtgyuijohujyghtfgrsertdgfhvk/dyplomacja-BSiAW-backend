let selectedGameId = null;

  document.getElementById("logoutBtn").addEventListener("click", async () => {
    await fetch("/api/logout", { method: "POST" });
    window.location.href = "/login";
  });

  async function loadGames() {
    const res = await fetch("/api/games");
    const data = await res.json();
    if (!data.ok) {
      alert("Failed to load games.");
      return;
    }

    const list = document.getElementById("gamesList");
    if (!data.data.length) {
      list.innerHTML = "<p>No games available yet. Create one to get started!</p>";
      return;
    }

    list.innerHTML = data.data.map(g => `
      <div class="card">
        <h3>${g.name}</h3>
        <p>Status: ${g.status}</p>
        <p>Started at: ${new Date(g.started_at).toLocaleString()}</p>
        <button name="${g.id}">Join</button>
        <div id="nations-${g.id}" class="nations"></div>
      </div>
    `).join('');
    for (let button of list.getElementsByTagName("button")) {
      button.addEventListener("click",()=>openJoinModal(button.name))
    }
    for (const g of data.data) loadNations(g.id);
  }

  async function loadNations(gameId) {
    const res = await fetch(`/api/games/${gameId}`);
    const data = await res.json();
    if (!data.ok) return;

    const div = document.getElementById(`nations-${gameId}`);
    div.innerHTML = data.nations.map(n => `
      <span class="nation ${n.user_id ? 'taken' : 'free'}">
        ${n.name} ${n.user_id ? '(taken)' : '(free)'}
      </span>
    `).join('');
  }

  async function openJoinModal(gameId) {
    selectedGameId = gameId;
    console.log("Joining game:", selectedGameId);

    const [gameRes, meRes] = await Promise.all([
      fetch(`/api/games/${gameId}`),
      fetch(`/api/me`)
    ]);

    const gameData = await gameRes.json();
    const meData = await meRes.json();

    if (!gameData.ok || !meData.ok) {
      alert("Failed to load game or user info.");
      return;
    }

    if (gameData.nations.some(n => String(n.user_id) === String(meData.user.id))) {
      window.location.href = `/game/${gameId}`;
      return;
    }

    const available = gameData.nations.filter(n => !n.user_id);
    if (!available.length) {
      alert("No nations left to join!");
      return;
    }

    const select = document.getElementById("nationSelect");
    select.innerHTML = available.map(n => `<option value="${n.name}">${n.name}</option>`).join("");

    document.getElementById("joinModal").style.display = "flex";
  }

  document.getElementById("confirmJoin").addEventListener("click", async () => {
    if (!selectedGameId) {
      alert("Error: no game selected.");
      return;
    }

    const nationName = document.getElementById("nationSelect").value;
    if (!nationName) return;

    console.log("Joining as:", nationName, "to game:", selectedGameId);

    const res = await fetch(`/api/games/${selectedGameId}/nations`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name: nationName })
    });
    const data = await res.json();

    if (data.ok) {

      alert(`You joined as ${nationName}!`);
      const res = await fetch(`/api/games/${selectedGameId}`);
      window.location.href = `/game/${selectedGameId}`;
    } else {
      alert(data.error || "Failed to join game.");
    }
  });

  async function createGame() {
    const name = prompt("Enter a name for the new game:");
    if (!name) return;

    const res = await fetch("/api/games", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name })
    });
    const data = await res.json();

    if (data.ok) {
      alert("Game created successfully!");
      loadGames();
    } else {
      alert(data.error || "Failed to create game.");
    }
  }

  document.getElementById("createGameBtn").addEventListener("click", createGame);
  loadGames();