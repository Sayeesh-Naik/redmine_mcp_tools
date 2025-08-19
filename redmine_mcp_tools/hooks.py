# Configs for Redmine MCP Tools App
app_name = "redmine_mcp_tools"  
app_title = "Redmine MCP Tools"  
app_version = "0.1.0" 
app_publisher = "Sayeesh Naik"
app_description = "Tools for Redmine MCP integration"
app_email = "sayeesh.naik@promantia.com"
app_license = "MIT"


# Register tools with Frappe Assistant Core
assistant_tools = [
	"redmine_mcp_tools.assistant_tools.mcp_custom_tools.RedmineIssueTool",
	"redmine_mcp_tools.assistant_tools.mcp_custom_tools.RedmineDashboardTool",
]
