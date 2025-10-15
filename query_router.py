"""
Intelligent Query Router
Analyzes user queries and determines optimal handling strategy
"""

import re
import logging
from typing import Dict, Literal
from dataclasses import dataclass
from enum import Enum

class QueryComplexity(Enum):
    """Query complexity levels"""
    SIMPLE = "simple"           # Quick tool can handle
    MODERATE = "moderate"       # Might need light reasoning
    COMPLEX = "complex"         # Needs CrewAI

class RouteDecision(Enum):
    """Routing decisions"""
    QUICK_TOOL = "quick_tool"      # Use EVI's quick tools
    CREW_AI = "crew_ai"            # Route to CrewAI
    CLARIFICATION = "clarification" # Need more info from user

@dataclass
class RoutingResult:
    """Result of routing analysis"""
    decision: RouteDecision
    complexity: QueryComplexity
    confidence: float  # 0.0 to 1.0
    suggested_tool: str = None
    reasoning: str = ""

class QueryRouter:
    """
    Analyzes queries and routes them to appropriate handlers.

    This is implemented as patterns + heuristics for the POC.
    In production, you could use a small classifier model.
    """

    def __init__(self):
        self.logger = logging.getLogger('pattern3.routing')
        self.logger.debug("Initializing QueryRouter")

        # Define patterns for quick tools
        self.quick_patterns = {
            'weather': [
                r'weather in',
                r'temperature in',
                r'how.*hot|cold',
                r'forecast for',
                r'rain.*today'
            ],
            'time': [
                r'what time',
                r'current time',
                r'time in',
                r'what.*clock say'
            ],
            'calculator': [
                r'\d+\s*[\+\-\*\/]\s*\d+',
                r'calculate',
                r'what is \d+',
                r'how much is \d+'
            ]
        }
        
        # Indicators of complexity requiring CrewAI
        self.complexity_indicators = {
            'multi_step': [
                r'analyze.*and.*compare',
                r'research.*and.*summarize',
                r'find.*then.*tell',
                r'first.*then.*finally'
            ],
            'requires_research': [
                r'latest',
                r'recent developments',
                r'current trends',
                r'what are people saying',
                r'industry'
            ],
            'requires_analysis': [
                r'why',
                r'analyze',
                r'compare',
                r'evaluate',
                r'pros and cons',
                r'differences between',
                r'which is better'
            ],
            'requires_expertise': [
                r'explain.*in detail',
                r'comprehensive',
                r'deep dive',
                r'technical',
                r'professional advice'
            ]
        }
        
    def analyze_query(self, query: str) -> RoutingResult:
        """
        Analyze a user query and determine routing.

        Args:
            query: User's text query

        Returns:
            RoutingResult with routing decision
        """
        self.logger.debug(f"Analyzing query: {query}")
        query_lower = query.lower().strip()

        # Check for quick tool patterns first
        quick_tool = self._check_quick_tools(query_lower)
        if quick_tool:
            self.logger.info(f"Quick tool match: {quick_tool}")
            return RoutingResult(
                decision=RouteDecision.QUICK_TOOL,
                complexity=QueryComplexity.SIMPLE,
                confidence=0.9,
                suggested_tool=quick_tool,
                reasoning=f"Simple {quick_tool} query detected"
            )

        # Check complexity indicators
        complexity_score = self._calculate_complexity(query_lower)
        self.logger.debug(f"Complexity score: {complexity_score}")

        if complexity_score >= 3:
            # High complexity - needs CrewAI
            self.logger.info(f"High complexity query (score: {complexity_score}), routing to CrewAI")
            return RoutingResult(
                decision=RouteDecision.CREW_AI,
                complexity=QueryComplexity.COMPLEX,
                confidence=0.85,
                reasoning=f"Complex query requiring specialized agents (score: {complexity_score})"
            )
        elif complexity_score >= 2:
            # Moderate complexity - probably needs CrewAI
            self.logger.info(f"Moderate complexity query (score: {complexity_score}), routing to CrewAI")
            return RoutingResult(
                decision=RouteDecision.CREW_AI,
                complexity=QueryComplexity.MODERATE,
                confidence=0.7,
                reasoning=f"Moderate complexity, likely needs research/analysis (score: {complexity_score})"
            )
        else:
            # Low complexity but no quick tool match
            # Let EVI's LLM handle with general knowledge
            self.logger.info("Low complexity query, using EVI base LLM")
            return RoutingResult(
                decision=RouteDecision.QUICK_TOOL,
                complexity=QueryComplexity.SIMPLE,
                confidence=0.6,
                suggested_tool="general_response",
                reasoning="Simple query, EVI can handle with base knowledge"
            )
    
    def _check_quick_tools(self, query: str) -> str:
        """Check if query matches any quick tool patterns"""
        for tool_name, patterns in self.quick_patterns.items():
            for pattern in patterns:
                if re.search(pattern, query):
                    return tool_name
        return None
    
    def _calculate_complexity(self, query: str) -> int:
        """
        Calculate complexity score based on indicators.
        
        Returns:
            Score from 0-5+ (higher = more complex)
        """
        score = 0
        
        for category, patterns in self.complexity_indicators.items():
            for pattern in patterns:
                if re.search(pattern, query):
                    score += 1
                    break  # Only count each category once
        
        # Additional heuristics
        word_count = len(query.split())
        if word_count > 20:
            score += 1  # Long queries often need more processing
        
        question_marks = query.count('?')
        if question_marks > 1:
            score += 1  # Multiple questions = more complex
        
        # Check for conjunctions indicating multi-part requests
        if re.search(r'\band\b.*\band\b', query):
            score += 1
        
        return score
    
    def explain_decision(self, result: RoutingResult) -> str:
        """
        Generate human-readable explanation of routing decision.
        For debugging and transparency.
        """
        explanation = f"""
        Query Routing Analysis:
        ----------------------
        Decision: {result.decision.value.upper()}
        Complexity: {result.complexity.value}
        Confidence: {result.confidence:.0%}
        
        Reasoning: {result.reasoning}
        """
        
        if result.suggested_tool:
            explanation += f"\nSuggested Tool: {result.suggested_tool}"
        
        return explanation


# Convenience function for quick routing
def route_query(query: str) -> RoutingResult:
    """Quick function to route a query"""
    router = QueryRouter()
    return router.analyze_query(query)


if __name__ == "__main__":
    # Test the router
    test_queries = [
        "What's the weather in New York?",
        "What time is it?",
        "Calculate 15 times 23",
        "Analyze the latest trends in AI and compare them to last year",
        "Why do companies use microservices?",
        "Hello, how are you?",
        "Research competitor pricing and recommend a strategy"
    ]
    
    router = QueryRouter()
    
    print("=== Query Router Tests ===\n")
    for query in test_queries:
        result = router.analyze_query(query)
        print(f"Query: {query}")
        print(f"  → Decision: {result.decision.value}")
        print(f"  → Tool: {result.suggested_tool or 'N/A'}")
        print(f"  → Confidence: {result.confidence:.0%}")
        print(f"  → Reasoning: {result.reasoning}\n")
