# Pyronaut VADER

A small Pyronaut service that analyzes product reviews with VADER. A browser page lets you choose a review file and see the sentiment result.

The app runs locally. The browser reads the selected file and sends its text to the Pyronaut API as JSON. The Python service calls VADER and returns the scores. No hosted AI service is involved.

## Requirements

- Python 3.10 or later for the Pyronaut CLI
- Pyronaut CLI 0.1.1
- A compatible GraalVM JDK and GraalPy, provisioned by `pyronaut setup`

The demo was prepared with GraalPy 25.4.4.1.1 and `vaderSentiment` 3.3.2. Check the [Pyronaut documentation](https://pyronaut.io/docs/) for current installation requirements.

## Install the CLI

Use a separate virtual environment for the CLI:

```bash
python3 -m venv ~/.venvs/pyronaut-cli
source ~/.venvs/pyronaut-cli/bin/activate
python -m pip install --upgrade pip
python -m pip install "pyronaut==0.1.1"
pyronaut setup
```

## Run the demo

From the project directory:

```bash
pyronaut install
pyronaut test
pyronaut dev
```

Open [http://localhost:8080](http://localhost:8080). Choose one of the review files in `samples/` and select **Run VADER in Pyronaut**.

Press `Ctrl+C` in the terminal to stop the server.

## How it works

```text
browser → POST /api/reviews/analyze → Python controller → VADER service → JSON result
```

The browser reads the selected file and sends its text in a JSON request. Pyronaut binds the request to a dataclass, injects the sentiment service, and returns the analysis as JSON.

## API example

```bash
curl -X POST http://localhost:8080/api/reviews/analyze \
  -H 'Content-Type: application/json' \
  -d '{"text":"I love this coffee grinder. It works perfectly!"}'
```

Example response:

```json
{"label":"positive","compound":0.8655,"positive":0.592,"neutral":0.408,"negative":0.0}
```

Blank review text returns `400 Bad Request`.

## Tests

The tests cover the home page, positive and negative analysis, and rejection of blank review text. Run them with:

```bash
pyronaut test
```
