def get_recycler_system_prompt():
    return """
    You are an expert Commodities & Recycling Market Analyst for the Motor Valley in Italy.
    Your goal is to analyze local market conditions and advise recycling companies on when to bid 
    on End-of-Life (EOL) vehicle materials.
    
    Format your response with these exact headers:
    **CURRENT MARKET TRENDS:**
    **MOTOR VALLEY LOGISTICS:**
    **RECOMMENDED ACTION:**
    """

def get_recycler_user_prompt(sector: str, quantity: float, platform_value: float, live_context: str):
    return f"""
    Analyze the following salvage pool data:
    - Material Sector: {sector}
    - Available Quantity: {quantity} tons
    - Estimated Platform Value: €{platform_value}
    
    Recent Market Intelligence:
    {live_context}
    """