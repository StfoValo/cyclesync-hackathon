from mcp_agent_server.ai_orchestrator import AIOrchestrator

# Inside your class/method where you trigger the AI:
self.agent = AIOrchestrator()
# Change the call from self.agent.run_agentic_analysis(...) to:
stream = self.agent.run_recycler_analysis(sector, quantity, platform_value)