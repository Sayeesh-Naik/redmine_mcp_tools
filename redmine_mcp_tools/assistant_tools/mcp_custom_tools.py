"""
Custom Tools for BYOT app
Includes:
- SimpleGreetingTool
- RedmineTool
"""

import frappe
from frappe import _
from typing import Dict, Any
from datetime import datetime
import requests
from frappe_assistant_core.core.base_tool import BaseTool
import json
from collections import defaultdict
import requests
from datetime import datetime


# -------------------------
# Simple Greeting Tool
# -------------------------
class SimpleGreetingTool(BaseTool):
    def __init__(self):
        super().__init__()
        self.name = "simple_greeting"
        self.description = self._get_description()
        self.category = "BYOT Examples"
        self.source_app = "byot"
        self.dependencies = []
        self.requires_permission = None
        self.default_config = {
            "greeting_style": "friendly",
            "include_time": True,
            "max_name_length": 50,
            "default_language": "en"
        }
        self.inputSchema = {
            "type": "object",
            "properties": {
                "name": {"type": "string", "minLength": 1, "maxLength": 50},
                "greeting_type": {
                    "type": "string",
                    "enum": ["hello", "goodbye", "welcome", "thanks"],
                    "default": "hello"
                },
                "language": {
                    "type": "string",
                    "enum": ["en", "es", "fr", "de"],
                    "default": "en"
                },
                "options": {
                    "type": "object",
                    "properties": {
                        "include_emoji": {"type": "boolean", "default": False},
                        "uppercase": {"type": "boolean", "default": False}
                    }
                }
            },
            "required": ["name"]
        }

    def _get_description(self) -> str:
        return """Generate personalized greetings with various styles and languages."""

    def execute(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        name = arguments.get("name", "").strip()
        greeting_type = arguments.get("greeting_type", "hello")
        language = arguments.get("language", "en")
        options = arguments.get("options", {})
        config = self.get_config()

        try:
            if len(name) > config.get("max_name_length", 50):
                return {"success": False, "error": "Name too long"}

            greeting = self._generate_greeting(name, greeting_type, language, options, config)

            if options.get("uppercase"):
                greeting = greeting.upper()

            return {
                "success": True,
                "result": {
                    "greeting": greeting,
                    "name": name,
                    "type": greeting_type,
                    "language": language,
                    "timestamp": datetime.now().isoformat(),
                    "metadata": {
                        "greeting_style": config.get("greeting_style"),
                        "options_applied": options,
                        "character_count": len(greeting),
                    },
                },
            }
        except Exception as e:
            frappe.log_error(title=_("Simple Greeting Tool Error"), message=str(e))
            return {"success": False, "error": str(e)}

    def _generate_greeting(self, name, greeting_type, language, options, config) -> str:
        greetings = {
            "en": {
                "hello": f"Hello {name}",
                "goodbye": f"Goodbye {name}",
                "welcome": f"Welcome {name}",
                "thanks": f"Thanks {name}"
            },
            "es": {"hello": f"Hola {name}", "goodbye": f"Adiós {name}", "welcome": f"Bienvenido {name}", "thanks": f"Gracias {name}"},
            "fr": {"hello": f"Bonjour {name}", "goodbye": f"Au revoir {name}", "welcome": f"Bienvenue {name}", "thanks": f"Merci {name}"},
            "de": {"hello": f"Hallo {name}", "goodbye": f"Auf Wiedersehen {name}", "welcome": f"Willkommen {name}", "thanks": f"Danke {name}"},
        }

        greeting = greetings.get(language, greetings["en"]).get(greeting_type, f"Hello {name}")

        if config.get("include_time"):
            greeting += f" (at {datetime.now().strftime('%H:%M:%S')})"

        if options.get("include_emoji"):
            greeting += " 🙂"

        return greeting


# -------------------------
# Redmine Tool
# -------------------------
class RedmineTool(BaseTool):
    # Credentials / constants
    API_URL = "https://redmine.promantia.in"
    API_KEY = "817ac36e7e9315d404965b34df7175a7344e506f"
    USER_EMAIL = "sayeesh.naik@promantia.com"
    USER_NAME = "Sayeesh Naik"

    def __init__(self):
        super().__init__()
        self.name = "redmine"
        self.display_name = "Redmine Integration Tool"
        self.description = self._get_description()
        self.version = "1.0.0"
        self.author = "Sayeesh Naik"
        self.author_email = "sayeesh.naik@promantia.com"
        self.category = "Integration"
        self.source_app = "byot"
        self.dependencies = ["requests"]
        self.requires_permission = None
        self.default_config = {
            "api_url": self.API_URL,
            "api_key": self.API_KEY,
            "timeout": 30
        }
        self.inputSchema = {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["list_projects", "list_issues", "get_issue", "create_issue", "update_issue"]
                },
                "project_id": {"type": "string"},
                "issue_id": {"type": "integer"},
                "subject": {"type": "string"},
                "description": {"type": "string"},
                "updates": {"type": "object"}  # dictionary of fields to update
            },
            "required": ["action"]
        }

    def _get_description(self) -> str:
        return """This tool provides a seamless interface to interact with the Redmine project management system. 
        It allows users to perform key actions:
        * List Projects: Retrieve all projects accessible via Redmine API
        * List Issues: Get all issues for a specific project or globally
        * Get Issue Details: Fetch detailed information of a single issue by its ID
        * Create Issue: Open a new issue in a selected project
        * Update Issue: Modify existing issues (subject, description, status, custom fields)
        """

    def execute(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        api_url = self.API_URL
        api_key = self.API_KEY
        timeout = 30
        headers = {"X-Redmine-API-Key": api_key, "Content-Type": "application/json"}

        try:
            action = arguments["action"]

            # -----------------------------
            # List all Redmine projects
            # -----------------------------
            if action == "list_projects":
                resp = requests.get(f"{api_url}/projects.json", headers=headers, timeout=timeout)
                resp.raise_for_status()
                return {"success": True, "result": resp.json()}

            # -----------------------------
            # List issues for a project or all
            # -----------------------------
            elif action == "list_issues":
                project_id = arguments.get("project_id")
                url = f"{api_url}/issues.json"
                if project_id:
                    url += f"?project_id={project_id}"
                resp = requests.get(url, headers=headers, timeout=timeout)
                resp.raise_for_status()
                return {"success": True, "result": resp.json()}

            # -----------------------------
            # Get details of a single issue
            # -----------------------------
            elif action == "get_issue":
                issue_id = arguments.get("issue_id")
                if not issue_id:
                    return {"success": False, "error": "Missing issue_id"}
                resp = requests.get(f"{api_url}/issues/{issue_id}.json", headers=headers, timeout=timeout)
                resp.raise_for_status()
                return {"success": True, "result": resp.json()}

            # -----------------------------
            # Create a new Redmine issue
            # -----------------------------
            elif action == "create_issue":
                project_id = arguments.get("project_id")
                subject = arguments.get("subject")
                description = arguments.get("description", "")
                if not project_id or not subject:
                    return {"success": False, "error": "project_id and subject are required"}

                payload = {
                    "issue": {
                        "project_id": project_id,
                        "subject": subject,
                        "description": description
                    }
                }
                resp = requests.post(f"{api_url}/issues.json", headers=headers, json=payload, timeout=timeout)
                resp.raise_for_status()
                return {"success": True, "result": resp.json()}

            # -----------------------------
            # Update an existing Redmine issue
            # -----------------------------
            elif action == "update_issue":
                issue_id = arguments.get("issue_id")
                updates = arguments.get("updates", {})
                if not issue_id:
                    return {"success": False, "error": "Missing issue_id"}
                if not updates:
                    return {"success": False, "error": "No fields to update provided"}

                # Make sure description is fully replaced
                if "description" in updates:
                    # Optional: fetch current description if you want to append
                    resp_current = requests.get(f"{api_url}/issues/{issue_id}.json", headers=headers, timeout=timeout)
                    resp_current.raise_for_status()
                    current_desc = resp_current.json()["issue"].get("description", "")
                    updates["description"] = current_desc + "\n" + updates["description"]

                payload = {"issue": updates}
                resp = requests.put(f"{api_url}/issues/{issue_id}.json", headers=headers, json=payload, timeout=timeout)
                resp.raise_for_status()
                return {"success": True, "result": resp.json()}


        except Exception as e:
            frappe.log_error(title=_("Redmine Tool Error"), message=str(e))
            return {"success": False, "error": str(e)}

# -------------------------
# Redmine Issue Report Tool
# -------------------------
class RedmineIssueReporterTool(BaseTool):
    # Hardcoded credentials
    API_URL = "https://redmine.promantia.in"
    API_KEY = "817ac36e7e9315d404965b34df7175a7344e506f"

    def __init__(self):
        super().__init__()
        self.name = "redmine_issue_reporter"
        self.description = "Generate summarized Redmine issue reports for management with visual dashboard using project name."
        self.category = "Integration"
        self.source_app = "byot"
        self.dependencies = ["requests"]
        self.requires_permission = None
        self.default_config = {
            "api_url": self.API_URL,
            "api_key": self.API_KEY,
            "timeout": 30
        }
        self.inputSchema = {
            "type": "object",
            "properties": {
                "project_name": {"type": "string", "description": "Redmine Project Name"},
                "filter": {"type": "string", "description": "Optional filter: status, assignee, priority"},
            },
            "required": ["project_name"]
        }

    def fetch_issues(self):
        """Fetch all issues from Redmine for the project."""
        url = f"{self.API_URL}/issues.json?project_id={self.PROJECT_ID}&status_id=*&limit=100"
        headers = {"X-Redmine-API-Key": self.API_KEY}
        all_issues = []
        offset = 0

        while True:
            response = requests.get(f"{url}&offset={offset}", headers=headers)
            if response.status_code != 200:
                raise Exception(f"Failed to fetch issues: {response.text}")

            data = response.json()
            issues = data.get("issues", [])
            all_issues.extend(issues)

            if len(issues) < 100:
                break
            offset += 100

        return all_issues

    def fetch_project_name(self):
        """Fetch project name for display in dashboard."""
        url = f"{self.API_URL}/projects/{self.PROJECT_ID}.json"
        headers = {"X-Redmine-API-Key": self.API_KEY}
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json().get("project", {}).get("name", self.PROJECT_ID)
        return self.PROJECT_ID

    def generate_dashboard(self, issues, project_name):
        """Generate modern HTML dashboard with glass morphism effect"""
        users_issues = defaultdict(list)
        for issue in issues:
            assignee = issue.get("assigned_to", {}).get("name", "Unassigned")
            users_issues[assignee].append(issue)

        # Summary metrics
        total_issues = len(issues)
        high_priority = sum(1 for i in issues if i.get("priority", {}).get("name", "").lower() == "high")
        normal_priority = sum(1 for i in issues if i.get("priority", {}).get("name", "").lower() == "normal")
        unique_assignees = len(users_issues.keys())

        # Color palette
        colors = {
            'primary': 'rgba(101, 87, 255, 0.8)',
            'secondary': 'rgba(41, 201, 255, 0.8)',
            'success': 'rgba(46, 213, 115, 0.8)',
            'danger': 'rgba(255, 71, 87, 0.8)',
            'warning': 'rgba(255, 165, 2, 0.8)',
            'dark': 'rgba(30, 30, 40, 0.85)',
            'light': 'rgba(245, 245, 255, 0.9)'
        }

        # Glass morphism summary cards
        summary_cards = f"""
        <div class="grand-report">
            <div class="metric-card" style="border-top: 4px solid {colors['primary']}">
                <div class="metric-value">{total_issues}</div>
                <div class="metric-label">Total Issues</div>
            </div>
            <div class="metric-card" style="border-top: 4px solid {colors['danger']}">
                <div class="metric-value">{high_priority}</div>
                <div class="metric-label">High Priority</div>
            </div>
            <div class="metric-card" style="border-top: 4px solid {colors['success']}">
                <div class="metric-value">{normal_priority}</div>
                <div class="metric-label">Normal Priority</div>
            </div>
            <div class="metric-card" style="border-top: 4px solid {colors['warning']}">
                <div class="metric-value">{unique_assignees}</div>
                <div class="metric-label">Unique Assignees</div>
            </div>
        </div>
        """

        # Per-user sections
        html_sections = []
        for user, issues_list in users_issues.items():
            status_count = defaultdict(int)
            priority_count = defaultdict(int)
            tracker_count = defaultdict(int)

            for issue in issues_list:
                status_count[issue.get("status", {}).get("name", "Unknown")] += 1
                priority_count[issue.get("priority", {}).get("name", "Unknown")] += 1
                tracker_count[issue.get("tracker", {}).get("name", "Unknown")] += 1

            # Generate chart colors
            status_colors = [f"hsla({i * 360 / len(status_count)}, 70%, 50%, 0.7)" for i in range(len(status_count))]
            priority_colors = [f"hsla({i * 360 / len(priority_count)}, 70%, 50%, 0.7)" for i in range(len(priority_count))]
            tracker_colors = [f"hsla({i * 360 / len(tracker_count)}, 70%, 50%, 0.7)" for i in range(len(tracker_count))]

            # HTML section with glass morphism
            section_html = f"""
            <div class="assignee-section">
                <div class="section-header">
                    <h2>{user}</h2>
                    <span class="badge">{len(issues_list)} issues</span>
                </div>
                
                <div class="chart-container">
                    <div class="chart-card">
                        <h3>Status Distribution</h3>
                        <canvas id="statusChart_{user.replace(' ', '_')}" height="200"></canvas>
                    </div>
                    <div class="chart-card">
                        <h3>Priority Distribution</h3>
                        <canvas id="priorityChart_{user.replace(' ', '_')}" height="200"></canvas>
                    </div>
                    <div class="chart-card">
                        <h3>Tracker Distribution</h3>
                        <canvas id="trackerChart_{user.replace(' ', '_')}" height="200"></canvas>
                    </div>
                </div>
                
                <div class="table-container">
                    <h3>Issue Details</h3>
                    <div class="table-scroll">
                        <table>
                            <thead>
                                <tr>
                                    <th>ID</th>
                                    <th>Subject</th>
                                    <th>Status</th>
                                    <th>Priority</th>
                                    <th>Tracker</th>
                                    <th>Created</th>
                                </tr>
                            </thead>
                            <tbody>
            """
            
            for issue in issues_list:
                created_on = issue.get("created_on", "").split('T')[0] if issue.get("created_on") else "N/A"
                section_html += f"""
                                <tr>
                                    <td>{issue.get("id")}</td>
                                    <td>{issue.get("subject")}</td>
                                    <td><span class="status-badge" style="background-color: {status_colors[list(status_count.keys()).index(issue.get("status", {}).get("name", "Unknown"))]}">{issue.get("status", {}).get("name", "")}</span></td>
                                    <td><span class="priority-badge" style="background-color: {priority_colors[list(priority_count.keys()).index(issue.get("priority", {}).get("name", "Unknown"))]}">{issue.get("priority", {}).get("name", "")}</span></td>
                                    <td><span class="tracker-badge" style="background-color: {tracker_colors[list(tracker_count.keys()).index(issue.get("tracker", {}).get("name", "Unknown"))]}">{issue.get("tracker", {}).get("name", "")}</span></td>
                                    <td>{created_on}</td>
                                </tr>
                """
            
            section_html += """
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
            
            <script>
            // Status Chart
            new Chart(
                document.getElementById('statusChart_""" + user.replace(' ', '_') + """'),
                {
                    type: 'doughnut',
                    data: {
                        labels: """ + str(list(status_count.keys())) + """,
                        datasets: [{
                            data: """ + str(list(status_count.values())) + """,
                            backgroundColor: """ + str(status_colors) + """,
                            borderWidth: 1,
                            borderColor: 'rgba(255, 255, 255, 0.1)'
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {
                            legend: {
                                position: 'right',
                                labels: {
                                    color: '""" + colors['light'] + """'
                                }
                            }
                        }
                    }
                }
            );
            
            // Priority Chart
            new Chart(
                document.getElementById('priorityChart_""" + user.replace(' ', '_') + """'),
                {
                    type: 'pie',
                    data: {
                        labels: """ + str(list(priority_count.keys())) + """,
                        datasets: [{
                            data: """ + str(list(priority_count.values())) + """,
                            backgroundColor: """ + str(priority_colors) + """,
                            borderWidth: 1,
                            borderColor: 'rgba(255, 255, 255, 0.1)'
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {
                            legend: {
                                position: 'right',
                                labels: {
                                    color: '""" + colors['light'] + """'
                                }
                            }
                        }
                    }
                }
            );
            
            // Tracker Chart
            new Chart(
                document.getElementById('trackerChart_""" + user.replace(' ', '_') + """'),
                {
                    type: 'polarArea',
                    data: {
                        labels: """ + str(list(tracker_count.keys())) + """,
                        datasets: [{
                            data: """ + str(list(tracker_count.values())) + """,
                            backgroundColor: """ + str(tracker_colors) + """,
                            borderWidth: 1,
                            borderColor: 'rgba(255, 255, 255, 0.1)'
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {
                            legend: {
                                position: 'right',
                                labels: {
                                    color: '""" + colors['light'] + """'
                                }
                            }
                        }
                    }
                }
            );
            </script>
            """
            html_sections.append(section_html)

        # Final HTML with glass morphism styling
        final_html = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Redmine Dashboard | {project_name}</title>
            <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
            <style>
                :root {{
                    --primary: {colors['primary']};
                    --secondary: {colors['secondary']};
                    --success: {colors['success']};
                    --danger: {colors['danger']};
                    --warning: {colors['warning']};
                    --dark: {colors['dark']};
                    --light: {colors['light']};
                    --shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
                    --border: 1px solid rgba(255, 255, 255, 0.1);
                    --transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
                }}

                * {{
                    margin: 0;
                    padding: 0;
                    box-sizing: border-box;
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                }}

                body {{
                    background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
                    color: white;
                    min-height: 100vh;
                    padding: 20px;
                }}

                .dashboard {{
                    max-width: 1400px;
                    margin: 0 auto;
                }}

                .header {{
                    text-align: center;
                    margin-bottom: 30px;
                    padding: 20px;
                    background: rgba(30, 30, 40, 0.6);
                    backdrop-filter: blur(10px);
                    border-radius: 15px;
                    border: var(--border);
                    box-shadow: var(--shadow);
                    transition: var(--transition);
                }}

                .header:hover {{
                    transform: translateY(-2px);
                    box-shadow: 0 12px 40px rgba(0, 0, 0, 0.4);
                }}

                h1 {{
                    font-size: 2.5rem;
                    margin-bottom: 10px;
                    background: linear-gradient(to right, var(--primary), var(--secondary));
                    -webkit-background-clip: text;
                    background-clip: text;
                    color: transparent;
                }}

                .subtitle {{
                    font-size: 1.1rem;
                    opacity: 0.8;
                }}

                .grand-report {{
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                    gap: 20px;
                    margin-bottom: 30px;
                }}

                .metric-card {{
                    background: rgba(30, 30, 40, 0.6);
                    backdrop-filter: blur(10px);
                    border-radius: 15px;
                    padding: 20px;
                    border: var(--border);
                    box-shadow: var(--shadow);
                    transition: var(--transition);
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                    text-align: center;
                }}

                .metric-card:hover {{
                    transform: translateY(-5px);
                    box-shadow: 0 15px 35px rgba(0, 0, 0, 0.4);
                }}

                .metric-value {{
                    font-size: 2.5rem;
                    font-weight: 700;
                    margin: 10px 0;
                }}

                .metric-label {{
                    font-size: 0.9rem;
                    opacity: 0.8;
                }}

                .assignee-section {{
                    margin-bottom: 40px;
                    background: rgba(30, 30, 40, 0.6);
                    backdrop-filter: blur(10px);
                    border-radius: 15px;
                    border: var(--border);
                    box-shadow: var(--shadow);
                    overflow: hidden;
                    transition: var(--transition);
                    padding: 20px;
                }}

                .assignee-section:hover {{
                    transform: translateY(-3px);
                    box-shadow: 0 12px 40px rgba(0, 0, 0, 0.4);
                }}

                .section-header {{
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    margin-bottom: 20px;
                    padding-bottom: 10px;
                    border-bottom: var(--border);
                }}

                .section-header h2 {{
                    margin: 0;
                    font-size: 1.5rem;
                }}

                .badge {{
                    background: var(--primary);
                    padding: 5px 15px;
                    border-radius: 20px;
                    font-size: 0.9rem;
                    font-weight: bold;
                }}

                .chart-container {{
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                    gap: 20px;
                    margin-bottom: 30px;
                }}

                .chart-card {{
                    background: rgba(30, 30, 40, 0.5);
                    backdrop-filter: blur(5px);
                    border-radius: 10px;
                    padding: 15px;
                    border: var(--border);
                }}

                .chart-card h3 {{
                    margin-top: 0;
                    margin-bottom: 15px;
                    font-size: 1.1rem;
                }}

                .table-container {{
                    margin-top: 20px;
                }}

                .table-container h3 {{
                    margin-bottom: 15px;
                }}

                .table-scroll {{
                    max-height: 400px;
                    overflow-y: auto;
                    border-radius: 10px;
                    border: var(--border);
                }}

                table {{
                    width: 100%;
                    border-collapse: collapse;
                }}

                th, td {{
                    padding: 12px 15px;
                    text-align: left;
                    border-bottom: var(--border);
                }}

                th {{
                    position: sticky;
                    top: 0;
                    background: rgba(30, 30, 40, 0.9);
                    backdrop-filter: blur(10px);
                    font-weight: 600;
                }}

                tr:hover {{
                    background: rgba(255, 255, 255, 0.05);
                }}

                .status-badge, .priority-badge, .tracker-badge {{
                    display: inline-block;
                    padding: 3px 10px;
                    border-radius: 12px;
                    font-size: 0.8rem;
                    font-weight: 500;
                }}

                @media (max-width: 768px) {{
                    .grand-report {{
                        grid-template-columns: 1fr;
                    }}
                    
                    .chart-container {{
                        grid-template-columns: 1fr;
                    }}
                }}
            </style>
        </head>
        <body>
            <div class="dashboard">
                <div class="header">
                    <h1>Redmine Project Dashboard</h1>
                    <div class="subtitle">{project_name}</div>
                </div>
                
                {summary_cards}
                
                {''.join(html_sections)}
            </div>
        </body>
        </html>
        """
        return final_html

    def execute(self, inputs: dict = None) -> str:
        """
        Main execution:
        - If user prompt mentions 'dashboard' OR 'report', return visual dashboard.
        - Default also returns dashboard (to keep unified output).
        """

        # Get project name from user input
        project_name = inputs.get("project_name")
        user_filter = inputs.get("filter", "").lower() if inputs else ""

        # Fetch issues
        issues = self.fetch_issues()
        project_display_name = self.fetch_project_name()

        # Always prefer dashboard view if 'dashboard' or 'report' mentioned
        if "dashboard" in user_filter or "report" in user_filter:
            html_output = self.generate_dashboard(issues, project_display_name)
        else:
            # Default also goes to dashboard (so only one UI is maintained)
            html_output = self.generate_dashboard(issues, project_display_name)

        return html_output






# -------------------------
# Export tools for Frappe Assistant Core
# -------------------------
__all__ = [
        "SimpleGreetingTool",
        "RedmineTool", 
        "RedmineIssueReporterTool",
    ]
