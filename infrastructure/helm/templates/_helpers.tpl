{{- define "ghcr.dockerconfigjson" -}}
{{- $username := .Values.ghcrIo.username -}}
{{- $password := .Values.ghcrIo.pat -}}
{{- $auth := printf "%s:%s" $username $password | b64enc -}}
{{- $dockerconfigjson := dict "auths" (dict "ghcr.io" (dict "username" $username "password" $password "email" .Values.ghcrIo.email "auth" $auth)) | toJson -}}
{{- print $dockerconfigjson | b64enc -}}
{{- end -}}

{{- define "egressNetworkPolicy" -}}
{{- if .enabled -}}
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: {{ include "{{ .chartName }}-fullname" . }}-egress
  labels:
    {{- include "{{ .chartName }}.labels" . | nindent 4 }}
spec:
  podSelector:
    matchLabels:
      {{- include "{{ .chartName }}.selectors" . | nindent 6 }}
  policyTypes:
  - Egress
  egress:
  {{- if .allowedHosts }}
  {{- range $host := .allowedHosts }}
  - to:
    - ipBlock:
        cidr: {{ $host }}
  {{- end }}
  {{- else }}
  - {}  # Allow all egress if no specific hosts defined
  {{- end }}
{{- else -}}
# Deny all egress when disabled
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: {{ include "{{ .chartName }}-fullname" . }}-egress-deny
  labels:
    {{- include "{{ .chartName }}.labels" . | nindent 4 }}
spec:
  podSelector:
    matchLabels:
      {{- include "{{ .chartName }}.selectors" . | nindent 6 }}
  policyTypes:
  - Egress
  egress: []  # Empty egress rules means deny all
{{- end }}
{{- end -}}