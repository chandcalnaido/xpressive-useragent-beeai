"""
BeeAI Backend Manager
Handles complex queries using specialized agents with BeeAI framework
All agents powered by Claude for maximum emotional intelligence
"""

import asyncio
import logging
import time
from typing import Dict, Any, Optional
from beeai_framework.agents.requirement import RequirementAgent
from beeai_framework.backend import ChatModel
from beeai_framework.tools import ThinkTool, WikipediaTool, OpenMeteoTool, HandoffTool


class BeeAIManager:
    """
    Manages BeeAI agents for complex query processing.
    This is the backend intelligence layer using BeeAI framework.

    All agents use Claude (claude-3-5-sonnet-20241022) for emotional intelligence.
    """

    def __init__(self, model_name: str = "anthropic:claude-3-5-sonnet-20241022", verbose: bool = False):
        """
        Initialize BeeAI Manager with specialized agents.

        Args:
            model_name: LLM model to use (default: anthropic:claude-3-5-sonnet-20241022)
                       Other options: "anthropic:claude-3-opus-20240229", "openai:gpt-4"
            verbose: Enable verbose logging
        """
        self.verbose = verbose
        self.model_name = model_name
        self.logger = logging.getLogger('pattern5.beeai')
        self.logger.info(f"Initializing BeeAI Manager (model={model_name}, verbose={verbose})")

        # Initialize LLM backend
        try:
            self.llm = ChatModel.from_name(model_name)
            self.logger.debug(f"LLM backend initialized: {model_name}")
        except Exception as e:
            self.logger.error(f"Failed to initialize LLM {model_name}: {e}")
            raise

        self._initialize_agents()

    def _initialize_agents(self):
        """Initialize specialized BeeAI agents"""

        self.logger.debug("Initializing BeeAI specialized agents")

        # Researcher Agent - Gathers information from web and knowledge bases
        self.researcher = RequirementAgent(
            name="ResearchSpecialist",
            llm=self.llm,
            tools=[ThinkTool(), WikipediaTool()],
            role="Senior Research Specialist",
            instructions="""You are an expert researcher with access to Wikipedia and reasoning tools.
            Your goal is to gather comprehensive, accurate information from multiple sources.
            You excel at finding relevant information quickly and synthesizing it into clear summaries.

            Always cite your sources and verify information accuracy.

            When researching:
            1. Use Wikipedia for established facts and background
            2. Break down complex topics into key points
            3. Provide context and explanations suitable for voice delivery
            4. Note any uncertainties or conflicting information
            5. Be concise but thorough - your response will be spoken aloud

            Keep your language natural and conversational while being informative."""
        )

        # Weather Specialist Agent - Handles weather queries
        self.weather_specialist = RequirementAgent(
            name="WeatherSpecialist",
            llm=self.llm,
            tools=[OpenMeteoTool()],
            role="Weather Specialist",
            instructions="""You are a weather specialist providing accurate weather forecasts.
            Use the OpenMeteo tool to get current weather and forecasts.

            Provide weather information in a natural, conversational way suitable for voice delivery.
            Include temperature, conditions, and any relevant warnings or recommendations.

            Keep responses concise and helpful - people want quick, actionable weather info."""
        )

        # Analyst Agent - Processes and analyzes information
        self.analyst = RequirementAgent(
            name="StrategicAnalyst",
            llm=self.llm,
            tools=[ThinkTool()],
            role="Strategic Analyst",
            instructions="""You are a strategic analyst who excels at breaking down complex information,
            identifying patterns, and providing actionable insights.
            You consider multiple perspectives and provide balanced analysis.

            When analyzing:
            1. Identify key themes and patterns
            2. Compare and contrast different aspects
            3. Evaluate strengths and weaknesses objectively
            4. Provide clear, actionable recommendations
            5. Format responses for voice delivery (concise but complete)

            Your analysis will be spoken aloud, so keep language natural and avoid jargon
            unless necessary. When technical terms are needed, briefly explain them."""
        )

        # Coordinator Agent - Main agent that orchestrates other specialists
        self.coordinator = RequirementAgent(
            name="ResponseCoordinator",
            llm=self.llm,
            tools=[
                ThinkTool(),
                HandoffTool(self.researcher, name="ResearchLookup",
                           description="Consult the research specialist for factual information and comprehensive research"),
                HandoffTool(self.weather_specialist, name="WeatherLookup",
                           description="Consult the weather specialist for weather forecasts and conditions"),
                HandoffTool(self.analyst, name="AnalysisConsult",
                           description="Consult the strategic analyst for detailed analysis and insights")
            ],
            role="Response Coordinator",
            instructions="""You are a skilled coordinator who synthesizes information from specialist teams
            to create coherent, user-friendly responses for a voice interface.

            Your responsibilities:
            1. Understand the user's query and determine which specialists to consult
            2. Delegate to appropriate specialists using handoff tools when needed
            3. Synthesize their responses into a complete, coherent answer
            4. Ensure responses are accurate, complete, and appropriately detailed for voice delivery
            5. Make the response conversational and natural

            When to use specialists:
            - ResearchLookup: For factual information, background on topics, historical context
            - WeatherLookup: For weather forecasts and conditions
            - AnalysisConsult: For comparisons, evaluations, strategic insights, pros/cons

            Important guidelines:
            - Your response will be spoken by a voice AI, so be conversational
            - Keep responses concise (30-60 seconds of speech typically)
            - Use natural language and avoid overly formal phrasing
            - Break complex information into digestible points
            - Be empathetic and helpful in tone"""
        )

        self.logger.debug("BeeAI agents initialized successfully")

    async def process_complex_query(self, query: str, context: Optional[str] = None) -> str:
        """
        Process a complex query through the BeeAI agent system.

        Args:
            query: The complex query to process
            context: Optional additional context

        Returns:
            Processed response from the agent system
        """
        start_time = time.time()

        self.logger.info(f"Processing complex query: {query}")
        if context:
            self.logger.debug(f"Additional context: {context}")

        print(f"\n{'='*60}")
        print(f"🐝 BeeAI Processing: {query}")
        print(f"{'='*60}\n")

        try:
            # Prepare the full query with context
            full_query = query
            if context:
                full_query = f"{query}\n\nAdditional context: {context}"

            # Run the coordinator agent
            self.logger.debug("Starting BeeAI coordinator agent")
            result = await self.coordinator.run(full_query)

            # Extract the response text
            if hasattr(result, 'content'):
                response_text = result.content
            elif hasattr(result, 'text'):
                response_text = result.text
            elif isinstance(result, str):
                response_text = result
            else:
                response_text = str(result)

            elapsed = time.time() - start_time
            print(f"\n⏱️  BeeAI processing completed in {elapsed:.2f}s\n")
            self.logger.info(f"BeeAI processing completed in {elapsed:.2f}s")

            return response_text

        except Exception as e:
            self.logger.error(f"BeeAI processing error: {e}", exc_info=True)
            print(f"❌ BeeAI error: {e}")
            return ("I encountered an issue processing that complex query. "
                   "Could you try rephrasing it or breaking it into smaller questions?")

    async def process_analysis_task(self, topic: str, analysis_type: str = "comprehensive") -> str:
        """
        Specialized method for analysis tasks.

        Args:
            topic: Topic to analyze
            analysis_type: Type of analysis (comprehensive, comparative, pros-cons)

        Returns:
            Analysis results
        """
        self.logger.info(f"Processing {analysis_type} analysis of: {topic}")

        query = f"""Perform a {analysis_type} analysis of: {topic}

Please provide:
- Key findings
- Important trends or patterns
- Insights and implications
- Actionable recommendations if applicable

Format for voice delivery - conversational and clear."""

        return await self.process_complex_query(query)

    async def process_comparison_task(self, item1: str, item2: str, criteria: Optional[str] = None) -> str:
        """
        Specialized method for comparison tasks.

        Args:
            item1: First item to compare
            item2: Second item to compare
            criteria: Optional specific criteria to compare

        Returns:
            Comparison results
        """
        self.logger.info(f"Processing comparison: {item1} vs {item2}")

        criteria_text = f" focusing on {criteria}" if criteria else ""

        query = f"""Compare {item1} and {item2}{criteria_text}.

Provide:
- Key similarities
- Important differences
- Strengths and weaknesses of each
- Recommendation or conclusion if appropriate

Be objective and balanced. Format for voice delivery."""

        return await self.process_complex_query(query)


async def main():
    """Test the BeeAI manager"""
    import os
    from dotenv import load_dotenv

    load_dotenv()

    # Check for API key
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("❌ ANTHROPIC_API_KEY not found in environment")
        print("   Please set it in your .env file")
        return

    print("=== Testing BeeAI Backend ===\n")

    # Initialize manager with Claude
    manager = BeeAIManager(
        model_name="anthropic:claude-3-5-sonnet-20241022",
        verbose=True
    )

    # Test complex query
    test_query = "What are the latest trends in voice AI technology?"
    response = await manager.process_complex_query(test_query)

    print(f"\n{'='*60}")
    print("Final Response:")
    print(f"{'='*60}")
    print(response)


if __name__ == "__main__":
    asyncio.run(main())
