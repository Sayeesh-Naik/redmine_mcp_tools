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
	# "redmine_mcp_tools.assistant_tools.mcp_custom_tools.SimpleGreetingTool",
	"redmine_mcp_tools.assistant_tools.mcp_custom_tools.RedmineTool",
	"redmine_mcp_tools.assistant_tools.mcp_custom_tools.RedmineIssueReporterTool",
	# Add more tools here as you create them
]

# Optional: Tool-specific configuration overrides
assistant_tool_configs = {
	"simple_greeting": {
		"greeting_style": "friendly",  
		"include_time": True,
		"max_name_length": 100,  
		"default_language": "en"
	},
    "redmine": {
		"api_url": "https://redmine.promantia.in",
		"api_key": "817ac36e7e9315d404965b34df7175a7344e506f",
		"user_email": "sayeesh.naik@promantia.com",
		"user_name": "Sayeesh Naik",
		"default_include_closed": False,
		"default_limit": 100,
		"request_timeout": 30,
		"connect_timeout": 10,
		"debug": True
	},
	"redmine_issue_reporter": {
		"api_url": "https://redmine.promantia.in",
		"api_key": "817ac36e7e9315d404965b34df7175a7344e506f",
		"user_email": "sayeesh.naik@promantia.com",
		"user_name": "Sayeesh Naik",
		"default_include_closed": False,
		"default_limit": 100,
		"request_timeout": 30,
		"connect_timeout": 10,
		"debug": True
	}
}