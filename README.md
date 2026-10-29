# Hangman

A web Hangman game: a Flask server owns the game logic, and the browser talks to it over a JSON REST API. The hidden word stays on the server until the game is won or lost.

This is the **assignment-scoped** version of the original Hangman client/server project: server + browser client only. There is no terminal client, bot platform, evaluation mode, or leaderboard.

## Requirements

- Python 3.10+
- `pip install -r requirements.txt`

## Run locally

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python3 server.py
```

Open [http://127.0.0.1:5000](http://127.0.0.1:5000).

Production-style (one worker, because games are stored in memory):

```bash
gunicorn --bind 127.0.0.1:5000 --workers 1 server:app
```

## Play

1. Choose Easy, Medium, or Hard.
2. Click **New Game**.
3. Guess letters with the on-screen keyboard or your physical keyboard.
4. You have six incorrect guesses. The drawing fills in as you miss.
5. Start another game without reloading the page.

## REST API

All endpoints accept/return JSON. While `status` is `playing`, responses never include `word`.

### Create a game

`POST /api/games`

```json
{ "difficulty": "medium" }
```

`201` response:

```json
{
  "game_id": "abc123",
  "pattern": "_ _ _ _ _",
  "guessed_letters": [],
  "incorrect_letters": [],
  "remaining_guesses": 6,
  "status": "playing"
}
```

Difficulty must be `easy`, `medium`, or `hard`.

### Get game state

`GET /api/games/{game_id}`

`200` on success, `404` if the id is unknown.

### Submit a guess

`POST /api/games/{game_id}/guess`

```json
{ "letter": "e" }
```

`200` on a valid new letter. `400` for duplicates, non-letters, multi-character input, or guesses after the game has ended. After a win or loss, the JSON includes `"word"`.

Example with curl:

```bash
curl -s -X POST http://127.0.0.1:5000/api/games \
  -H 'Content-Type: application/json' \
  -d '{"difficulty":"easy"}'

curl -s -X POST http://127.0.0.1:5000/api/games/GAME_ID/guess \
  -H 'Content-Type: application/json' \
  -d '{"letter":"a"}'
```

## Tests

```bash
python3 -m unittest discover -s tests -t . -v
```

## Project layout

```
hangman/
├── game.py              # engine (no Flask)
├── word_manager.py
├── server.py            # Flask REST API + static files
├── static/
│   ├── index.html
│   ├── style.css
│   └── app.js
├── words/
│   ├── easy.txt
│   ├── medium.txt
│   └── hard.txt
├── tests/
├── requirements.txt
└── render.yaml
```

## Deploy on Render

1. Push this repo to GitHub.
2. In [Render](https://render.com), create a **Web Service** from the repo (or apply the Blueprint in `render.yaml`).
3. Build command: `pip install -r requirements.txt`
4. Start command: `gunicorn --bind 0.0.0.0:$PORT --workers 1 server:app`
5. Use the **free** instance type if you want a class demo. The service may sleep when idle; the first request can take a minute.

Games are stored in memory. A restart (or sleep on the free tier) clears active games.

## Rules

- One letter per guess
- Six incorrect guesses
- Duplicate / invalid guesses are rejected and do not change the board
- Server is authoritative; the browser never receives the answer until `won` or `lost`
