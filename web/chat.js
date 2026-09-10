const thread = document.getElementById("thread");
const input  = document.getElementById("input");
const send   = document.getElementById("send");

/* Append one bubble. `who` is "me" or "them". */
function bubble(who, text) {
  const el = document.createElement("div");
  el.className = `msg ${who}`;
  const p = document.createElement("p");
  p.textContent = text;              // textContent, not innerHTML -- never render
  el.appendChild(p);                 // model output as markup
  thread.appendChild(el);
  thread.scrollTop = thread.scrollHeight;
  return el;
}

/* Three blinking dots while the agent works. Returned so we can remove it. */
function typing() {
  const el = document.createElement("div");
  el.className = "msg them typing";
  el.innerHTML = "<p><span></span><span></span><span></span></p>";
  thread.appendChild(el);
  thread.scrollTop = thread.scrollHeight;
  return el;
}

async function ask(message) {
  bubble("me", message);
  input.value = "";
  send.disabled = true;
  const dots = typing();

  try {
    const res = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message }),
    });
    const data = await res.json();
    dots.remove();
    bubble("them", data.reply);
  } catch (err) {
    dots.remove();
    bubble("them", "Sorry — I couldn't reach the server just then. Try again?");
  } finally {
    send.disabled = false;
    input.focus();
  }
}

send.addEventListener("click", () => {
  if (input.value.trim()) ask(input.value.trim());
});
input.addEventListener("keydown", (e) => {
  if (e.key === "Enter" && input.value.trim()) ask(input.value.trim());
});

/* Suggestion chips -- makes the demo repeatable without typing on camera. */
document.querySelectorAll("#suggestions button").forEach((btn) => {
  btn.addEventListener("click", () => ask(btn.textContent.trim()));
});
