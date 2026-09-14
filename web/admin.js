const queueEl = document.getElementById("queue");
const logEl   = document.getElementById("log");
const countEl = document.getElementById("pending-count");

function el(tag, cls, text) {
  const n = document.createElement(tag);
  if (cls) n.className = cls;
  if (text !== undefined) n.textContent = text;
  return n;
}

const INFO = `<svg width="15" height="15" viewBox="0 0 24 24" fill="none"
  stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
  <circle cx="12" cy="12" r="10"/><path d="M12 16v-4"/><path d="M12 8h.01"/></svg>`;

function renderCard(item) {
  const card = el("div", `card ${item.status === "pending" ? "pending" : ""}`);

  const top = el("div", "card-top");
  top.appendChild(el("span", "id", `${item.action_type} · ${item.id}`));
  top.appendChild(el("span", `badge ${item.status}`, item.status));
  card.appendChild(top);

  // reasoning above the draft: it's why the draft exists
  const why = el("div", "why");
  why.innerHTML = INFO;
  why.appendChild(el("span", null, item.reason));
  card.appendChild(why);

  card.appendChild(el("div", "draft", item.content));

  if (item.status === "pending") {
    const actions = el("div", "actions");
    const go = el("button", "pill go", "Approve and send");
    go.addEventListener("click", () => decide(item.id, "approved"));
    const no = el("button", "pill no", "Reject");
    no.addEventListener("click", () => decide(item.id, "rejected"));
    actions.append(go, no);
    card.appendChild(actions);
  }
  return card;
}

const deciding = new Set();

async function decide(id, decision) {
  if (deciding.has(id)) return;   // guard the double click before it leaves
  deciding.add(id);
  await fetch(`${window.FOYER_API}/api/approvals/${id}/${decision}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ note: "" }),
  });
  deciding.delete(id);
  refresh();
}

async function refresh() {
  try {
    const [aRes, lRes] = await Promise.all([
      fetch(`${window.FOYER_API}/api/approvals`), fetch(`${window.FOYER_API}/api/log`),
    ]);
    const { pending } = await aRes.json();
    const { entries } = await lRes.json();

    countEl.textContent = pending.length;

    queueEl.replaceChildren();
    if (pending.length === 0) {
      queueEl.appendChild(el("p", "empty",
        "Nothing waiting. Foyer handled everything else on its own."));
    } else {
      pending.forEach((item) => queueEl.appendChild(renderCard(item)));
    }

    logEl.replaceChildren();
    if (entries.length === 0) {
      logEl.appendChild(el("p", "empty", "No activity yet."));
    } else {
      const list = el("div", "log");
      entries.forEach((e) => {
        const row = el("div", "row");
        row.appendChild(el("div", "when", new Date(e.timestamp).toLocaleString()));
        const what = el("div", "what");
        what.appendChild(el("strong", null, e.action));
        what.appendChild(el("span", null, e.reason));
        what.appendChild(el("div", "actor", e.agent));
        row.appendChild(what);
        list.appendChild(row);
      });
      logEl.appendChild(list);
    }
  } catch (err) {
    queueEl.replaceChildren(el("p", "empty",
      "Can't reach the server. Start it with: uvicorn server:app --reload"));
  }
}

refresh();
setInterval(refresh, 4000);
