# -*- mode: Python -*-

k8s_yaml(helm('infrastructure/helm', name='assistant', values='infrastructure/helm/values.yaml',set=[
    ""
]))

# The helm() call above is functionally equivalent to the following:
#
# k8s_yaml(local('helm template -f ./values-dev.yaml ./busybox'))
# watch_file('./busybox')
# watch_file('./values-dev.yaml')


docker_build('warhammer',
             '.',
             dockerfile='components/warhammer/Dockerfile',
             build_args={'DEV': '1'})

# 'busybox-deployment' is the name of the Kubernetes resource we're deploying.
k8s_resource('warhammer', port_forwards=['8080:8080','5678:5678'])

k8s_resource('assistant-qdrant', port_forwards=['6333:6333'])