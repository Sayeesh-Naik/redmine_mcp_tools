````markdown
# Redmine Integration Tools

![Dashboard Preview](assets/dashboard-screenshot.png)

A Python toolkit for **Redmine project management** with API integration, dashboards, and reporting.

---

## 📌 Table of Contents
- [Features](#features)
- [Installation](#installation)
- [Tools](#tools)
- [RedmineIssueTool](#redminetool)
- [RedmineDashboardTool](#redmineissuereportertool)
- [Usage Examples](#usage-examples)
- [Configuration](#configuration)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)

---

## ✨ Features
- 🔗 Real-time Redmine API integration  
- 📊 Interactive dashboards with charts & tables  
- 🗂️ Multi-project support  
- 🎯 Priority & status tracking with color coding  
- 📑 Automated reporting (HTML / Docs)  
- 📖 Technical & functional documentation for Redmine tickets  

---

## 🛠 Installation
```bash
pip install requests python-dotenv
````

---

## 🔧 Tools

### 1. RedmineIssueTool

Low-level API interface for Redmine operations.

**Available Actions:**

```python
actions = [
    "list_projects",
    "list_issues",
    "get_issue",
    "create_issue",
    "update_issue"
]
```

**Example – List Projects**

```python
from redmine_tool import RedmineTool

tool = RedmineTool()
projects = tool.execute({"action": "list_projects"})
```

---

### 2. RedmineDashboardTool

Generates visual dashboards and reports.

**Color Coding Scheme:**

| Category | Values                | Colors   |
| -------- | --------------------- | ---------|
| Priority | High, Normal          | 🔴 🟢    |
| Status   | New, In Progress, etc | ⚪ 🟡 🔵 |

**Example – Generate Dashboard**

```python
from redmine_tool import RedmineIssueReporterTool

reporter = RedmineIssueReporterTool()
dashboard_html = reporter.execute({
    "project_name": "NTPT Implementation",
    "filter": "priority=high"
})
```

---

## 🚀 Usage Examples

### Create a New Issue

```python
tool.execute({
    "action": "create_issue",
    "project_id": 123,
    "subject": "Login page bug",
    "description": "Submit button not working"
})
```

### Update Issue Status

```python
tool.execute({
    "action": "update_issue",
    "issue_id": 456,
    "updates": {
        "status_id": 2,
        "notes": "Fixed in latest commit"
    }
})
```

### Generate Project Dashboard

```
LLM Example Prompt: Generate redmine dashboard for project name "<your_redmine_project_name>"

```

---

## ⚙️ Configuration

Create a `.env` file in your project root:

```ini
REDMINE_API_URL=https://redmine.example.com
REDMINE_API_KEY=your_api_key_here
TIMEOUT=30
```

---

## 🐛 Troubleshooting

**1. Authentication Errors**

* Ensure correct API key in `.env`
* Verify permissions in Redmine

**2. Data Not Loading**

* Check network connectivity
* Confirm project ID exists

---

## 🤝 Contributing

* ✅ Add unit tests for new features
* 📖 Update documentation where needed
* 📝 Use type hints for all methods
