const thread = document.getElementById("thread");
const input  = document.getElementById("input");
const send   = document.getElementById("send");

/* The agent replies in light markdown: **bold** names and "- " bullets.
   Plain text would show literal asterisks; innerHTML would execute model
   output as markup. So we parse into real DOM nodes and only ever set text
   via textContent — safe by construction, and the formatting still renders. */
function inline(text, parent) {
  text.split(/\*\*(.+?)\*\*/g).forEach((part, i) => {
    if (!part) return;                 // skip empties but keep index parity
    if (i % 2 === 1) {
      const b = document.createElement("strong");
      b.textContent = part;
      parent.appendChild(b);
    } else {
      parent.appendChild(document.createTextNode(part));
    }
  });
}

function bubble(who, text) {
  const el = document.createElement("div");
  el.className = `msg ${who}`;

  // The model often runs bullets inline rather than on their own lines.
  const lines = text
    .replace(/\s+[-•*]\s+(?=\*\*)/g, "\n- ")
    .split("\n").map((l) => l.trim()).filter(Boolean);

  let list = null;
  lines.forEach((line) => {
    if (/^[-•]\s/.test(line) || /^\*\s/.test(line)) {
      if (!list) { list = document.createElement("ul"); el.appendChild(list); }
      const li = document.createElement("li");
      inline(line.replace(/^[-•*]\s+/, ""), li);
      list.appendChild(li);
    } else {
      list = null;                     // a normal line closes the list
      const p = document.createElement("p");
      inline(line, p);
      el.appendChild(p);
    }
  });

  thread.appendChild(el);
  thread.scrollTop = thread.scrollHeight;
  return el;
}

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
    bubble("them", "The front desk is offline. Start the server and try again.");
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

/* Chips fill the composer rather than sending. On camera this matters: you
   click, the question appears in the input, then you press send — so the
   viewer sees a person asking rather than text materialising in the thread. */
document.querySelectorAll("#chips button").forEach((btn) => {
  btn.addEventListener("click", () => {
    input.value = btn.textContent.trim();
    input.focus();
  });
});

/* Scroll reveal — toggles rather than unobserving, so it reverses on scroll up. */
const io = new IntersectionObserver((entries) => {
  entries.forEach((e) => e.target.classList.toggle("seen", e.isIntersecting));
}, { threshold: 0.15, rootMargin: "0px 0px -8% 0px" });
document.querySelectorAll(".reveal").forEach((n) => io.observe(n));
