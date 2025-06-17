load("ext://dotenv", "dotenv")
# -*- mode: Python -*-



# The helm() call above is functionally equivalent to the following:
#
# k8s_yaml(local('helm template -f ./values-dev.yaml ./busybox'))
# watch_file('./busybox')
# watch_file('./values-dev.yaml')

docker_build('ghcr.io/melvinkl/chat_assistant/assistant:latest',
             '.',
             dockerfile='assistant/Dockerfile',
             build_args={'DEV': '1'},
             live_update=[
                 sync("assistant", "/app/assistant"),
                 sync("components/base-library",
                      "/app/components/base-library"),                 
             ],
             )



values = [    
    "assistant.ingress.enabled=false",
    "assistant.debug=true",
    "ollama.runtimeClassName=",
]


k8s_yaml(helm('infrastructure/helm', name='assistant', values='infrastructure/helm/values.yaml',set=values))
# 'busybox-deployment' is the name of the Kubernetes resource we're deploying.

k8s_resource('assistant', port_forwards=[port_forward(8080,8080, link_path="/docs"),'5679:5679'])

