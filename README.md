# Pyronaut VADER v1

A small Pyronaut application that analyzes product reviews with VADER. The browser page lets you select a review file and see the result.

Uses Pyronaut CLI 0.1.1, GraalVM 25.4.4.1.1 (based on JDK 25.0.4.1), GraalPy 25.4.4.1.1, and `vaderSentiment` 3.3.2. The GraalVM JDK was selected with SDKMAN identifier `25.4.4+1-graal`. The project does not pin a JDK version; `pyronaut setup` locates or provisions a compatible one.

## Flow

```text
Browser reads review file
  → sends review text as JSON
  → Micronaut HTTP server running on Netty
  → Python controller
  → Python sentiment service
  → VADER
  → JSON result shown in browser
```

The analysis runs locally. The demo does not send review text to a hosted AI service.

This project declares Micronaut's Netty server module. Netty handles the HTTP connections; Micronaut provides routing and dispatches the request to the Python controller.

## Run

The Pyronaut CLI requires Python 3.10 or later. Install it in a separate virtual environment and provision its SDK:

```bash
python3 -m venv ~/.venvs/pyronaut-cli
source ~/.venvs/pyronaut-cli/bin/activate
python -m pip install --upgrade pip
python -m pip install "pyronaut==0.1.1"
pyronaut setup
```

The activated `pyronaut-cli` environment is for the CLI. From the project directory, run `pyronaut install`; it creates the project's `.venv` with GraalPy and installs `vaderSentiment`. You don't need to activate the project environment for `pyronaut run`, `dev`, or `test`; they use it automatically.

Install dependencies, run the tests, and start the development server:

```bash
pyronaut install
pyronaut test
pyronaut dev
```

Open [http://localhost:8080](http://localhost:8080), choose a file under `samples/`, and select **Run VADER in Pyronaut**. Press `Ctrl+C` in the terminal to stop the server.

## API

The browser reads the selected file and posts its text to `/api/reviews/analyze` as JSON.

```bash
curl -X POST http://localhost:8080/api/reviews/analyze \
  -H 'Content-Type: application/json' \
  -d '{"text":"I love this coffee grinder. It works perfectly!"}'
```

Example response:

```json
{"label":"positive","compound":0.8655,"positive":0.592,"neutral":0.408,"negative":0.0}
```

Blank review text returns `400 Bad Request`:

```bash
curl -i -X POST http://localhost:8080/api/reviews/analyze \
  -H 'Content-Type: application/json' \
  -d '{"text":""}'
```

## Package

In the Pyronaut 0.1.1 artifacts tested here, the Python application code is packaged inside the JAR, native executable, and Crema wheel in GraalPy's virtual filesystem. However, the `vaderSentiment` library is not packaged in those artifacts; GraalPy loads it from the project's `.venv` on disk. When you launch an artifact, `VIRTUAL_ENV` must point to this project's `.venv`. If it is unset or points elsewhere, the server starts, but the requests to `/api/reviews/analyze` fail with `ModuleNotFoundError: No module named 'vaderSentiment'`.

### Tested formats

#### Path 1: Keep the CLI environment active

```bash
source ~/.venvs/pyronaut-cli/bin/activate
```

##### `fat-jar`

```bash
pyronaut build --jar
VIRTUAL_ENV="$PWD/.venv" java -jar dist/pyronaut-vader-1.0.0.jar
```

##### `wheel-crema`

Build the wheel, then use the install and run commands printed by Pyronaut. Prefix its printed run command with `VIRTUAL_ENV="$PWD/.venv"`.

```bash
pyronaut build --native-base
```

##### `wheel-native`

```bash
pyronaut build --native
VIRTUAL_ENV="$PWD/.venv" ./__pyronaut__/native/pyronaut-vader
```

#### Path 2: Switch to the project environment

```bash
deactivate
source .venv/bin/activate
```

##### `fat-jar`

```bash
~/.venvs/pyronaut-cli/bin/pyronaut build --jar
java -jar dist/pyronaut-vader-1.0.0.jar
```

##### `wheel-crema`

Build the wheel with the CLI, then use Pyronaut's printed install and run commands. The project `.venv` is active for the run command.

```bash
~/.venvs/pyronaut-cli/bin/pyronaut build --native-base
```

##### `wheel-native`

```bash
~/.venvs/pyronaut-cli/bin/pyronaut build --native
./__pyronaut__/native/pyronaut-vader
```

The native build took 13 minutes and 13 seconds on this machine. Pyronaut staged the executable at `__pyronaut__/native/pyronaut-vader` and created the wheel `dist/pyronaut_vader-1.0.0-graalpy313-graalpy253_313_native-macosx_26_0_arm64.whl`.

### Not tested

| Format | Build command |
| --- | --- |
| `wheel-jvm` | `~/.venvs/pyronaut-cli/bin/pyronaut build --jvm` |
| `docker-jvm` | `~/.venvs/pyronaut-cli/bin/pyronaut build --jvm --docker` |
| `docker-native` | `~/.venvs/pyronaut-cli/bin/pyronaut build --native --docker` |
| `docker-crema` | `~/.venvs/pyronaut-cli/bin/pyronaut build --native-base --docker` |

For `docker-jvm`, set `image-name` under `[tool.pyronaut.build.docker]` in `pyproject.toml`. Docker formats require Docker.

## Clean start

Stop the running application with `Ctrl+C`. If the project's `.venv` is active, run `deactivate` first. From the project directory, activate the CLI environment:

```bash
source ~/.venvs/pyronaut-cli/bin/activate
```

Then remove Pyronaut's generated state and the project environment:

```bash
pyronaut clean --full
```

`clean --full` removes `__pyronaut__/` and `.venv/`. It leaves built packages in `dist/`; remove that directory too if you want to clear old JARs and wheels:

```bash
rm -r dist
```

Recreate the project environment and resolve dependencies:

```bash
pyronaut install
```
