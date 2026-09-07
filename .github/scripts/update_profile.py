#!/usr/bin/env python3
"""
GitHub Profile README Dynamic Updater
Author: Anthony Pilatasig / Automation System
"""

import os
import re
import json
import urllib.request
import urllib.error
from datetime import datetime, timezone

USERNAME = "AnthonyPilatasig"
README_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "README.md"))

# Language badge mappings
LANG_BADGES = {
    "C#": "https://img.shields.io/badge/C%23-239120?style=flat-square&logo=csharp&logoColor=white",
    ".NET": "https://img.shields.io/badge/.NET-512BD4?style=flat-square&logo=dotnet&logoColor=white",
    "TypeScript": "https://img.shields.io/badge/TypeScript-3178C6?style=flat-square&logo=typescript&logoColor=white",
    "JavaScript": "https://img.shields.io/badge/JavaScript-F7DF1E?style=flat-square&logo=javascript&logoColor=black",
    "Java": "https://img.shields.io/badge/Java-ED8B00?style=flat-square&logo=openjdk&logoColor=white",
    "Python": "https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white",
    "HTML": "https://img.shields.io/badge/HTML5-E34F26?style=flat-square&logo=html5&logoColor=white",
    "CSS": "https://img.shields.io/badge/CSS3-1572B6?style=flat-square&logo=css3&logoColor=white",
    "Dart": "https://img.shields.io/badge/Dart-0175C2?style=flat-square&logo=dart&logoColor=white",
    "Go": "https://img.shields.io/badge/Go-00ADD8?style=flat-square&logo=go&logoColor=white",
    "Rust": "https://img.shields.io/badge/Rust-000000?style=flat-square&logo=rust&logoColor=white",
    "Vue": "https://img.shields.io/badge/Vue.js-4FC08D?style=flat-square&logo=vuedotjs&logoColor=white",
    "React": "https://img.shields.io/badge/React-20232A?style=flat-square&logo=react&logoColor=61DAFB",
}

# Curated metadata for key projects
PROJECT_METADATA = {
    "net8-education-microservices": {
        "title": "Educational Microservices Platform",
        "description": "Ecosistema distribuido de microservicios en <b>.NET 8</b> (Analytics, Adaptive Engine, Assessment, Competency y Content) con <b>Clean Architecture, CQRS, Event Sourcing y DDD</b>.",
        "tags": [".NET 8", "C#", "Microservices", "CQRS", "Docker", "Kubernetes"],
    },
    "DebtManager": {
        "title": "Debt Manager & Financial Advisor",
        "description": "Asesor financiero personal multiplataforma desarrollado con <b>.NET 9 + Avalonia UI + PostgreSQL</b> para análisis de flujo de caja y factibilidad financiera.",
        "tags": [".NET 9", "C#", "Avalonia UI", "PostgreSQL", "Clean Arch"],
    },
    "anthony-portfolio": {
        "title": "Interactive Senior Portfolio & WASM Engine",
        "description": "Portafolio interactivo moderno con <b>React 19, TypeScript y Vite</b> integrado con motor WebAssembly aislado y optimización de memoria a 4GB.",
        "tags": ["React 19", "TypeScript", "TailwindCSS", "WebAssembly", "Vite"],
    },
    "Sistema_Optimazacion_Inventario_Algoritmos-y-Estructura-de-Datos-": {
        "title": "Inventory Optimization (Knapsack Problem)",
        "description": "Sistema de optimización de inventarios con <b>Programación Dinámica en Java</b> (Recursivo, Memoización Top-Down y Bottom-Up) y análisis de complejidad formal para la UPS.",
        "tags": ["Java", "Algoritmos", "Dynamic Programming", "Benchmarking"],
    },
    "RPG_Journey": {
        "title": "RPG Journey (Turn-Based Engine)",
        "description": "Videojuego de rol por turnos en <b>Java</b> aplicando POO avanzada, gestión de inventario, atributos de personajes e interfaz gráfica.",
        "tags": ["Java", "OOP", "Game Dev", "GUI"],
    },
}

# Ignore list for repositories that shouldn't appear in recent list
IGNORED_REPO_PATTERNS = ["deber", "examen", "tarea"]

