load("ext://dotenv", "dotenv")
dotenv(fn=".env")

config.define_bool("debug")
cfg = config.parse()
backend_debug = cfg.get("debug", False)

docker_build('ghcr.io/melvinkl/chat_assistant/assistant:latest',
             '.',
             dockerfile='assistant/Dockerfile',
             build_args={'DEV': '1' if backend_debug else '0'},
             live_update=[
                 sync("assistant", "/app/assistant"),
             ],
             )

docker_build('ghcr.io/melvinkl/chat_assistant/home-assistant-component:latest',
             '.',
             dockerfile='components/home-assistant/Dockerfile',
             build_args={'DEV': '1'})


values = [    
    "assistant.ingress.enabled=false",
    "assistant.debug=true",
    "ghcrIo.username=%s" % os.environ.get("GH_USERNAME", ""),
    "ghcrIo.pat=%s" % os.environ.get("GH_PAT", ""),
    "ghcrIo.email=%s" % os.environ.get("GH_MAIL", ""),    
    "open-webui.ollama.runtimeClassName=",
    "components.homeAssistantComponent.ingress.enabled=false",
    "components.homeAssistantComponent.debug=true",
    "components.homeAssistantComponent.secrets.homeassistant.SETTINGS_HOMEASSISTANT_APIKEY=%s" % os.environ.get("SETTINGS_HOMEASSISTANT_APIKEY", ""),
]

if os.environ.get("SETTINGS_OPENAI_API_KEY", None):
    values.append("assistant.settings.openai.SETTINGS_OPENAI_API_KEY=%s" % os.environ.get("SETTINGS_OPENAI_API_KEY", None))
if os.environ.get("SETTINGS_OPENAI_BASE_URL", None):
    values.append("assistant.settings.openai.SETTINGS_OPENAI_BASE_URL=%s" % os.environ.get("SETTINGS_OPENAI_BASE_URL", None))
    values.append("ollama.enabled=false") # There is no need for ollama if a different llm is used.
if os.environ.get("SETTINGS_OPENAI_MODEL", None):
    values.append("assistant.settings.openai.SETTINGS_OPENAI_MODEL=%s" % os.environ.get("SETTINGS_OPENAI_MODEL", None))    

k8s_yaml(helm('infrastructure/helm', name='assistant', values='infrastructure/helm/values.yaml',set=values))

k8s_resource('assistant', port_forwards=[port_forward(8080,8080, link_path="/docs"),'5679:5679'])
k8s_resource('home-assistant-component', port_forwards=['8082:8080','5680:5680'])
k8s_resource('assistant-qdrant', port_forwards=[ port_forward( 6333, container_port=6333, name="Dashboard", link_path="/dashboard", ), ])
