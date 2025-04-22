#! /bin/sh

# Base Component API
docker  run --user $(id -u):$(id -g) --rm \
    -v $PWD/components:/local openapitools/openapi-generator-cli:latest generate \
    -i /local/base-component-api/openapi.yaml \
    -g python-fastapi \
    -o /local/base-component-api \
    --additional-properties=packageName="base_component_api"    

# Component client
docker  run --user $(id -u):$(id -g) --rm \
    -v $PWD:/local openapitools/openapi-generator-cli:latest generate \
    -i /local/components/base-component-api/openapi.yaml \
    -g python \
    -o /local/assistant/src \
    --additional-properties=generateSourceCodeOnly="true",packageName="assistant.component_api"


# Assistant API
docker  run --user $(id -u):$(id -g) --rm \
    -v $PWD:/local openapitools/openapi-generator-cli:latest generate \
    -i /local/openapi-spec.yaml \
    -g python-fastapi \
    -o /local/assistant \
    --skip-validate-spec \
    --additional-properties=generateSourceCodeOnly="true",packageName="assistant"
