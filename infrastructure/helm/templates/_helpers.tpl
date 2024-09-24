{{- define "ghcr.dockerconfigjson" -}}
{{- $username := .Values.ghcrIo.username -}}
{{- $password := .Values.ghcrIo.pat -}}
{{- $auth := printf "%s:%s" $username $password | b64enc -}}
{{- $dockerconfigjson := dict "auths" (dict "ghcr.io" (dict "username" $username "password" $password "email" .Values.ghcrIo.email "auth" $auth)) | toJson -}}
{{- print $dockerconfigjson | b64enc -}}
{{- end -}}