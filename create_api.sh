#! /bin/sh

# Base Component API
docker  run --user $(id -u):$(id -g) --rm \
    -v $PWD/components:/local openapitools/openapi-generator-cli generate \
    -i /local/openapi.yaml \
    -g python-fastapi \
    -o /local/base-component-api/

# Component client
docker  run --user $(id -u):$(id -g) --rm \
    -v $PWD:/local openapitools/openapi-generator-cli generate \
    -i /local/components/openapi.yaml \
    -g python \
    -o /local/assistant
