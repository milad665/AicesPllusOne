import requests
import logging
import json
from typing import List, Dict, Any, Optional
from google.adk.agents import LlmAgent

# ----------------------------
# Logging setup and helpers
# ----------------------------
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
LOG_PREFIX = "MyLog :::::::::::"

def _safe_repr(value: Any, max_len: int = 2000) -> str:
    """Make values safe & compact for logging."""
    try:
        if isinstance(value, (dict, list)):
            out = json.dumps(value, ensure_ascii=False, indent=2)
        else:
            out = str(value)
    except Exception as e:
        out = f"<unrepresentable: {type(value).__name__} ({e})>"
    if len(out) > max_len:
        return out[:max_len] + f"... [truncated {len(out)-max_len} chars]"
    return out

def log_step(unit: str, result: Any = None) -> None:
    logging.info("%s %s", LOG_PREFIX, unit)
    if result is not None:
        logging.info("result: %s", _safe_repr(result))

# ----------------------------
# Constants
# ----------------------------
API_BASE = "https://aices-plus-one-analyzer-691085128403.europe-west1.run.app"
log_step("Set API_BASE", API_BASE)

TIMEOUT_S = 30
log_step("Set TIMEOUT_S", TIMEOUT_S)

# ----------------------------
# Optional tool example
# ----------------------------
def clone_repository(repo_url: str) -> bool:
    log_step("Enter clone_repository(repo_url)")
    print(f"Cloned repository {repo_url}")
    result = True
    log_step("Return from clone_repository", result)
    return result

# ----------------------------
# Data fetchers
# ----------------------------
def fetch_projects() -> List[Dict[str, Any]]:
    """
    GET /projects -> list of lightweight project items (with id, project_type, language).
    """
    log_step("Enter fetch_projects()")

    url = f"{API_BASE}/projects"
    log_step("Construct URL for /projects", url)

    resp = requests.get(url, headers={"accept": "application/json"}, timeout=TIMEOUT_S)
    log_step("HTTP GET /projects response object", {"status_code": getattr(resp, "status_code", None)})

    resp.raise_for_status()
    log_step("resp.raise_for_status()", "OK")

    data = resp.json()
    log_step("Parse JSON from /projects", data)

    if not isinstance(data, list):
        log_step("Type check /projects failed", type(data).__name__)
        raise ValueError("Unexpected /projects response shape; expected a list.")
    log_step("Type check /projects passed", "list")

    ids = [p.get("id") for p in data if isinstance(p, dict)]
    log_step("Summarize /projects ids", ids)

    log_step("Return from fetch_projects()", f"{len(data)} items")
    return data

def fetch_project_entrypoints(project_id: str) -> List[Dict[str, Any]]:
    """
    GET /projects/{project_id}/entrypoints -> list of entry points for the given project.
    Expected item shape:
      {
        "name": "string",
        "file_path": "string",
        "line_number": 0,
        "type": "string",
        "parameters": [],
        "return_type": "string",
        "documentation": "string"
      }
    """
    log_step("Enter fetch_project_entrypoints(project_id)", project_id)

    url = f"{API_BASE}/projects/{project_id}/entrypoints"
    log_step("Construct URL for /projects/{id}/entrypoints", url)

    resp = requests.get(url, headers={"accept": "application/json"}, timeout=TIMEOUT_S)
    log_step(
        "HTTP GET /projects/{id}/entrypoints response object",
        {"status_code": getattr(resp, "status_code", None), "url": getattr(resp, "url", url)}
    )

    resp.raise_for_status()
    log_step("resp.raise_for_status()", "OK")

    data = resp.json()
    log_step("Parse JSON from /entrypoints", data)

    if not isinstance(data, list):
        log_step("Type check /entrypoints failed", type(data).__name__)
        raise ValueError(f"Unexpected /projects/{project_id}/entrypoints response shape; expected a list.")
    log_step("Type check /entrypoints passed", "list")

    log_step("Return from fetch_project_entrypoints()", f"{len(data)} items")
    return data

