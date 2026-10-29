const difficultyEl = document.getElementById("difficulty");
const newGameBtn = document.getElementById("new-game");
const patternEl = document.getElementById("pattern");
const messageEl = document.getElementById("message");
const remainingEl = document.getElementById("remaining");
const guessedEl = document.getElementById("guessed");
const incorrectEl = document.getElementById("incorrect");
const keyboardEl = document.getElementById("keyboard");

const PART_IDS = [
  "part-head",
  "part-body",
  "part-arm-l",
  "part-arm-r",
  "part-leg-l",
  "part-leg-r",
];

let gameId = null;
let busy = false;

function letters() {
  return "abcdefghijklmnopqrstuvwxyz".split("");
}

function buildKeyboard() {
  keyboardEl.innerHTML = "";
  for (const letter of letters()) {
    const button = document.createElement("button");
    button.type = "button";
    button.className = "key";
    button.dataset.letter = letter;
    button.textContent = letter;
    button.addEventListener("click", () => submitGuess(letter));
    keyboardEl.appendChild(button);
  }
}

function setMessage(text, kind) {
  messageEl.textContent = text;
  messageEl.classList.remove("won", "lost");
  if (kind) {
    messageEl.classList.add(kind);
  }
}

function listText(items) {
  return items.length ? items.join(" ").toUpperCase() : "—";
}

function updateDrawing(remaining) {
  const misses = 6 - remaining;
  PART_IDS.forEach((id, index) => {
    document.getElementById(id).classList.toggle("visible", index < misses);
  });
}

function updateKeyboard(state) {
  const guessed = new Set(state.guessed_letters || []);
  const incorrect = new Set(state.incorrect_letters || []);
  const over = state.status !== "playing";
  for (const button of keyboardEl.querySelectorAll(".key")) {
    const letter = button.dataset.letter;
    button.classList.remove("correct", "incorrect");
    if (incorrect.has(letter)) {
      button.classList.add("incorrect");
    } else if (guessed.has(letter)) {
      button.classList.add("correct");
    }
    button.disabled = over || guessed.has(letter);
  }
}

function render(state) {
  patternEl.textContent = state.pattern;
  remainingEl.textContent = String(state.remaining_guesses);
  guessedEl.textContent = listText(state.guessed_letters || []);
  incorrectEl.textContent = listText(state.incorrect_letters || []);
  updateDrawing(state.remaining_guesses);
  updateKeyboard(state);

  if (state.status === "won") {
    setMessage(`You won! The word was ${state.word}.`, "won");
  } else if (state.status === "lost") {
    setMessage(`You lost. The word was ${state.word}.`, "lost");
  } else {
    setMessage("");
  }
}

async function api(path, options) {
  const response = await fetch(path, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  const body = await response.json().catch(() => ({}));
  if (!response.ok) {
    throw new Error(body.error || `Request failed (${response.status})`);
  }
  return body;
}

async function startGame() {
  if (busy) {
    return;
  }
  busy = true;
  setMessage("Starting…");
  try {
    const state = await api("/api/games", {
      method: "POST",
      body: JSON.stringify({ difficulty: difficultyEl.value }),
    });
    gameId = state.game_id;
    render(state);
  } catch (error) {
    setMessage(error.message, "lost");
  } finally {
    busy = false;
  }
}

async function submitGuess(letter) {
  if (!gameId || busy) {
    return;
  }
  busy = true;
  try {
    const state = await api(`/api/games/${gameId}/guess`, {
      method: "POST",
      body: JSON.stringify({ letter }),
    });
    render(state);
  } catch (error) {
    setMessage(error.message, "lost");
  } finally {
    busy = false;
  }
}

newGameBtn.addEventListener("click", startGame);

document.addEventListener("keydown", (event) => {
  if (event.metaKey || event.ctrlKey || event.altKey) {
    return;
  }
  const letter = event.key.toLowerCase();
  if (letter.length === 1 && letter >= "a" && letter <= "z") {
    submitGuess(letter);
  }
});

buildKeyboard();
startGame();
