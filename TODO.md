# TODO — Web-Based Hangman

## Assignment scope

Build and deploy a playable Hangman game with a Flask backend and browser-based HTML/CSS/JavaScript client.

### Required
1. Game engine and word management
2. Flask server and REST API
3. Browser-based client
4. Testing and debugging
5. Cloud deployment

### Out of scope — do not implement
- [x] Human terminal client (`terminal_client.py`)
- [x] Automated/student bots and bot progression (`bot_examples/`)
- [x] Evaluation mode and evaluation endpoints
- [x] Official scoring system
- [x] Leaderboards
- [x] Evaluation anti-cheat, idle timeout, and evaluation rate limiting
- [x] Logging/replay features and endpoints
- [x] Future extensions such as multiplayer, accounts, tournaments, and bot competitions

The original `SPECIFICATION.md` also describes those out-of-scope features. For this reduced assignment, follow its game-engine, REST API, browser-client, game-rules, and word-list requirements only. The instructor's Cursor transcript was not present in the uploaded project materials available for this review, so this plan does not attribute additional requirements to that transcript.

## Implementation rules
- Complete one phase at a time; do not generate the entire application in one step.
- Keep the game engine independent of Flask and the browser.
- The Flask server is authoritative for game state and guesses.
- Never send the hidden word to the browser while a game is `playing`.
- Add and run relevant tests in each phase before marking its verification complete.

---

## Phase 1 — Game engine and word management

- [x] Create `game.py` with a UI- and Flask-independent `HangmanGame`.
- [x] Keep the answer private during active play.
- [x] Track guesses, incorrect guesses, remaining attempts, and game status.
- [x] Enforce one English letter per guess and reject duplicate guesses.
- [x] Enforce six incorrect guesses and prevent guesses after game completion.
- [x] Reveal the answer only after a win or loss.
- [x] Create Easy, Medium, and Hard word lists under `words/`.
- [x] Load and validate word lists; remove duplicates and select random words by difficulty.
- [x] Add engine and word-manager unit tests.
- [x] Harden input validation to English A–Z and validate the incorrect-guess limit.
- [ ] Re-run all Phase 1 tests after the latest validation changes.

**Current status:** Implemented; final regression run pending.

## Phase 2 — Flask server and REST API

- [x] Create the Flask app in `server.py`.
- [x] Store active games in server memory and generate unique game IDs.
- [x] Implement `POST /api/games`.
- [x] Implement `GET /api/games/{game_id}`.
- [x] Implement `POST /api/games/{game_id}/guess`.
- [x] Accept/return JSON and validate request bodies, difficulty, and guesses.
- [x] Return appropriate success and error status codes, including 400 and 404.
- [x] Ensure active-game API responses do not expose the answer.
- [x] Serve the browser application from `/`.
- [x] Add API tests.
- [ ] Run API tests in an environment with the declared Flask dependency installed.

**Current status:** Implemented; API test execution is environment-blocked until Flask is installed.

## Phase 3 — Browser-based client

- [x] Create `static/index.html`, `static/style.css`, and `static/app.js`.
- [x] Provide Easy, Medium, and Hard difficulty selection and a New Game button.
- [x] Display the masked word, guessed letters, and remaining incorrect guesses.
- [x] Provide on-screen and physical-keyboard letter input.
- [x] Update the Hangman drawing after incorrect guesses.
- [x] Display win/loss messages and allow a new game without reloading.
- [x] Use `fetch()` to communicate with the REST API; keep game logic and answer on the server.
- [ ] Manually verify complete browser gameplay against a running Flask server.
- [ ] Verify browser error states and responsive layout in a browser.

**Current status:** Implemented; manual browser verification pending.

## Phase 4 — Testing and debugging

- [x] Add tests for game rules, word management, and REST endpoints.
- [x] Cover correct/incorrect guesses, duplicates, invalid input, win/loss, and answer secrecy in test cases.
- [ ] Run the complete test suite, including Flask API tests.
- [ ] Resolve all failures and record the final test result.
- [ ] Perform an end-to-end browser game: create, win, lose, and restart.
- [ ] Confirm API responses never expose the answer during active play.

**Current status:** Test coverage exists. In this environment, the initial full test run stopped at collection because Flask is not installed; engine and word-manager tests have passed before the latest validation changes. Re-run after installing `requirements.txt`.

## Phase 5 — Cloud deployment

- [x] Add `requirements.txt` with Flask and Gunicorn.
- [x] Add `render.yaml` with a Gunicorn web-service start command.
- [x] Document local setup, API usage, and deployment in `README.md`.
- [ ] Install dependencies and verify the production Gunicorn command locally.
- [ ] Push the project to a GitHub repository.
- [ ] Deploy the service to Render or an equivalent cloud host.
- [ ] Verify the public HTTPS URL serves the browser client.
- [ ] Verify a complete game works through the deployed browser and API.

**Current status:** Deployment configuration and documentation exist; no live deployment or public URL has been verified.

---

## Recommended workflow

For each phase: inspect the existing implementation, make only the changes needed for that phase, run its tests, fix failures, update this checklist based on actual verification, and commit the verified changes to GitHub. Do not mark a task complete merely because code has been written.
