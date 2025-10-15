"""
BeeAI Agent SDK Tools Wrapper
Bridges EVITools and BeeAI with Claude Agent SDK tool interface
"""

import asyncio
import logging
import os
from typing import Dict, Any, List
from dataclasses import dataclass

# Import existing tools
from evi_tools import EVITools
from beeai_manager import BeeAIManager


@dataclass
class ToolResult:
    """Standardized tool result format for Claude SDK"""
    content: List[Dict[str, str]]
    is_error: bool = False


class BeeAISDKToolRegistry:
    """
    Registry for all tools available to Claude Agent SDK.
    Wraps existing EVI tools and BeeAI with Claude SDK tool interface.
    """

    def __init__(self, verbose: bool = False, claude_client=None):
        self.logger = logging.getLogger('pattern5.tools')
        self.logger.info("Initializing BeeAI SDK Tool Registry")

        # Initialize existing tool backends
        self.evi_tools = EVITools()

        # BeeAI manager will be initialized async
        self.beeai_manager = None
        self._beeai_init_task = None
        self.verbose = verbose

        self.logger.debug("Tool backends initialized successfully")

    async def _ensure_beeai_initialized(self):
        """Ensure BeeAI manager is initialized (lazy initialization)"""
        if self.beeai_manager is None:
            if self._beeai_init_task is None:
                self._beeai_init_task = asyncio.create_task(self._init_beeai())
            await self._beeai_init_task

    async def _init_beeai(self):
        """Initialize BeeAI manager asynchronously"""
        try:
            self.logger.info("Initializing BeeAI manager with Claude models")
            self.beeai_manager = BeeAIManager(
                model_name="anthropic:claude-3-5-sonnet-20241022",
                verbose=self.verbose
            )
            self.logger.info("BeeAI manager initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize BeeAI manager: {e}", exc_info=True)
            raise

    # ============================================================================
    # QUICK RESPONSE TOOLS (< 1 second)
    # ============================================================================

    async def get_weather(self, args: Dict[str, Any]) -> ToolResult:
        """
        Get weather information for a location.

        Args:
            args: {
                "location": str - City or location name
                "units": str - "fahrenheit" or "celsius" (optional, default: fahrenheit)
            }

        Returns:
            ToolResult with weather information
        """
        try:
            location = args.get("location", "New York")
            units = args.get("units", "fahrenheit")

            self.logger.info(f"Getting weather for {location} in {units}")

            result = self.evi_tools.get_weather(location, units)

            return ToolResult(
                content=[{"type": "text", "text": result}],
                is_error=False
            )
        except Exception as e:
            self.logger.error(f"Weather tool error: {e}", exc_info=True)
            return ToolResult(
                content=[{"type": "text", "text": f"Error getting weather: {str(e)}"}],
                is_error=True
            )

    async def get_time(self, args: Dict[str, Any]) -> ToolResult:
        """
        Get current time in a timezone.

        Args:
            args: {
                "timezone": str - Timezone name (optional, default: America/New_York)
            }

        Returns:
            ToolResult with current time
        """
        try:
            timezone = args.get("timezone", "America/New_York")

            self.logger.info(f"Getting time for timezone: {timezone}")

            result = self.evi_tools.get_time(timezone)

            return ToolResult(
                content=[{"type": "text", "text": result}],
                is_error=False
            )
        except Exception as e:
            self.logger.error(f"Time tool error: {e}", exc_info=True)
            return ToolResult(
                content=[{"type": "text", "text": f"Error getting time: {str(e)}"}],
                is_error=True
            )

    async def calculate(self, args: Dict[str, Any]) -> ToolResult:
        """
        Perform mathematical calculations.

        Args:
            args: {
                "expression": str - Mathematical expression to evaluate
            }

        Returns:
            ToolResult with calculation result
        """
        try:
            expression = args.get("expression", "")

            if not expression:
                return ToolResult(
                    content=[{"type": "text", "text": "No expression provided"}],
                    is_error=True
                )

            self.logger.info(f"Calculating: {expression}")

            result = self.evi_tools.calculate(expression)

            return ToolResult(
                content=[{"type": "text", "text": result}],
                is_error=False
            )
        except Exception as e:
            self.logger.error(f"Calculator tool error: {e}", exc_info=True)
            return ToolResult(
                content=[{"type": "text", "text": f"Error in calculation: {str(e)}"}],
                is_error=True
            )

    # ============================================================================
    # COMPLEX ANALYSIS TOOLS (BeeAI Backend)
    # ============================================================================

    async def consult_research_team(self, args: Dict[str, Any]) -> ToolResult:
        """
        Consult specialized research agents for complex queries.
        Uses BeeAI backend with researcher, analyst, and coordinator agents.
        All agents powered by Claude for emotional intelligence.

        Args:
            args: {
                "query": str - Complex query requiring research/analysis
                "context": str - Additional context (optional)
            }

        Returns:
            ToolResult with comprehensive analysis
        """
        try:
            await self._ensure_beeai_initialized()

            query = args.get("query", "")
            context = args.get("context")

            if not query:
                return ToolResult(
                    content=[{"type": "text", "text": "No query provided for research team"}],
                    is_error=True
                )

            self.logger.info(f"Consulting BeeAI research team for: {query}")

            # Run BeeAI (already async)
            result = await self.beeai_manager.process_complex_query(query, context)

            self.logger.info("BeeAI research team consultation completed")

            return ToolResult(
                content=[{"type": "text", "text": result}],
                is_error=False
            )
        except Exception as e:
            self.logger.error(f"Research team tool error: {e}", exc_info=True)
            return ToolResult(
                content=[{"type": "text", "text": f"Error consulting research team: {str(e)}"}],
                is_error=True
            )

    async def analyze_topic(self, args: Dict[str, Any]) -> ToolResult:
        """
        Perform specialized analysis on a topic using BeeAI agents.

        Args:
            args: {
                "topic": str - Topic to analyze
                "analysis_type": str - "comprehensive", "comparative", or "pros-cons" (optional)
            }

        Returns:
            ToolResult with detailed analysis
        """
        try:
            await self._ensure_beeai_initialized()

            topic = args.get("topic", "")
            analysis_type = args.get("analysis_type", "comprehensive")

            if not topic:
                return ToolResult(
                    content=[{"type": "text", "text": "No topic provided for analysis"}],
                    is_error=True
                )

            self.logger.info(f"Analyzing topic: {topic} (type: {analysis_type})")

            result = await self.beeai_manager.process_analysis_task(topic, analysis_type)

            self.logger.info("Topic analysis completed")

            return ToolResult(
                content=[{"type": "text", "text": result}],
                is_error=False
            )
        except Exception as e:
            self.logger.error(f"Analysis tool error: {e}", exc_info=True)
            return ToolResult(
                content=[{"type": "text", "text": f"Error in analysis: {str(e)}"}],
                is_error=True
            )

    async def compare_items(self, args: Dict[str, Any]) -> ToolResult:
        """
        Compare two items using specialized BeeAI analysis agents.

        Args:
            args: {
                "item1": str - First item to compare
                "item2": str - Second item to compare
                "criteria": str - Specific comparison criteria (optional)
            }

        Returns:
            ToolResult with comparison analysis
        """
        try:
            await self._ensure_beeai_initialized()

            item1 = args.get("item1", "")
            item2 = args.get("item2", "")
            criteria = args.get("criteria")

            if not item1 or not item2:
                return ToolResult(
                    content=[{"type": "text", "text": "Need both items to compare"}],
                    is_error=True
                )

            self.logger.info(f"Comparing: {item1} vs {item2}")

            result = await self.beeai_manager.process_comparison_task(item1, item2, criteria)

            self.logger.info("Comparison completed")

            return ToolResult(
                content=[{"type": "text", "text": result}],
                is_error=False
            )
        except Exception as e:
            self.logger.error(f"Comparison tool error: {e}", exc_info=True)
            return ToolResult(
                content=[{"type": "text", "text": f"Error in comparison: {str(e)}"}],
                is_error=True
            )

    # ============================================================================
    # UTILITY TOOLS
    # ============================================================================

    async def confirm_action(self, args: Dict[str, Any]) -> ToolResult:
        """
        Request confirmation for an action from the user.

        Args:
            args: {
                "action": str - Action to confirm
                "details": str - Additional details (optional)
            }

        Returns:
            ToolResult with confirmation request
        """
        try:
            action = args.get("action", "")
            details = args.get("details", "")

            self.logger.info(f"Requesting confirmation for: {action}")

            result = self.evi_tools.confirm_action(action, details)

            return ToolResult(
                content=[{"type": "text", "text": result}],
                is_error=False
            )
        except Exception as e:
            self.logger.error(f"Confirmation tool error: {e}", exc_info=True)
            return ToolResult(
                content=[{"type": "text", "text": f"Error requesting confirmation: {str(e)}"}],
                is_error=True
            )

    # ============================================================================
    # TOOL DEFINITIONS FOR CLAUDE SDK
    # ============================================================================

    def get_tool_definitions(self) -> List[Dict[str, Any]]:
        """
        Get tool definitions in Claude SDK format.

        Returns:
            List of tool definition dictionaries
        """
        return [
            {
                "name": "get_weather",
                "description": "Get current weather information for any location. Use this when user asks about weather, temperature, or forecast.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "location": {
                            "type": "string",
                            "description": "City or location name (e.g., 'New York', 'London', 'Tokyo')"
                        },
                        "units": {
                            "type": "string",
                            "enum": ["fahrenheit", "celsius"],
                            "description": "Temperature units (default: fahrenheit)"
                        }
                    },
                    "required": ["location"]
                }
            },
            {
                "name": "get_time",
                "description": "Get current time in any timezone. Use when user asks about time or clock.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "timezone": {
                            "type": "string",
                            "description": "Timezone name (e.g., 'America/New_York', 'Europe/London', 'Asia/Tokyo'). Default: America/New_York"
                        }
                    },
                    "required": []
                }
            },
            {
                "name": "calculate",
                "description": "Perform mathematical calculations. Supports basic arithmetic (+, -, *, /).",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "expression": {
                            "type": "string",
                            "description": "Mathematical expression to evaluate (e.g., '15 * 23', '100 + 50')"
                        }
                    },
                    "required": ["expression"]
                }
            },
            {
                "name": "consult_research_team",
                "description": "Consult specialized AI research team powered by BeeAI and Claude for complex queries requiring in-depth research, analysis, or multi-step reasoning. Use for questions about trends, industry analysis, detailed explanations, or comparative studies. All agents use Claude for emotional intelligence.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "The complex query or question to research"
                        },
                        "context": {
                            "type": "string",
                            "description": "Additional context or constraints for the research (optional)"
                        }
                    },
                    "required": ["query"]
                }
            },
            {
                "name": "analyze_topic",
                "description": "Perform specialized analysis on a specific topic using BeeAI agents. Use for deep dives, technical explanations, or comprehensive reviews.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "topic": {
                            "type": "string",
                            "description": "Topic to analyze"
                        },
                        "analysis_type": {
                            "type": "string",
                            "enum": ["comprehensive", "comparative", "pros-cons"],
                            "description": "Type of analysis to perform (default: comprehensive)"
                        }
                    },
                    "required": ["topic"]
                }
            },
            {
                "name": "compare_items",
                "description": "Compare two items, technologies, approaches, or concepts using BeeAI analysis agents. Use when user asks to compare or evaluate differences.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "item1": {
                            "type": "string",
                            "description": "First item to compare"
                        },
                        "item2": {
                            "type": "string",
                            "description": "Second item to compare"
                        },
                        "criteria": {
                            "type": "string",
                            "description": "Specific criteria for comparison (optional)"
                        }
                    },
                    "required": ["item1", "item2"]
                }
            },
            {
                "name": "confirm_action",
                "description": "Request user confirmation before performing an action. Use when an action requires explicit user approval.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "action": {
                            "type": "string",
                            "description": "Action that requires confirmation"
                        },
                        "details": {
                            "type": "string",
                            "description": "Additional details about the action (optional)"
                        }
                    },
                    "required": ["action"]
                }
            }
        ]

    async def execute_tool(self, tool_name: str, args: Dict[str, Any]) -> ToolResult:
        """
        Execute a tool by name.

        Args:
            tool_name: Name of the tool to execute
            args: Tool arguments

        Returns:
            ToolResult from the executed tool
        """
        self.logger.debug(f"Executing tool: {tool_name} with args: {args}")

        # Map tool names to methods
        tool_methods = {
            "get_weather": self.get_weather,
            "get_time": self.get_time,
            "calculate": self.calculate,
            "consult_research_team": self.consult_research_team,
            "analyze_topic": self.analyze_topic,
            "compare_items": self.compare_items,
            "confirm_action": self.confirm_action
        }

        tool_method = tool_methods.get(tool_name)

        if not tool_method:
            self.logger.warning(f"Unknown tool requested: {tool_name}")
            return ToolResult(
                content=[{"type": "text", "text": f"Unknown tool: {tool_name}"}],
                is_error=True
            )

        return await tool_method(args)


# Convenience function for testing
async def test_tools():
    """Test tool registry"""
    registry = BeeAISDKToolRegistry(verbose=True)

    print("=== Testing BeeAI SDK Tool Registry ===\n")

    # Test weather tool
    print("1. Testing weather tool...")
    result = await registry.get_weather({"location": "San Francisco"})
    print(f"   Result: {result.content[0]['text']}\n")

    # Test time tool
    print("2. Testing time tool...")
    result = await registry.get_time({"timezone": "America/Los_Angeles"})
    print(f"   Result: {result.content[0]['text']}\n")

    # Test calculator
    print("3. Testing calculator...")
    result = await registry.calculate({"expression": "42 * 7"})
    print(f"   Result: {result.content[0]['text']}\n")

    print("=== Tool Definitions ===")
    for tool_def in registry.get_tool_definitions():
        print(f"  - {tool_def['name']}: {tool_def['description']}")


if __name__ == "__main__":
    import asyncio
    asyncio.run(test_tools())
