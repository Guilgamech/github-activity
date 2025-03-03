#!/usr/bin/env python3

import sys
import json
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError

def main():
    # Verificar argumentos
    if len(sys.argv) != 2:
        print("Error: Por favor proporciona un nombre de usuario de GitHub")
        print("Uso: github-activity <username>")
        sys.exit(1)
    
    username = sys.argv[1]
    api_url = f"https://api.github.com/users/{username}/events"
    
    try:
        # Configurar la solicitud con User-Agent requerido
        req = Request(api_url)
        req.add_header('User-Agent', 'GitHub-Activity-CLI/1.0')
        
        # Realizar la solicitud
        with urlopen(req) as response:
            if response.status != 200:
                raise HTTPError(api_url, response.status, "Error en la respuesta", response.headers, None)
            
            data = response.read().decode('utf-8')
            events = json.loads(data)
            
            if not events:
                print(f"No se encontró actividad reciente para {username}")
                return
            
            print(f"Actividad reciente de {username}:\n")
            for event in events[:10]:  # Mostrar primeros 10 eventos
                print(format_event(event))
    
    except HTTPError as e:
        if e.code == 404:
            print(f"Error: Usuario '{username}' no encontrado")
        else:
            print(f"Error de API: {e.code} - {e.reason}")
        sys.exit(1)
    except URLError as e:
        print(f"Error de conexión: {e.reason}")
        sys.exit(1)
    except json.JSONDecodeError:
        print("Error: Respuesta inválida de la API")
        sys.exit(1)

def format_event(event):
    event_type = event['type']
    repo = event['repo']['name']
    payload = event['payload']
    
    if event_type == 'PushEvent':
        return f"- Pushed {len(payload['commits'])} commits to {repo}"
    
    if event_type == 'IssuesEvent':
        action = payload['action']
        return f"- {action.capitalize()} an issue in {repo}"
    
    if event_type == 'PullRequestEvent':
        action = payload['action']
        return f"- {action.capitalize()} a pull request in {repo}"
    
    if event_type == 'WatchEvent':
        return f"- Starred {repo}"
    
    if event_type == 'ForkEvent':
        return f"- Forked {repo} to {payload['forkee']['full_name']}"
    
    if event_type == 'CreateEvent':
        ref_type = payload['ref_type']
        return f"- Created a {ref_type} in {repo}"
    
    return f"- Performed {event_type} on {repo}"

if __name__ == "__main__":
    main()