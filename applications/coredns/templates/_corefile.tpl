{{/* Generate basic labels */}}
{{- define "corefile" }}
Corefile: |
{{- if .Values.publicDnsServers }}
  .:30053 {
    forward . {{ join " " .Values.publicDnsServers }}
    log
    errors
{{- if .Values.acls }}
    acl {
{{ .Values.acls | indent 6 -}}
    }
{{- end }}
  }
{{- end }}

  {{ .Values.domain }}:30053 {
    log
    k8s_gateway {{ .Values.domain }} {
      resources Ingress Service
      ttl 10
    }
  }

{{ if .Values.additionalZones -}}
{{ .Values.additionalZones | indent 2}}
{{- end }}

{{ if .Values.additionalConfigs -}}
{{ toYaml .Values.additionalConfigs }}
{{- end }}
{{- end }}
