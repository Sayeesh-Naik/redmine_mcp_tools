"""
Custom Tools for BYOT app
Includes:
- SimpleGreetingTool
- RedmineTool
"""

import frappe
from frappe import Optional, _
from typing import Dict, Any, List
from datetime import datetime
import requests
from frappe_assistant_core.core.base_tool import BaseTool
import json
from collections import defaultdict
import requests
from datetime import datetime, timedelta
import json
from datetime import datetime, timedelta
import random 


# -------------------------
# Redmine Issue Tool
# -------------------------
class RedmineIssueTool(BaseTool):
    # Credentials / constants
    API_URL = "https://redmine.promantia.in"
    API_KEY = "817ac36e7e9315d404965b34df7175a7344e506f"
    USER_EMAIL = "sayeesh.naik@promantia.com"
    USER_NAME = "Sayeesh Naik"

    def __init__(self):
        super().__init__()
        self.name = "redmine_issue_tool"
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
# Redmine Dashboard Tool
# ------------------------
class RedmineDashboardTool(BaseTool):
    # Hardcoded credentials
    API_URL = "https://redmine.promantia.in"
    API_KEY = "817ac36e7e9315d404965b34df7175a7344e506f"

    def __init__(self):
        super().__init__()
        self.name = "redmine_dashboard_tool"
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

    def _get_project_id(self, project_name: str, headers: dict, timeout: int) -> Optional[int]:
        """Fetch project ID by project name"""
        resp = requests.get(f"{self.API_URL}/projects.json", headers=headers, timeout=timeout)
        resp.raise_for_status()
        projects = resp.json().get("projects", [])
        return next((p["id"] for p in projects if p["name"].lower() == project_name.lower()), None)

    def _fetch_all_issues(self, project_id: int, headers: dict, timeout: int) -> List[dict]:
        """Fetch all issues for a project with pagination"""
        issues = []
        offset = 0
        while True:
            resp = requests.get(
                f"{self.API_URL}/issues.json?project_id={project_id}&limit=100&offset={offset}",
                headers=headers,
                timeout=timeout
            )
            resp.raise_for_status()
            data = resp.json()
            issues.extend(data.get("issues", []))
            if offset + 100 >= data.get("total_count", 0):
                break
            offset += 100
        return issues

    def _group_issues_by_assignee(self, issues: List[dict]) -> defaultdict:
        """Group issues by assignee"""
        users_issues = defaultdict(list)
        for issue in issues:
            assignee = issue.get("assigned_to", {}).get("name") or "Unassigned"
            users_issues[assignee].append(issue)
        return users_issues

    def _generate_issue_row(self, issue: dict, index: int) -> str:
        """Generate HTML row for an issue"""
        priority = issue.get("priority", {}).get("name") or "Normal"
        status = issue.get("status", {}).get("name") or "Open"
        
        # Priority and status colors
        PRIORITY_COLORS = {
            "high": "#ff4757",
            "normal": "#2ed573",
            "low": "#1e90ff"
        }
        STATUS_COLORS = {
            "New": "#a4b0be",
            "In Progress": "#ffa502",
            "Deployed to UAT": "#3742fa",
            "Deployed to Production": "#2ed573",
            "Awaiting For Customer Demo": "#9b59b6",
            "On Hold": "#e67e22",
            "default": "#7f8c8d"
        }
        
        # Overdue calculation
        today = datetime.today().date()
        due_date = issue.get("due_date")
        overdue = ""
        if due_date:
            due_dt = datetime.strptime(due_date, "%Y-%m-%d").date()
            if due_dt < today:
                overdue = " (Overdue)"
        
        # Row styling
        bg_color = "rgba(255, 255, 255, 0.05)" if index % 2 else "rgba(255, 255, 255, 0.1)"
        priority_bg = PRIORITY_COLORS.get(priority.lower(), "#2ed573")
        status_bg = STATUS_COLORS.get(status, STATUS_COLORS["default"])
        
        return f"""
        <tr style="background-color:{bg_color}">
            <td style="padding:12px; border-bottom:1px solid rgba(255,255,255,0.1)">{issue['id']}</td>
            <td style="padding:12px; border-bottom:1px solid rgba(255,255,255,0.1)">{issue['subject']}</td>
            <td style="padding:12px; border-bottom:1px solid rgba(255,255,255,0.1); background-color:{priority_bg}">{priority}</td>
            <td style="padding:12px; border-bottom:1px solid rgba(255,255,255,0.1); background-color:{status_bg}">{status}{overdue}</td>
        </tr>
        """

    def _generate_user_section(self, user: str, user_issues: List[dict]) -> str:
        """Generate HTML section for a user with charts and issue table"""
        priority_count = defaultdict(int)
        status_count = defaultdict(int)
        summary_rows = []
        
        for i, issue in enumerate(user_issues):
            priority = issue.get("priority", {}).get("name") or "Normal"
            status = issue.get("status", {}).get("name") or "Open"
            priority_count[priority] += 1
            status_count[status] += 1
            summary_rows.append(self._generate_issue_row(issue, i))
        
        # Prepare chart data
        priority_labels = list(priority_count.keys())
        priority_values = [priority_count[k] for k in priority_labels]
        status_labels = list(status_count.keys())
        status_values = [status_count[k] for k in status_labels]
        
        # Generate unique IDs for charts
        user_id = user.replace(" ", "_")
        
        return f"""
        <div class="user-section">
            <h2 class="user-title">{user}</h2>
            <div class="chart-container">
                <div class="chart-box">
                    <canvas id="{user_id}_priorityChart"></canvas>
                </div>
                <div class="chart-box">
                    <canvas id="{user_id}_statusChart"></canvas>
                </div>
            </div>
            <h3 class="table-title">Ticket Summary</h3>
            <div class="table-container">
                <table class="issue-table">
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>Subject</th>
                            <th>Priority</th>
                            <th>Status</th>
                        </tr>
                    </thead>
                    <tbody>
                        {''.join(summary_rows)}
                    </tbody>
                </table>
            </div>
            <script>
                // Priority Chart
                new Chart(
                    document.getElementById('{user_id}_priorityChart').getContext('2d'), {{
                        type: 'bar',
                        data: {{
                            labels: {json.dumps(priority_labels)},
                            datasets: [{{
                                label: 'Priority Count',
                                data: {json.dumps(priority_values)},
                                backgroundColor: [
                                    '#ff4757', '#2ed573', '#1e90ff', '#ffa502', '#9b59b6'
                                ],
                                borderColor: 'rgba(255, 255, 255, 0.2)',
                                borderWidth: 1
                            }}]
                        }},
                        options: {{
                            responsive: true,
                            maintainAspectRatio: false,
                            plugins: {{
                                legend: {{ display: false }},
                                title: {{ 
                                    display: true, 
                                    text: 'Priority Distribution',
                                    color: '#ffffff',
                                    font: {{ size: 14 }}
                                }}
                            }},
                            scales: {{
                                x: {{ 
                                    grid: {{ color: 'rgba(255, 255, 255, 0.1)' }},
                                    ticks: {{ color: '#ffffff' }}
                                }},
                                y: {{ 
                                    grid: {{ color: 'rgba(255, 255, 255, 0.1)' }},
                                    ticks: {{ color: '#ffffff', precision: 0 }},
                                    beginAtZero: true
                                }}
                            }}
                        }}
                    }}
                );
                
                // Status Chart
                new Chart(
                    document.getElementById('{user_id}_statusChart').getContext('2d'), {{
                        type: 'doughnut',
                        data: {{
                            labels: {json.dumps(status_labels)},
                            datasets: [{{
                                label: 'Status Distribution',
                                data: {json.dumps(status_values)},
                                backgroundColor: [
                                    '#a4b0be', '#ffa502', '#3742fa', '#2ed573', 
                                    '#9b59b6', '#e67e22', '#7f8c8d'
                                ],
                                borderColor: 'rgba(255, 255, 255, 0.2)',
                                borderWidth: 1
                            }}]
                        }},
                        options: {{
                            responsive: true,
                            maintainAspectRatio: false,
                            plugins: {{
                                legend: {{ 
                                    position: 'right',
                                    labels: {{ color: '#ffffff' }}
                                }},
                                title: {{ 
                                    display: true, 
                                    text: 'Status Distribution',
                                    color: '#ffffff',
                                    font: {{ size: 14 }}
                                }}
                            }},
                            cutout: '65%'
                        }}
                    }}
                );
            </script>
        </div>
        """

    def _generate_html_template(self, project_name: str, html_sections: List[str]) -> str:
        """Generate the complete HTML template with all sections"""
        return f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Redmine Project Dashboard: {project_name}</title>
            <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
            <style>
                :root {{
                    --primary-color: #1e1e2d;
                    --secondary-color: #2d2d3d;
                    --accent-color: #ffffff;
                    --text-color: black;
                    --text-muted: rgba(255, 255, 255, 0.7);
                    --glass-bg: rgba(30, 30, 45, 0.7);
                    --glass-border: rgba(255, 255, 255, 0.1);
                    --glass-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.36);
                }}
                
                * {{
                    margin: 0;
                    padding: 0;
                    box-sizing: border-box;
                }}
                
                body {{
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    background: black;
                    color: var(--text-color);
                    min-height: 100vh;
                    padding: 20px;
                }}
                
                .header {{
                    text-align: center;
                    margin-bottom: 30px;
                    padding: 20px;
                    background: var(--glass-bg);
                    backdrop-filter: blur(10px);
                    -webkit-backdrop-filter: blur(10px);
                    border-radius: 15px;
                    border: 1px solid var(--glass-border);
                    box-shadow: var(--glass-shadow);
                }}
                
                .header h1 {{
                    font-size: 3rem;
                    margin-bottom: 15px;
                    background: linear-gradient(90deg, #c43b9d, #ffffff);
                    -webkit-background-clip: text;
                    background-clip: text;
                    color: transparent;
                }}
                
                .header p {{
                    color: white;
                    font-size: 1.5rem;
                    font-style: italic;
                }}
                
                .user-section {{
                    background: var(--glass-bg);
                    backdrop-filter: blur(10px);
                    -webkit-backdrop-filter: blur(10px);
                    border-radius: 15px;
                    border: 1px solid var(--glass-border);
                    box-shadow: var(--glass-shadow);
                    padding: 25px;
                    margin-bottom: 30px;
                }}
                
                .user-title {{
                    font-size: 1.5rem;
                    margin-bottom: 20px;
                    color: white;
                    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
                    padding-bottom: 10px;
                }}
                
                .chart-container {{
                    display: flex;
                    flex-wrap: wrap;
                    gap: 20px;
                    margin-bottom: 30px;
                }}
                
                .chart-box {{
                    flex: 1;
                    min-width: 300px;
                    height: 300px;
                    background: rgba(0, 0, 0, 0.2);
                    border-radius: 10px;
                    padding: 15px;
                }}
                
                .table-title {{
                    font-size: 1.2rem;
                    margin: 20px 0 15px 0;
                    color: var(--text-muted);
                }}
                
                .table-container {{
                    max-height: 500px;
                    overflow-y: auto;
                    border-radius: 10px;
                    background: rgba(0, 0, 0, 0.2);
                }}
                
                /* Custom scrollbar */
                .table-container::-webkit-scrollbar {{
                    width: 8px;
                    height: 8px;
                }}
                
                .table-container::-webkit-scrollbar-track {{
                    background: rgba(0, 0, 0, 0.1);
                    border-radius: 10px;
                }}
                
                .table-container::-webkit-scrollbar-thumb {{
                    background: #4e44ce;
                    border-radius: 10px;
                }}
                
                .table-container::-webkit-scrollbar-thumb:hover {{
                    background: #3a32a8;
                }}
                
                .issue-table {{
                    width: 100%;
                    border-collapse: collapse;
                    color: var(--text-color);
                    border: 1px solid black;
                    background: white;
                }}
                
                .issue-table th {{
                    background: black;
                    color: white;
                    padding: 12px;
                    text-align: left;
                    position: sticky;
                    top: 0;
                    backdrop-filter: blur(5px);
                    border: 1px solid white;
                }}
                
                .issue-table td {{
                    padding: 12px;
                    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
                    border: 1px solid black;
                }}
                
                @media (max-width: 768px) {{
                    .chart-container {{
                        flex-direction: column;
                    }}
                    
                    .chart-box {{
                        min-width: 100%;
                    }}
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Redmine Project Dashboard</h1>
                <p>Project: {project_name}</p>
            </div>
            {''.join(html_sections)}
        </body>
        </html>
        """

    def execute(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        try:
            project_name = arguments.get("project_name")
            if not project_name:
                return {"success": False, "error": "project_name is required"}
            
            headers = {
                "X-Redmine-API-Key": self.API_KEY,
                "Content-Type": "application/json"
            }
            
            # Get project ID
            project_id = self._get_project_id(project_name, headers, self.default_config["timeout"])
            if not project_id:
                return {"success": False, "error": f"Project '{project_name}' not found"}
            
            # Fetch all issues
            issues = self._fetch_all_issues(project_id, headers, self.default_config["timeout"])
            
            # Group issues by assignee
            users_issues = self._group_issues_by_assignee(issues)
            
            # Generate HTML sections for each user
            html_sections = []
            for user, user_issues in users_issues.items():
                html_sections.append(self._generate_user_section(user, user_issues))
            
            # Generate final HTML
            final_html = self._generate_html_template(project_name, html_sections)
            
            return {"success": True, "result": final_html}
            
        except Exception as e:
            frappe.log_error(title=_("Redmine Issue Reporter Tool Error"), message=str(e))
            return {"success": False, "error": str(e)}




# -------------------------
# Export tools for Frappe Assistant Core
# -------------------------
__all__ = [
        "RedmineIssueTool", 
        "RedmineDashboardTool",
    ]