def get_headers():
    token = os.environ.get("GITHUB_TOKEN")
    headers = {
        "User-Agent": "AnthonyPilatasig-Profile-Updater",
        "Accept": "application/vnd.github.v3+json",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers

def fetch_json(url):
    req = urllib.request.Request(url, headers=get_headers())
    try:
        with urllib.request.urlopen(req, timeout=15) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        print(f"HTTP Error {e.code} fetching {url}: {e.reason}")
        return None
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None

def format_relative_time(date_str):
    try:
        dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        now = datetime.now(timezone.utc)
        diff = now - dt
        seconds = diff.total_seconds()
        
        if seconds < 60:
            return "Hace un momento"
        elif seconds < 3600:
            minutes = int(seconds // 60)
            return f"Hace {minutes} {'minuto' if minutes == 1 else 'minutos'}"
        elif seconds < 86400:
            hours = int(seconds // 3600)
            return f"Hace {hours} {'hora' if hours == 1 else 'horas'}"
        elif seconds < 86400 * 30:
            days = int(seconds // 86400)
            return f"Hace {days} {'día' if days == 1 else 'días'}"
        elif seconds < 86400 * 365:
            months = int(seconds // (86400 * 30))
            return f"Hace {months} {'mes' if months == 1 else 'meses'}"
        else:
            years = int(seconds // (86400 * 365))
            return f"Hace {years} {'año' if years == 1 else 'años'}"
    except Exception:
        return date_str[:10]

def build_featured_projects_section(repos):
    featured_keys = list(PROJECT_METADATA.keys())
    repo_map = {r["name"]: r for r in repos if isinstance(r, dict) and "name" in r}
    
    # Also find any other repos with topics 'showcase' or 'featured'
    for r in repos:
        topics = r.get("topics", [])
        if ("showcase" in topics or "featured" in topics) and r["name"] not in featured_keys:
            featured_keys.append(r["name"])
            
    # Take up to 4 top featured projects
    selected = featured_keys[:4]
    
    cards = []
    for name in selected:
        repo = repo_map.get(name)
        meta = PROJECT_METADATA.get(name, {})
        
        title = meta.get("title") or (repo["name"] if repo else name)
        url = repo["html_url"] if repo else f"https://github.com/{USERNAME}/{name}"
        
        desc = meta.get("description")
        if not desc and repo and repo.get("description"):
            desc = repo["description"]
        if not desc:
            desc = "Proyecto en desarrollo continuo y arquitectura moderna."
            
        tags = meta.get("tags")
        if not tags and repo:
            tags = repo.get("topics", [])
            if repo.get("language") and repo["language"] not in tags:
                tags.insert(0, repo["language"])
        if not tags:
            tags = ["Software"]
            
        tags_html = " ".join([f"`{t}`" for t in tags[:6]])
        
        stars = repo.get("stargazers_count", 0) if repo else 0
        stars_badge = f" ★ {stars}" if stars > 0 else ""
        
        cards.append(f"""    <td width="50%" valign="top">
      <h3><a href="{url}">🚀 {title}</a>{stars_badge}</h3>
      <p>{desc}</p>
      <p>{tags_html}</p>
    </td>""")

    # Group into 2 columns per row
    rows = []
    for i in range(0, len(cards), 2):
        chunk = cards[i:i+2]
        if len(chunk) == 1:
            chunk.append('<td width="50%" valign="top"></td>')
        rows.append("  <tr>\n" + "\n".join(chunk) + "\n  </tr>")
        
    table_content = "<table>\n" + "\n".join(rows) + "\n</table>"
    return table_content

def build_recent_repos_section(repos):
    filtered = []
    for r in repos:
        name = r.get("name", "")
        if name == USERNAME or r.get("fork", False) or r.get("private", False):
            continue
        # Filter homework/exam repos from polluting profile
        if any(p in name.lower() for p in IGNORED_REPO_PATTERNS):
            continue
        filtered.append(r)
        
    filtered.sort(key=lambda x: x.get("pushed_at", ""), reverse=True)
    recent = filtered[:6]
    
    rows = []
    for r in recent:
        name = r["name"]
        url = r["html_url"]
        desc = r.get("description") or "—"
        if len(desc) > 85:
            desc = desc[:82] + "..."
        lang = r.get("language") or "General"
        badge_url = LANG_BADGES.get(lang)
        lang_str = f'<img src="{badge_url}" height="20"/>' if badge_url else f"`{lang}`"
        stars = f"⭐ {r.get('stargazers_count', 0)}"
        updated = format_relative_time(r.get("pushed_at", ""))
        
        rows.append(f"| [**{name}**]({url}) | {desc} | {lang_str} | {stars} | {updated} |")
        
    table = "| Repositorio | Descripción | Stack | Stars | Actualizado |\n| :--- | :--- | :---: | :---: | :--- |\n" + "\n".join(rows)
    return table

def build_recent_activity_section(events):
    if not events:
        return "_No hay eventos públicos recientes registrados._"
    
    activities = []
    seen = set()
    
    for ev in events:
        ev_type = ev.get("type")
        repo_name = ev.get("repo", {}).get("name", "")
        repo_url = f"https://github.com/{repo_name}"
        short_repo = repo_name.split("/")[-1] if "/" in repo_name else repo_name
        
        if ev_type == "PushEvent":
            commits = ev.get("payload", {}).get("commits", [])
            for c in commits:
                msg = c.get("message", "").split("\n")[0]
                if not msg:
                    continue
                sha = c.get("sha", "")[:7]
                commit_url = f"{repo_url}/commit/{c.get('sha', '')}"
                dedup_key = f"{repo_name}-{msg}"
                if dedup_key not in seen:
                    seen.add(dedup_key)
                    activities.append(f"- 🔨 Push en [`{short_repo}`]({repo_url}): [`{sha}`]({commit_url}) {msg}")
                    break
        elif ev_type == "PullRequestEvent":
            action = ev.get("payload", {}).get("action", "")
            pr = ev.get("payload", {}).get("pull_request", {})
            title = pr.get("title") or f"Pull Request en {short_repo}"
            pr_url = pr.get("html_url") or repo_url
            number = pr.get("number") or ""
            dedup_key = f"pr-{repo_name}-{number}"
            if dedup_key not in seen:
                seen.add(dedup_key)
                activities.append(f"- 🔀 PR #{number} ({action}) en [`{short_repo}`]({repo_url}): [{title}]({pr_url})")
        elif ev_type == "CreateEvent":
            ref_type = ev.get("payload", {}).get("ref_type", "")
            if ref_type == "repository":
                dedup_key = f"create-repo-{repo_name}"
                if dedup_key not in seen:
                    seen.add(dedup_key)
                    activities.append(f"- ✨ Creado nuevo repositorio: [`{short_repo}`]({repo_url})")
                    
        if len(activities) >= 6:
            break
            
    if not activities:
        return "_Actividad sincronizada automáticamente con GitHub Actions._"
        
    return "\n".join(activities)

def replace_section(content, marker_name, new_text):
    start_marker = f"<!-- {marker_name}:START -->"
    end_marker = f"<!-- {marker_name}:END -->"
    pattern = re.compile(
        re.escape(start_marker) + r".*?" + re.escape(end_marker),
        re.DOTALL
    )
    replacement = f"{start_marker}\n{new_text}\n{end_marker}"
    if pattern.search(content):
        return pattern.sub(lambda _: replacement, content)
    else:
        print(f"Warning: Markers {start_marker} and {end_marker} not found in README.")
        return content

def main():
    print(f"Fetching GitHub data for user {USERNAME}...")
    repos = fetch_json(f"https://api.github.com/users/{USERNAME}/repos?per_page=100&sort=pushed") or []
    events = fetch_json(f"https://api.github.com/users/{USERNAME}/events?per_page=50") or []
    
    if not os.path.exists(README_PATH):
        print(f"Error: README not found at {README_PATH}")
        return
        
    with open(README_PATH, "r", encoding="utf-8") as f:
        readme_content = f.read()
        
    featured_md = build_featured_projects_section(repos)
    recent_repos_md = build_recent_repos_section(repos)
    recent_activity_md = build_recent_activity_section(events)
    
    updated_content = replace_section(readme_content, "FEATURED_PROJECTS", featured_md)
    updated_content = replace_section(updated_content, "RECENT_REPOS", recent_repos_md)
    updated_content = replace_section(updated_content, "RECENT_ACTIVITY", recent_activity_md)
    
    with open(README_PATH, "w", encoding="utf-8") as f:
        f.write(updated_content)
        
    print(f"Successfully updated {README_PATH}")

if __name__ == "__main__":
    main()
