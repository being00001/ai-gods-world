const API = {
  state: "/api/mvp/state?limit=50",
  turn: "/api/mvp/turn",
  reset: "/api/mvp/reset",
};

const state = {
  snapshot: null,
  logs: [],
};

const els = {
  status: document.getElementById("status-window"),
  logs: document.getElementById("turn-log"),
  msg: document.getElementById("message-box"),
};

function setMessage(text) {
  els.msg.textContent = text;
}

function randomHumanAction() {
  const actions = ["pray", "preach", "doubt"];
  const index = Math.floor(Math.random() * actions.length);
  return actions[index];
}

function pickHumanActionForAiTarget(target) {
  const current = state.snapshot;
  if (!current) return randomHumanAction();

  if (target === "meditate") {
    if ((current.human?.faith || 0) >= 2) return "doubt";
    return "pray";
  }

  if (target === "smite") {
    if ((current.human?.faith || 0) > 0) return "preach";
    return "pray";
  }

  if (target === "tempt") {
    return "pray";
  }

  return randomHumanAction();
}

async function fetchJson(url, options) {
  const response = await fetch(url, options);
  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.error || "request failed");
  }
  return data;
}

function render() {
  const snapshot = state.snapshot || {};

  const statusLines = [
    `turn: ${snapshot.turn ?? "-"}`,
    `phase: ${snapshot.phase ?? "-"}`,
    `winner: ${snapshot.winner ?? "none"}`,
    "",
    "[human]",
    `faith: ${snapshot.human?.faith ?? "-"}`,
    `influence: ${snapshot.human?.influence ?? "-"}`,
    `followers: ${snapshot.human?.followers ?? "-"}`,
    "",
    "[ai_god]",
    `divine_power: ${snapshot.ai_god?.divine_power ?? "-"}`,
    `wrath: ${snapshot.ai_god?.wrath ?? "-"}`,
    `followers: ${snapshot.ai_god?.followers ?? "-"}`,
    "",
    `log_count: ${snapshot.log_count ?? 0}`,
  ];

  els.status.textContent = statusLines.join("\n");

  if (!state.logs.length) {
    els.logs.textContent = "no logs";
    return;
  }

  const logLines = state.logs.map((log, i) => {
    const details = JSON.stringify(log.details || {});
    return `${i + 1}. T${log.turn} ${log.actor}:${log.action} ${details}`;
  });
  els.logs.textContent = logLines.join("\n");
}

async function refreshState() {
  const data = await fetchJson(API.state);
  state.snapshot = data.state || null;
  state.logs = data.logs || [];
  render();
}

async function processTurn(humanAction, sourceLabel) {
  setMessage(`${sourceLabel} -> human_action=${humanAction}`);
  const result = await fetchJson(API.turn, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ action: humanAction }),
  });

  state.snapshot = result.state || state.snapshot;
  state.logs = result.logs || state.logs;

  const aiAction = result.ai_action || "none";
  const winner = result.state?.winner || "none";
  setMessage(`turn=${result.turn} human=${result.human_action} ai=${aiAction} winner=${winner}`);

  render();
}

async function resetMvp() {
  setMessage("resetting...");
  const data = await fetchJson(API.reset, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
  });

  state.snapshot = data.state || null;
  state.logs = data.logs || [];
  setMessage("reset complete");
  render();
}

function bindEvents() {
  document.querySelectorAll("[data-human-action]").forEach((button) => {
    button.addEventListener("click", async () => {
      const rawAction = button.dataset.humanAction;
      const action = rawAction === "random" ? randomHumanAction() : rawAction;
      try {
        await processTurn(action, `human:${rawAction}`);
      } catch (error) {
        setMessage(`error: ${error.message}`);
      }
    });
  });

  document.querySelectorAll("[data-ai-target]").forEach((button) => {
    button.addEventListener("click", async () => {
      const target = button.dataset.aiTarget;
      const action = pickHumanActionForAiTarget(target);
      try {
        await processTurn(action, `ai-target:${target}`);
      } catch (error) {
        setMessage(`error: ${error.message}`);
      }
    });
  });

  document.getElementById("refresh-state").addEventListener("click", async () => {
    try {
      await refreshState();
      setMessage("state refreshed");
    } catch (error) {
      setMessage(`error: ${error.message}`);
    }
  });

  document.getElementById("reset-mvp").addEventListener("click", async () => {
    try {
      await resetMvp();
    } catch (error) {
      setMessage(`error: ${error.message}`);
    }
  });
}

document.addEventListener("DOMContentLoaded", async () => {
  bindEvents();
  try {
    await refreshState();
    setMessage("ready");
  } catch (error) {
    setMessage(`error: ${error.message}`);
  }
});
