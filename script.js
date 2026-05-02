// ============================================================
// script.js — AI Trip Planner Chatbot Frontend Logic
// ============================================================
 
// ── Session ID (unique per browser tab) ─────────────────────
const SESSION_ID = "sess_" + Math.random().toString(36).substr(2, 9);
 
// ── DOM References ───────────────────────────────────────────
const messageArea  = document.getElementById("messageArea");
const userInput    = document.getElementById("userInput");
const sendBtn      = document.getElementById("sendBtn");
const micBtn       = document.getElementById("micBtn");
const resetBtn     = document.getElementById("resetBtn");
const quickBar     = document.getElementById("quickReplyBar");
const planModal    = document.getElementById("planModal");
const planBox      = document.getElementById("planBox");
 
// ── Voice Recognition setup ──────────────────────────────────
let recognition = null;
if ("webkitSpeechRecognition" in window || "SpeechRecognition" in window) {
  const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
  recognition = new SR();
  recognition.lang = "en-IN";
  recognition.continuous = false;
  recognition.interimResults = false;
 
  recognition.onresult = (e) => {
    userInput.value = e.results[0][0].transcript;
    micBtn.classList.remove("active");
  };
  recognition.onend = () => micBtn.classList.remove("active");
}
 
// ── Init ─────────────────────────────────────────────────────
window.addEventListener("load", showWelcome);
 
function showWelcome() {
  messageArea.innerHTML = "";
  clearQuickReplies();
 
  addBotMessage(
    `<div class="welcome-card">
      <h3>✈️ Hey there, Traveller!</h3>
      <p>I'm your <strong>AI Trip Planner</strong>. Tell me where you want to go and I'll create a <strong>complete personalised travel plan</strong> for you — itinerary, budget, hotels & tips!</p>
      <div class="example">"Plan a 5-day trip to Manali from Delhi under ₹15,000 for friends"</div>
      <div class="example">"7 days Leh Ladakh trip from Mumbai, budget ₹50,000 solo"</div>
      <div class="example">"Pondicherry from Bangalore, 3 days, couple trip, ₹10,000"</div>
      <div style="margin-top:10px;font-size:12px;color:#667;line-height:1.6"><b>✈️ 24 Destinations:</b> Goa · Manali · Jaipur · Kerala · Delhi · Agra · Shimla · Varanasi · Mumbai · Udaipur · Rishikesh · Ooty · Andaman · Amritsar · Darjeeling · Leh Ladakh · Mysore · Pondicherry · Spiti · Coorg · Pushkar · Hampi · Mussoorie · Kolkata</div>
    </div>`
  );
}
 
// ── Send message ─────────────────────────────────────────────
function sendMessage(text) {
  const msg = (text || userInput.value).trim();
  if (!msg) return;
 
  addUserMessage(msg);
  userInput.value = "";
  clearQuickReplies();
  showTyping();
 
  fetch("/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message: msg, session_id: SESSION_ID }),
  })
    .then((r) => r.json())
    .then((data) => {
      removeTyping();
      handleResponse(data);
    })
    .catch(() => {
      removeTyping();
      addBotMessage("⚠️ Oops! Couldn't connect to the server. Make sure Flask is running.");
    });
}
 
// ── Handle API response ──────────────────────────────────────
function handleResponse(data) {
  if (data.type === "followup") {
    addBotMessage(formatText(data.text));
    if (data.quick_replies && data.quick_replies.length) {
      showQuickReplies(data.quick_replies);
    }
  } else if (data.type === "plan") {
    addBotMessage("🎉 <strong>Your trip plan is ready!</strong> Click below to view it 👇");
    const viewBtn = document.createElement("button");
    viewBtn.className = "chip";
    viewBtn.style.margin = "4px 0 0 40px";
    viewBtn.innerHTML = "📋 View Full Trip Plan";
    viewBtn.onclick = () => openPlanModal(data.plan);
    messageArea.appendChild(viewBtn);
    scrollBottom();
  } else if (data.type === "error") {
    addBotMessage("❌ " + data.text);
  }
}
 
// ── Message Helpers ──────────────────────────────────────────
function addBotMessage(html) {
  const row = document.createElement("div");
  row.className = "msg-row bot";
  row.innerHTML = `
    <div class="msg-avatar"><i class="fas fa-robot"></i></div>
    <div class="bubble">${html}</div>`;
  messageArea.appendChild(row);
  scrollBottom();
}
 
function addUserMessage(text) {
  const row = document.createElement("div");
  row.className = "msg-row user";
  row.innerHTML = `<div class="bubble">${escapeHTML(text)}</div>`;
  messageArea.appendChild(row);
  scrollBottom();
}
 
