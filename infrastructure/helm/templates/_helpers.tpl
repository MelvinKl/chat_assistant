{{- define "ghcr.dockerconfigjson" -}}
{{- $username := .Values.ghcrIo.username -}}
{{- $password := .Values.ghcrIo.pat -}}
{{- $auth := printf "%s:%s" $username $password | b64enc -}}
{{- $dockerconfigjson := dict "auths" (dict "ghcr.io" (dict "username" $username "password" $password "email" .Values.ghcrIo.email "auth" $auth)) | toJson -}}
{{- print $dockerconfigjson | b64enc -}}
{{- end -}}

{{- define "assistant.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{- define "assistant.labels" -}}
helm.sh/chart: {{ .Chart.Name }}-{{ .Chart.Version | replace "+" "_" }}
app.kubernetes.io/name: {{ include "assistant.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
app.kubernetes.io/version: {{ .Chart.Version }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{- define "assistant.selectorLabels" -}}
app.kubernetes.io/name: {{ include "assistant.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}