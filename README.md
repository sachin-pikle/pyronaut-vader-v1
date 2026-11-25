# Pyronaut VADER v1

A small Pyronaut application that analyzes product reviews with VADER and stores the results in Oracle Database Free. The browser page lets you select a review file and see the result.

> **Note:** This demo was used in the Practical Python AI on the JVM with GraalPy and Pyronaut session at WeAreDevelopers Conference India. See the [conference talk entry](https://github.com/sachin-pikle/conference-talks/tree/main#2026-wearedevelopers-conference-india) for the presentation and video details.

## Versions

- Pyronaut CLI: 0.1.2
- Micronaut Core: 5.2.22
- Micronaut Platform: 5.2.5
- GraalVM: 25.4.4.1.1 (JDK 25.0.4.1)
- GraalPy: 25.4.4.1.1
- GraalPy interpreter: `graalpy3.13-25.4.4`
- Native Image JDK: 25
- `vaderSentiment`: 3.3.2

The GraalVM JDK was selected with SDKMAN identifier `25.4.4+1-graal`. The project does not pin a JDK version; `pyronaut setup` locates or provisions a compatible one.

## Flow

```text
Browser reads review file
  → sends review text as JSON
  → Micronaut HTTP server running on Netty
  → Python controller
  → Python sentiment service
  → VADER
  → Micronaut Data repository
  → Oracle Database Free
  → JSON result shown in browser
```

The analysis runs locally. The demo does not send review text to a hosted AI service.

This project declares Micronaut's Netty server module. Netty handles the HTTP connections; Micronaut provides routing and dispatches the request to the Python controller.

Micronaut Data implements the repository during Pyronaut processing. During development and testing, Micronaut Test Resources starts Oracle Database Free in a container and supplies the datasource configuration. The `dev` and `test` environments recreate the demo table, so this history is temporary.

## Run

The Pyronaut CLI requires Python 3.10 or later. A Docker-compatible engine, such as Docker Desktop or Rancher Desktop, must also be installed and running so Test Resources can start Oracle Database Free. Podman requires Docker compatibility to be configured.

Install the CLI in a separate virtual environment and provision its SDK:

```bash
sdk use java 25.4.4+1-graal
python3 -m venv ~/.venvs/pyronaut-cli
source ~/.venvs/pyronaut-cli/bin/activate
python3 -m pip install --upgrade pip
python3 -m pip install --upgrade 'pyronaut==0.1.2'
```

```bash
sdk use java 25.4.4+1-graal
pyronaut setup --refresh
```

`pyronaut setup` prepares the shared GraalVM/GraalPy SDKs and CLI build tools.

From the project directory, `pyronaut install` creates the project's GraalPy `.venv`, installs Python dependencies, resolves build, runtime, development-runtime, and test dependencies, and generates the application schema and Python editor stubs. `pyronaut run`, `dev`, and `test` use that environment automatically.

Install dependencies, run the tests, and start the development server:

```bash
sdk use java 25.4.4+1-graal
pyronaut install
pyronaut test
pyronaut dev
```

The first `test` or `dev` run may take longer while the Oracle Database Free image is downloaded. If that initial download exceeds the startup timeout, run the command again after the download finishes. Test Resources stops its container when the command ends.

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

Each successful analysis is stored without changing the response from `/api/reviews/analyze`. List the saved analyses with:

```bash
curl http://localhost:8080/api/reviews/history | jq
```

## API documentation

Pyronaut generates the OpenAPI description during processing. `pyronaut dev` runs processing before starting the app. While it is running, open [Swagger UI](http://localhost:8080/swagger-ui/index.html) or [ReDoc](http://localhost:8080/redoc/index.html) to explore and call the endpoint.

This project exposes the generated OpenAPI specification, Swagger UI, and ReDoc through static-resource mappings in `config/application.toml`. Pyronaut configures these mappings automatically for direct single-file applications, but not for projects.

## Package

Database persistence does not change the available packaging formats. During `pyronaut dev` and `pyronaut test`, Micronaut Test Resources starts a temporary Oracle Database Free container and supplies its connection settings. Packaged applications need the URL and credentials of an accessible Oracle database at runtime.

### Summary

The status below records whether the current application has been tested end-to-end with Oracle.

| Format | Build command | Tested with Oracle |
| --- | --- | --- |
| `docker-jvm` | `pyronaut build --jvm --docker` | Yes |
| `fat-jar` | `pyronaut build --jar` | Yes |
| `wheel-crema` | `pyronaut build --native-base` | Yes |
| `wheel-jvm` | `pyronaut build --jvm` | No |
| `wheel-native` | `pyronaut build --native` | No |
| `docker-native` | `pyronaut build --native --docker` | No |
| `docker-crema` | `pyronaut build --native-base --docker` | No |

### `docker-jvm`

```bash
source ~/.venvs/pyronaut-cli/bin/activate
```

Set `image-name` under `[tool.pyronaut.build.docker]` in `pyproject.toml`:

```toml
[tool.pyronaut.build.docker]
image-name = "pyronaut-vader"
```

A Docker-compatible engine, such as Docker Desktop or Rancher Desktop, must be installed and running. Podman requires Docker compatibility to be configured. Verify that the `docker` CLI can reach the engine:

```bash
docker version
sdk use java 25.4.4+1-graal
```

Build the JVM container image:

```bash
pyronaut build --jvm --docker
```

The generated image includes the declared Python dependencies and does not use the project's host `.venv`.

Confirm that the image was created:

```bash
docker image ls pyronaut-vader
```

The image is tagged `pyronaut-vader:1.0.0`.

Create a network for the application and database:

```bash
docker network create pyronaut-vader-network
```

Start Oracle Database Free on that network:

```bash
docker run -d \
  --name pyronaut-vader-db \
  --network pyronaut-vader-network \
  -e ORACLE_PASSWORD=OracleDemo123 \
  -e APP_USER=vader \
  -e APP_USER_PASSWORD=VaderDemo123 \
  gvenzl/oracle-free:slim-faststart
```

Follow the database log until you see `DATABASE IS READY TO USE!`. Press `Ctrl+C` to stop following the log; the database container will continue running.

```bash
docker logs -f pyronaut-vader-db
```

Run the application in the foreground and pass the datasource configuration:

```bash
docker run --rm \
  --name pyronaut-vader \
  --network pyronaut-vader-network \
  -p 8080:8080 \
  -e DATASOURCES_DEFAULT_URL='jdbc:oracle:thin:@//pyronaut-vader-db:1521/FREEPDB1' \
  -e DATASOURCES_DEFAULT_USERNAME=vader \
  -e DATASOURCES_DEFAULT_PASSWORD=VaderDemo123 \
  -e DATASOURCES_DEFAULT_SCHEMA_GENERATE=CREATE_DROP \
  pyronaut-vader:1.0.0
```

`CREATE_DROP` is used only for this temporary demo. A production deployment should manage the schema with a migration tool such as Flyway or Liquibase.

In another terminal, test the API:

```bash
curl -i -X POST http://localhost:8080/api/reviews/analyze \
  -H 'Content-Type: application/json' \
  -d '{"text":"This coffee grinder is fantastic."}'
```

Analyze a negative review:

```bash
curl -i -X POST http://localhost:8080/api/reviews/analyze \
  -H 'Content-Type: application/json' \
  -d '{"text":"This robot vacuum is terrible and completely useless."}'
```

Show both saved analyses:

```bash
curl -s http://localhost:8080/api/reviews/history | jq
```

Stop the application with `Ctrl+C`, then remove the temporary database and network:

```bash
docker stop pyronaut-vader-db
docker rm pyronaut-vader-db
docker network rm pyronaut-vader-network
```

### Host-run formats

#### Prepare Oracle

The JAR, Crema wheel, and native wheel run on the host rather than inside Docker. Start a separate Oracle container and publish its database port:

```bash
docker run -d \
  --name pyronaut-vader-db-host \
  -p 1521:1521 \
  -e ORACLE_PASSWORD=OracleDemo123 \
  -e APP_USER=vader \
  -e APP_USER_PASSWORD=VaderDemo123 \
  gvenzl/oracle-free:slim-faststart
```

Follow the log until you see `DATABASE IS READY TO USE!`, then press `Ctrl+C`:

```bash
docker logs -f pyronaut-vader-db-host
```

Export the datasource configuration in the terminal that will run the application:

```bash
export DATASOURCES_DEFAULT_URL='jdbc:oracle:thin:@//localhost:1521/FREEPDB1'
export DATASOURCES_DEFAULT_USERNAME=vader
export DATASOURCES_DEFAULT_PASSWORD=VaderDemo123
export DATASOURCES_DEFAULT_SCHEMA_GENERATE=CREATE_DROP
```

Use the same Oracle container and environment variables for each host-run format below. Run only one application at a time and stop it with `Ctrl+C`.

Before starting the next format, remove the table created by the previous application:

```bash
docker exec pyronaut-vader-db-host bash -lc \
  'printf "DROP TABLE sentiment_analysis PURGE;\nDROP SEQUENCE sentiment_analysis_seq;\nEXIT;\n" |
   sqlplus -s "$APP_USER/$APP_USER_PASSWORD@//localhost:1521/FREEPDB1"'
```

Micronaut Data creates both objects for the entity. Removing both prevents `ORA-00955: name is already used by an existing object` when the next application processes `CREATE_DROP`.

#### Path 1: CLI environment

```bash
source ~/.venvs/pyronaut-cli/bin/activate
```

**`fat-jar`**

```bash
pyronaut build --jar
java -jar dist/pyronaut-vader-1.0.0.jar
```

The JAR includes the declared Python dependencies and does not use the project's host `.venv`.

**`wheel-crema`**

Note: In the Pyronaut 0.1.2 artifacts tested here, the Python application code in GraalPy's virtual filesystem is packaged inside the Crema binary. However, the `vaderSentiment` package and other packages are not packaged in the Crema binary; GraalPy loads it from the project's `.venv` on disk. When you launch an artifact, `VIRTUAL_ENV` must point to this project's `.venv`. If it is unset or points elsewhere, the server starts, but the requests to `/api/reviews/analyze` fail with `ModuleNotFoundError: No module named 'vaderSentiment'`.

Track this packaging question in [Pyronaut issue #430](https://github.com/micronaut-projects/pyronaut/issues/430).


Build the wheel, then run the staged binary:

The build stages the binary at `__pyronaut__/native/pyronaut-vader`.

```bash
pyronaut build --native-base
VIRTUAL_ENV="$PWD/.venv" ./__pyronaut__/native/pyronaut-vader
```

The wheel is written to `dist/`. To test the installed wheel instead, use the optional commands below; you can keep the wheel installed afterwards.

```bash
python -m pip install dist/*.whl
VIRTUAL_ENV="$PWD/.venv" pyronaut-vader
```

#### Path 2: Project environment

Start Oracle and export the datasource configuration as described under **Prepare Oracle** above.

```bash
deactivate
source .venv/bin/activate
```

**`fat-jar`**

```bash
~/.venvs/pyronaut-cli/bin/pyronaut build --jar
java -jar dist/pyronaut-vader-1.0.0.jar
```

**`wheel-crema`**

Build the wheel, then run the staged binary:

The build stages the binary at `__pyronaut__/native/pyronaut-vader`.

```bash
~/.venvs/pyronaut-cli/bin/pyronaut build --native-base
./__pyronaut__/native/pyronaut-vader
```

The wheel is written to `dist/`. To test the installed wheel instead, install and run its command:

```bash
python -m pip install dist/*.whl
pyronaut-vader
```

For each format, analyze a review and read the saved row:

```bash
curl -X POST http://localhost:8080/api/reviews/analyze \
  -H 'Content-Type: application/json' \
  -d '{"text":"This coffee grinder is fantastic."}'

curl -s http://localhost:8080/api/reviews/history | jq
```

#### Clean up host-run tests

After testing one or more host-run formats, clear the datasource variables and remove the temporary database:

```bash
unset DATASOURCES_DEFAULT_URL
unset DATASOURCES_DEFAULT_USERNAME
unset DATASOURCES_DEFAULT_PASSWORD
unset DATASOURCES_DEFAULT_SCHEMA_GENERATE

docker stop pyronaut-vader-db-host
docker rm pyronaut-vader-db-host
```

## Clean start

This resets the project's generated Pyronaut state. Clean up any package-test database containers using the commands in the Package section first.

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
sdk use java 25.4.4+1-graal
pyronaut install
```
