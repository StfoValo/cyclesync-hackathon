# MCP Agent Server

This directory acts as the intelligent agentic backend for the CycleSync Recycler Hub, providing live, strategic analysis of material salvage valuations based on real-world data.

## Components

*   **`market_agent.py`**: Contains the `MotorValleyAgent`, an agent powered by Google's Gemini LLM. It queries the local `MarketCacheManager` (populated by the ETL pipeline) to inject live real-world context into its prompt and streams the synthesized market analysis back to the caller.
*   **`agent_tools.py`**: Contains external tools and capabilities available to the agent, such as `search_live_market_data` which utilizes DuckDuckGo to search the internet for current recycling market data, acting as an active tool during the agentic reasoning process.