function showTyping() {
  const row = document.createElement("div");
  row.className = "msg-row bot";
  row.id = "typingRow";
  row.innerHTML = `
    <div class="msg-avatar"><i class="fas fa-robot"></i></div>
    <div class="bubble">
      <div class="typing-indicator">
        <span></span><span></span><span></span>
      </div>
    </div>`;
  messageArea.appendChild(row);
  scrollBottom();
}
 
function removeTyping() {
  const t = document.getElementById("typingRow");
  if (t) t.remove();
}
 
function scrollBottom() {
  const c = document.getElementById("chatContainer");
  c.scrollTop = c.scrollHeight;
}
 
// ── Quick Replies ────────────────────────────────────────────
function showQuickReplies(replies) {
  clearQuickReplies();
  replies.forEach((r) => {
    const chip = document.createElement("button");
    chip.className = "chip";
    chip.textContent = r;
    chip.onclick = () => sendMessage(r);
    quickBar.appendChild(chip);
  });
}
 
function clearQuickReplies() { quickBar.innerHTML = ""; }
 
// ── Plan Modal ───────────────────────────────────────────────
function openPlanModal(plan) {
  planBox.innerHTML = buildPlanHTML(plan);
  planModal.classList.add("open");
  planBox.scrollTop = 0;
}
 
function closePlanModal() { planModal.classList.remove("open"); }
 
// Close modal on overlay click
planModal.addEventListener("click", (e) => {
  if (e.target === planModal) closePlanModal();
});
 
// ── Build HTML for plan modal ────────────────────────────────
function buildPlanHTML(p) {
  const bb = p.budget_breakdown;
  const withinBudget = bb.within_budget;
 
  // ── Header ──────────────────────────────────────────────
  let html = `
  <div class="plan-header">
    <button class="close-btn" onclick="closePlanModal()">✕</button>
    <h2>${p.travel_emoji} ${p.destination} Trip Plan</h2>
    <p>${p.description}</p>
    <div class="plan-meta">
      <span class="meta-chip">📅 ${p.days} Days</span>
      <span class="meta-chip">💰 ₹${p.budget.toLocaleString()} Budget</span>
      <span class="meta-chip">👥 ${capitalize(p.travel_type)}</span>
      <span class="meta-chip">🎯 ${capitalize(p.vibe)}</span>
    </div>
  </div>
  <div class="plan-body">`;
 
  // ── Best Time ────────────────────────────────────────────
  html += `
  <div>
    <div class="section-title"><i class="fas fa-calendar-alt"></i> Best Time to Visit</div>
    <div class="best-time-banner">
      <i class="fas fa-sun" style="font-size:20px"></i>
      <span>${p.best_time}</span>
    </div>
  </div>`;
 
  // ── Budget Breakdown ─────────────────────────────────────
  html += `
  <div>
    <div class="section-title"><i class="fas fa-wallet"></i> Budget Breakdown</div>
    <div class="budget-grid">
      <div class="budget-item">
        <div class="bi-label">✈️ Travel${p.source_city ? `<br><small style="font-size:10px;color:#888;font-weight:400">${p.source_city} → ${p.destination}</small>` : ''}</div>
        <div class="bi-value">₹${bb.travel.toLocaleString()}</div>
      </div>
      <div class="budget-item">
        <div class="bi-label">🏨 Hotel</div>
        <div class="bi-value">₹${bb.hotel.toLocaleString()}</div>
      </div>
      <div class="budget-item">
        <div class="bi-label">🍽️ Food</div>
        <div class="bi-value">₹${bb.food.toLocaleString()}</div>
      </div>
      <div class="budget-item">
        <div class="bi-label">🎡 Activities</div>
        <div class="bi-value">₹${bb.activities.toLocaleString()}</div>
      </div>
      <div class="budget-item">
        <div class="bi-label">🚖 Transport</div>
        <div class="bi-value">₹${bb.local_transport.toLocaleString()}</div>
      </div>
    </div>
    <div class="budget-total">
      <span>Total Estimated Cost</span>
      <div style="display:flex;align-items:center;gap:10px">
        <span style="font-size:20px">₹${bb.total.toLocaleString()}</span>
        <span class="budget-status ${withinBudget ? "status-ok" : "status-over"}">
          ${withinBudget ? "✅ Within Budget" : "⚠️ Over Budget"}
        </span>
      </div>
    </div>
  </div>`;
 
  // ── Day-wise Itinerary ───────────────────────────────────
  html += `<div><div class="section-title"><i class="fas fa-map-marked-alt"></i> Day-wise Itinerary</div>`;
  p.itinerary.forEach((day) => {
    html += `
    <div class="day-card" style="margin-bottom:12px">
      <div class="day-header"><i class="fas fa-sun"></i> Day ${day.day} — ${day.title}</div>
      <div class="day-body">`;
 
    // Places
    day.places.forEach((place) => {
      html += `
      <div class="place-row">
        <i class="fas fa-map-marker-alt place-icon"></i>
        <div class="place-info">
          <h4>${place.name}</h4>
          <p>${place.desc}</p>
        </div>
        <a href="${place.map}" target="_blank"><i class="fas fa-external-link-alt"></i> Map</a>
      </div>`;
    });
 
    // Activities
    if (day.activities.length) {
      html += `<div class="day-tags">`;
      day.activities.forEach((a) => {
        html += `<span class="tag activity"><i class="fas fa-bolt"></i> ${a}</span>`;
      });
      html += `</div>`;
    }
 
    // Food
    if (day.food.length) {
      html += `<div class="day-tags">`;
      day.food.forEach((f) => {
        html += `<span class="tag food"><i class="fas fa-utensils"></i> ${f}</span>`;
      });
      html += `</div>`;
    }
 
    html += `</div></div>`;
  });
  html += `</div>`;
 
  // ── Hotel Recommendations ────────────────────────────────
  html += `<div><div class="section-title"><i class="fas fa-hotel"></i> Hotel Recommendations</div>
  <div class="hotel-grid">`;
 
  const tiers = ["budget", "midrange", "luxury"];
  const tierLabels = { budget: "Budget", midrange: "Mid-Range", luxury: "Luxury" };
  const tierClasses = { budget: "tier-budget", midrange: "tier-midrange", luxury: "tier-luxury" };
 
  tiers.forEach((tier) => {
    p.hotels[tier].forEach((h) => {
      const isRec = tier === p.hotels.recommended_tier;
      html += `
      <div class="hotel-card ${isRec ? "recommended" : ""}">
        <span class="hotel-tier-badge ${tierClasses[tier]}">${tierLabels[tier]}${isRec ? " ⭐ Recommended" : ""}</span>
        <h4>${h.name}</h4>
        <p>📍 ${h.area} &nbsp;|&nbsp; ⭐ ${h.rating}</p>
        <div class="hotel-price">₹${h.price_per_night.toLocaleString()}<span style="font-size:11px;font-weight:400;color:var(--muted)"> / night</span></div>
      </div>`;
    });
  });
  html += `</div></div>`;
 
  // ── Travel Tips ──────────────────────────────────────────
  html += `<div><div class="section-title"><i class="fas fa-lightbulb"></i> Travel Tips</div>
  <div class="tips-list">`;
  [...p.tips, ...p.travel_tips].forEach((tip) => {
    html += `<div class="tip-row"><i class="fas fa-check-circle"></i><span>${tip}</span></div>`;
  });
  html += `</div></div>`;
 
  // ── Map Link ─────────────────────────────────────────────
  html += `<div><div class="section-title"><i class="fas fa-globe"></i> Location</div>
  <a href="${p.map_link}" target="_blank" class="action-btn primary" style="display:inline-flex;text-decoration:none">
    <i class="fas fa-map-marked-alt"></i> Open ${p.destination} on Google Maps
  </a></div>`;
 
  html += `</div>`; // end plan-body
 
  // ── Action Buttons ───────────────────────────────────────
  html += `
  <div class="plan-actions">
    <button class="action-btn outline" onclick="closePlanModal()">
      <i class="fas fa-arrow-left"></i> Back to Chat
    </button>
    <button class="action-btn primary" onclick="printPlan()">
      <i class="fas fa-print"></i> Print / Save PDF
    </button>
    <button class="action-btn outline" onclick="startNewTrip()">
      <i class="fas fa-plus"></i> Plan Another Trip
    </button>
  </div>`;
 
  return html;
}
 