# ----------------------------
# Prompt builder (aligned with your C# strings)
# ----------------------------
def build_instruction_from_api(
    project_description: str,
) -> str:
    """
    Builds the final instruction string whose content matches your C# GenerateSystemContextAsync:
      - systemPrompt: exact same text
      - userPrompt: project list and entry points formatted to match your example
    Entry points are fetched per-project and mapped as:
      Project.Name   -> project_id
      Identifier     -> entrypoint['name']
      EntryPointType -> entrypoint['type']
      Route          -> entrypoint['file_path']
    """
    log_step("Enter build_instruction_from_api(project_description)", {"project_description": project_description})

    # (1) Fetch all projects
    projects_index = fetch_projects()
    log_step("Fetched projects_index", {"count": len(projects_index)})

    # (2) For each project, fetch entry points and accumulate both projects and entry points
    detailed_projects: List[Dict[str, Any]] = []
    accumulated_entrypoints: List[Dict[str, Any]] = []
    log_step("Initialize detailed_projects list", detailed_projects)
    log_step("Initialize accumulated_entrypoints list", accumulated_entrypoints)

    for p in projects_index:
        log_step("Loop project p", p)
        pid = p.get("id")
        log_step("Extract pid", pid)

        if not pid:
            log_step("Skip project without id", p)
            continue

        # Treat p itself as our "ProjectConfiguration" row for the prompt
        detailed_projects.append(p)
        log_step("Append p to detailed_projects (size now)", len(detailed_projects))

        # Fetch entry points for this project (correct endpoint)
        eps = fetch_project_entrypoints(pid)
        log_step("Fetched entry points for project", {"project_id": pid, "count": len(eps)})

        # Attach project_id for formatting later
        for ep in eps:
            ep_with_pid = dict(ep)
            ep_with_pid["_project_id"] = pid
            accumulated_entrypoints.append(ep_with_pid)
            log_step("Append ep_with_pid to accumulated_entrypoints (size now)", len(accumulated_entrypoints))

    # (3) Build project list lines:
    #     "{ProjectId}->{ProjectTypes}, Language: {ProgrammingLanguage}"
    # Our API returns "project_type" and "language".
    project_lines: List[str] = []
    log_step("Initialize project_lines", project_lines)

    for d in detailed_projects:
        log_step("Loop project d", d)
        pid = d.get("id", "unknown-id")
        log_step("d.id", pid)

        proj_type = d.get("project_type") or ""
        log_step("d.project_type (raw)", proj_type)

        lang = d.get("language") or ""
        log_step("d.language", lang)

        if isinstance(proj_type, list):
            proj_type_str = ",".join([str(x) for x in proj_type])
            log_step("Joined proj_type list", proj_type_str)
        else:
            proj_type_str = str(proj_type) if proj_type else ""
            log_step("proj_type coerced to string", proj_type_str)

        line = f"{pid}->{proj_type_str}, Language: {lang}"
        log_step("Built project line", line)

        project_lines.append(line)
        log_step("Append line to project_lines (size now)", len(project_lines))

    # (4) Build entry point lines:
    #     $"{e.Project.Name}->{e.Identifier}({e.EntryPointType}):{e.Route}"
    # Map from API: name->Identifier, type->EntryPointType, file_path->Route, project_id->Project.Name
    ep_lines: List[str] = []
    log_step("Initialize ep_lines", ep_lines)

    for e in accumulated_entrypoints:
        log_step("Loop entrypoint e", e)
        proj_name = e.get("_project_id", "unknown-project")
        log_step("e.Project.Name (from pid)", proj_name)

        identifier = e.get("name", "unknown")
        log_step("e.Identifier (name)", identifier)

        ep_type = e.get("type", "unknown")
        log_step("e.EntryPointType (type)", ep_type)

        route = e.get("file_path", "")
        log_step("e.Route (file_path)", route)

        ep_line = f"{proj_name}->{identifier}({ep_type}):{route}"
        log_step("Built ep_line", ep_line)

        ep_lines.append(ep_line)
        log_step("Append ep_line to ep_lines (size now)", len(ep_lines))

    # (5) Build *exact* prompt text (content matches your C#)
    system_prompt = (
        "You are a software architect assistant. Your job is to design a software architecture model using the C4 model, "
        "based on a given system description, project types, and entry points. "
        "Return the architecture in the provided JSON format. "
        "Use the 'Exists' property in C4 element classes (container, component, person, softwaresystem) to distinguish between existing and future elements. "
        "In the PlantUML script, paint new elements in red."
    )
    log_step("Set system_prompt", system_prompt)

    user_prompt = (
        f"*Project description:* {project_description}\n"
        "*Project list:*\n"
        f"{'\n-    '.join(project_lines)}\n"
        "*Entry points:*\n"
        f"{'\n-    '.join(ep_lines) if ep_lines else ''}\n"
    )
    log_step("Set user_prompt", user_prompt)

    instruction = f"{system_prompt}\n\n{user_prompt}"
    log_step("Compose final instruction (length chars)", len(instruction))
    log_step("FINAL INSTRUCTION", instruction)

    log_step("Return from build_instruction_from_api()", "instruction string ready")
    return instruction

# ----------------------------
# Build the agent with the live instruction text
# ----------------------------
project_description_text = "Describe the overall system here (business goals, major capabilities, non-functionals)."
log_step("Set project_description_text", project_description_text)

instruction_text = build_instruction_from_api(project_description=project_description_text)
log_step("instruction_text created (length)", len(instruction_text))
log_step("instruction_text (preview)", instruction_text)

root_agent = LlmAgent(
    model="gemini-2.0-flash",
    name="gemini_flash_agent",
    instruction=instruction_text,
    tools=[clone_repository],
)
log_step("root_agent created", {"model": "gemini-2.0-flash", "name": "gemini_flash_agent"})

# (Optional) For debugging:
# print(root_agent.instruction)
