#!/bin/sh -e
python -m robot --outputdir ./logs/ \
                --variable WIREMOCK_URL:${WIREMOCK_URL} \
                ${ROBOT_ARGS} \
                --loglevel DEBUG \
                ./tests
