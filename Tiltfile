load("ext://dotenv", "dotenv")
# -*- mode: Python -*-



# The helm() call above is functionally equivalent to the following:
#
# k8s_yaml(local('helm template -f ./values-dev.yaml ./busybox'))
# watch_file('./busybox')
# watch_file('./values-dev.yaml')


docker_build('ghcr.io/melvinkl/chat_assistant/rag:latest',
             '.',
             dockerfile='components/rag/Dockerfile',
             build_args={'DEV': '1'})

docker_build('ghcr.io/melvinkl/chat_assistant/assistant:latest',
             '.',
             dockerfile='assistant/Dockerfile',
             build_args={'DEV': '1'})



values = [
    "components.rag[0].ingress.enabled=false",
    "components.rag[0].debug=true",
    "assistant.ingress.enabled=false",
    "assistant.debug=true",
    "open-webui.ollama.runtimeClassName=",
]


k8s_yaml(helm('infrastructure/helm', name='assistant', values='infrastructure/helm/values.yaml',set=values))
# 'busybox-deployment' is the name of the Kubernetes resource we're deploying.
k8s_resource('warhammer', port_forwards=['8080:8080','5678:5678'])
k8s_resource('assistant', port_forwards=['8081:8080','5679:5679'])

k8s_resource('assistant-qdrant', port_forwards=['6333:6333'])

k8s_resource('unstructured', port_forwards=['8000:8000'])

