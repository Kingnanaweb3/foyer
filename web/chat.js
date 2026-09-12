const thread = document.getElementById("thread");
const input  = document.getElementById("input");
const send   = document.getElementById("send");

/* The model replies in light markdown -- **bold** and "- " bullets. Rendering
   it as raw text shows literal asterisks; rendering it via innerHTML would
   execute model output as markup. So we parse it into real DOM nodes and set
   text with textContent only. Safe by construction, still looks right. */
function renderInline(text, parent) {
  // split on **bold** runs, keeping the captured group
  text.split(/\*\*(.+?)\*\*/g).forEach((part, i) => {
    if (!part) return;
    if (i % 2 === 1) {
      const b = document.createElement("strong");
      b.textContent = part;
      parent.appendChild(b);
    } else {
      parent.appendChild(document.createTextNode(part));
    }
  });
}

/* Append one bubble. `who` is "me" or "them". */
function bubble(who, text) {
  const el = document.createElement("div");
  el.className = `msg ${who}`;

  // Normalise: the model sometimes runs bullets inline instead of on new lines.
  const normalised = text.replace(/\s+-\s+\*\*/g, "\n- **");
  const lines = normalised.split("\n").map((l) => l.trim()).filter(Boolean);

  let list = null;
  lines.forEach((line) => {
    if (line.startsWith("- ")) {
      if (!list) { list = document.createElement("ul"); el.appendChild(list); }
      const li = document.createElement("li");
      renderInline(line.slice(2), li);
      list.appendChild(li);
    } else {
      list = null;                   // a non-bullet line closes the list
      const p = document.createElement("p");
      renderInline(line, p);
      el.appendChild(p);
    }
  });

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
