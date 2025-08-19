# Redmine Integration Tools

A complete Python toolkit for Redmine project management with API integration and visual reporting capabilities.

---

## 📌 Table of Contents
- [Features](#-features)
- [Installation](#-installation)
- [Tools Overview](#-tools-overview)
- [RedmineIssueTool](#1-redmineissuetool)
- [RedmineDashboardTool](#2-redminedashboardtool)
- [Usage Examples](#-usage-examples)
- [Configuration](#-configuration)
- [Troubleshooting](#-troubleshooting)
- [Contributing](#-contributing)

---

## ✨ Features
- Real-time Redmine API integration
- **CRUD operations on issues by Project ID, Project Name, or Ticket Title**
- Visual dashboards with interactive charts
- Multi-project support
- Priority/status tracking with color coding
- Automated reporting
- Documentation for both technical and functional workflows
- **Safe Mode:** Delete operation is disabled (contact tool developer)

---

## 🛠️ Installation
```bash
pip install requests python-dotenv
````

---

## 🔧 Tools Overview

### 1. redmineissuetool

Core API interface for Redmine operations.

**Available Actions:**

```python
actions = [
    "list_projects",
    "list_issues", 
    "get_issue",
    "create_issue",
    "update_issue",
    "delete_issue"  # ⚠️ Blocked — returns warning message
]
```

> **Note**:
>
> * You can perform actions based on **Project ID**, **Project Name**, or **Ticket Title**.
> * **Delete Operation**: Instead of deleting, the tool will respond:
>   *"For delete functionality contact with Sayeesh, who developed this tool."*

---

### 2. RedminedashboardTool

Visual reporting and dashboard generation.

**Color Coding Scheme:**

| Category | Values                 | Colors    |
| -------- | ---------------------- | --------- |
| Priority | High, Normal           | 🔴, 🟢    |
| Status   | New, In Progress, etc. | ⚪, 🟡, 🔵 |

**Example: Generate Dashboard**

```python
from redmine_tool import RedminedashboardTool
reporter = RedminedashboardTool()
dashboard = reporter.execute({
    "project_name": "NTPT Implementation",
    "filter": "priority=high"
})
```

---

## 🚀 Usage Examples

### Basic Operations

**Create a new issue (by project name):**

```python
tool.execute({
    "action": "create_issue",
    "project_name": "ERPNext",
    "subject": "Login page bug",
    "description": "Submit button not working"
})
```

**Update issue by title:**

```python
tool.execute({
    "action": "update_issue",
    "title": "Login page bug",
    "updates": {
        "status_id": 2,
        "notes": "Fixed in latest commit"
    }
})
```

**⚠️ Attempt delete issue:**

```python
tool.execute({
    "action": "delete_issue",
    "issue_id": 789
})
```
---

## ⚙️ Configuration

Create `.env` file in project root:

```ini
REDMINE_API_URL=https://redmine.example.com
REDMINE_API_KEY=<your_api_key_here>
TIMEOUT=30
```

* `REDMINE_API_URL`: Your Redmine server endpoint
* `REDMINE_API_KEY`: Personal API key from Redmine
* `TIMEOUT`: Request timeout in seconds (default: 30)

---

## 🐛 Troubleshooting

**Common Issues:**

1. **Authentication Errors**

   * Verify API key in `.env`
   * Check API key permissions

2. **Data Not Loading**

   * Confirm network connectivity
   * Validate project exists

3. **Delete Attempts**

   * Tool intentionally blocks delete operation
   * Message: *"For delete functionality contact with Sayeesh, who developed this tool."*

---

## 👨‍💻 Developer Contact

For enhancements, bug fixes, or **delete functionality requests**, please contact: \
**Sayeesh (Redmine Tool Developer)**\
**Email: sayeesh.naik@promantia.com**

```

---
