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

Keyword documentation: WIP --> link will be added here

See tests/robot/tests/integration_tests.robot for detailed examples.

## Development

Prerequisites:

* docker-compose (to run integration tests)
* flake8 (for static code analysis)
* twine (release)

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