// ── Actions ──────────────────────────────────────────────────
function printPlan() { window.print(); }
 
function startNewTrip() {
  closePlanModal();
  fetch("/reset", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ session_id: SESSION_ID }),
  });
  showWelcome();
}
 
// ── Event Listeners ──────────────────────────────────────────
sendBtn.addEventListener("click", () => sendMessage());
 
userInput.addEventListener("keydown", (e) => {
  if (e.key === "Enter" && !e.shiftKey) sendMessage();
});
 
resetBtn.addEventListener("click", startNewTrip);
 
micBtn.addEventListener("click", () => {
  if (!recognition) {
    addBotMessage("🎤 Voice input is not supported in this browser. Try Chrome!");
    return;
  }
  if (micBtn.classList.contains("active")) {
    recognition.stop();
    micBtn.classList.remove("active");
  } else {
    recognition.start();
    micBtn.classList.add("active");
    addBotMessage("🎤 Listening... Speak your trip details now.");
  }
});
 
// ── Utility ──────────────────────────────────────────────────
function escapeHTML(str) {
  return str.replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;");
}
 
function capitalize(str) {
  return str ? str.charAt(0).toUpperCase() + str.slice(1) : "";
}
 
// Convert **bold** and line breaks in bot messages
function formatText(text) {
  return text
    .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")
    .replace(/\n/g, "<br>");
}