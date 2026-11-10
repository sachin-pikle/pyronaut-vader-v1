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

From the project directory, install dependencies, run the tests, and start the development server:

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

Blank review text returns `400 Bad Request`.

## Package

### `fat-jar`

Build and run an executable JAR with a compatible GraalVM JDK:

```bash
pyronaut build --jar
java -jar dist/pyronaut-vader-1.0.0.jar
```

### `wheel-native`

Build and run a native executable:

```bash
pyronaut build --native
./pyronaut/native/application
```

### `wheel-jvm`

Build the wheel. Pyronaut prints the commands to install and run it:

```bash
pyronaut build --jvm
```

Use the printed `Install with:` and `Run it with:` commands in the GraalPy deployment environment. A compatible GraalVM JDK is required.

### `docker-jvm`

Set the image name in `pyproject.toml`, then build and run the image:

```toml
[tool.pyronaut.build.docker]
image-name = "pyronaut-vader"
```

```bash
pyronaut build --jvm --docker
docker run --rm -p 8080:8080 pyronaut-vader:1.0.0
```

### `docker-native`

Build and run the native image:

```bash
pyronaut build --native --docker
docker run --rm -p 8080:8080 pyronaut-vader:1.0.0-native
```

### `wheel-crema`

Build the wheel. Pyronaut prints the commands to install and run it:

```bash
pyronaut build --native-base
```

Use the printed `Install with:` and `Run it with:` commands in the deployment environment.

### `docker-crema`

Build and run the Crema image:

```bash
pyronaut build --native-base --docker
docker run --rm -p 8080:8080 pyronaut-vader:1.0.0-native
```

Wheel builds create a distributable Python wheel in `dist/`. Container builds require Docker. Native and Crema builds take longer than JVM builds; native builds also require application dependencies to support GraalVM Native Image. See the [Pyronaut packaging documentation](https://pyronaut.io/docs/) for deployment details.
