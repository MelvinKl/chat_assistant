# Chat Assistant
================

## Overview

This repository contains the source code for a chat assistant application, including a Kubernetes Helm chart and a setup script for developing locally using k3d.
The chat assistant API is located in the `assistant` directory and provides endpoints for user interaction.


## Directory Structure

The repository is organized as follows:

### `infrastructure/helm`

* Contains the Helm chart for deploying the chat assistant to a Kubernetes cluster.

### `infrastructure/local/create_local_env.sh`

* Setup script for creating a local k3d cluster for development purposes.

### `.vscode` and `.devcontainer`

* Contain configuration files for debugging with Visual Studio Code and developing in a devcontainer, respectively.

## Getting Started

To get started with the chat assistant, follow these steps:

1. Create a new Kubernetes cluster using `infrastructure/local/create_local_env.sh`.
2. Use Tiltfile to start the chat assistant application.
3. When using Tiltfile, the APIs will wait for the debugger to connect.

## Components

### Home Assistant Component

### Rag Component

The rag component implements a simple rag solution. You can have as many of them as you like, the definition in the helm-chart is an array.
You can have a separate instance for every topic you want to cover.

## Development

This repository provides a `Tiltfile` for local development.
It is required to have a `.env` file in the root of the repositrory with the following values:
- `SETTINGS_HOMEASSISTANT_APIKEY`: The apikey for your homeassistant installation.


### Extending the Chat Assistant

To add new features or components to the chat assistant, refer to the blueprint in `components/base-component-api`. One example component is `rag-component` in `components/rag`.

## Files

* `.vscode`: Configuration files for debugging with Visual Studio Code.
* `.devcontainer`: Configuration files for developing in a devcontainer.
* `assistant`: The chat assistant API and its endpoints.
* `components`: Directory containing the blueprint for extending the chat assistant, including example components like `rag-component`.
* `infrastructure/helm`: Helm chart for deploying the chat assistant to a Kubernetes cluster.
* `infrastructure/local/create_local_env.sh`: Setup script for creating a local k3d cluster.