class CostTracker:
    """Track API usage and costs across the session"""
    
    def __init__(self):
        self.total_tokens = 0
        self.total_cost = 0.0
        self.test_count = 0
    
    def add_test(self, tokens: int, cost: float):
        """Record a test run"""
        self.total_tokens += tokens
        self.total_cost += cost
        self.test_count += 1
    
    def get_total_tokens(self) -> int:
        return self.total_tokens
    
    def get_total_cost(self) -> float:
        return self.total_cost
    
    def get_test_count(self) -> int:
        return self.test_count
    
    def reset(self):
        """Reset all counters"""
        self.total_tokens = 0
        self.total_cost = 0.0
        self.test_count = 0