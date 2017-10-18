# WireMock Robot Framework Library

This project implements the Robot Framework keywords to interact with [WireMock](http://wiremock.org/) through HTTP.

## Installation

```sh
$ pip install robotframework-wiremock
```

## Usage

Add library to settings section:

```
*** Settings ***
Library  WireMockLibrary
```

[Keyword documentation for the latest release](https://tyrjola.github.io/docs/robotframework-wiremock.html)

See tests/robot/tests/integration_tests.robot for detailed usage examples.

## Development

Prerequisites:

* docker-compose (to run integration tests)
* flake8 (for static code analysis)
* twine (release)
* robot-framework (for doc generation)

Install prerequisites:

```sh
$ make setup
```

Print help:

```sh
$ make help
```

Start wiremock and run tests:

```sh
$ make tester/test
```

Run lint:

```sh
$ make lint
```
