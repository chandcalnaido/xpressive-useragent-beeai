#!/usr/bin/env python3
"""
Simple verification test for BeeAI SDK Tool Registry
Tests imports and tool definitions without making external API calls
"""

import asyncio
import sys


def test_imports():
    """Verify all imports work correctly"""
    print("=" * 70)
    print("Step 1: Testing Imports")
    print("=" * 70)

    try:
        print("  ✓ Importing beeai_sdk_tools...")
        from beeai_sdk_tools import BeeAISDKToolRegistry, ToolResult
        print("  ✓ Importing beeai_manager...")
        from beeai_manager import BeeAIManager
        print("  ✓ Importing evi_tools...")
        from evi_tools import EVITools
        print("  ✓ Importing BeeAI framework components...")
        from beeai_framework.agents.requirement import RequirementAgent
        from beeai_framework.backend import ChatModel
        from beeai_framework.logger import Logger
        from beeai_framework.tools.think import ThinkTool
        from beeai_framework.tools.search.wikipedia import WikipediaTool
        from beeai_framework.tools.weather import OpenMeteoTool
        from beeai_framework.tools.handoff import HandoffTool

        print("\n✅ All imports successful!\n")
        return True

    except ImportError as e:
        print(f"\n❌ Import failed: {e}\n")
        return False


def test_tool_registry_initialization():
    """Test tool registry initialization"""
    print("=" * 70)
    print("Step 2: Testing Tool Registry Initialization")
    print("=" * 70)

    try:
        from beeai_sdk_tools import BeeAISDKToolRegistry

        print("  → Creating BeeAISDKToolRegistry instance...")
        registry = BeeAISDKToolRegistry(verbose=False)
        print("  ✓ Tool registry created successfully")

        print("  → Checking EVITools backend...")
        assert registry.evi_tools is not None, "EVITools not initialized"
        print("  ✓ EVITools backend initialized")

        print("  → Checking BeeAI manager state...")
        assert registry.beeai_manager is None, "BeeAI should be lazy-initialized"
        print("  ✓ BeeAI manager correctly set to lazy initialization")

        print("\n✅ Tool registry initialization successful!\n")
        return True, registry

    except Exception as e:
        print(f"\n❌ Tool registry initialization failed: {e}\n")
        import traceback
        traceback.print_exc()
        return False, None


def test_tool_definitions(registry):
    """Test tool definitions format"""
    print("=" * 70)
    print("Step 3: Testing Tool Definitions")
    print("=" * 70)

    try:
        tool_defs = registry.get_tool_definitions()

        print(f"  → Found {len(tool_defs)} tool definitions")

        expected_tools = [
            "get_weather",
            "get_time",
            "calculate",
            "consult_research_team",
            "analyze_topic",
            "compare_items",
            "confirm_action"
        ]

        print(f"  → Expecting {len(expected_tools)} tools")

        # Check all expected tools are present
        tool_names = [tool["name"] for tool in tool_defs]
        for expected in expected_tools:
            assert expected in tool_names, f"Missing tool: {expected}"
            print(f"    ✓ {expected}")

        # Validate tool definition format
        print("\n  → Validating tool definition format...")
        for tool in tool_defs:
            assert "name" in tool, f"Tool missing 'name': {tool}"
            assert "description" in tool, f"Tool {tool['name']} missing 'description'"
            assert "input_schema" in tool, f"Tool {tool['name']} missing 'input_schema'"

            schema = tool["input_schema"]
            assert schema["type"] == "object", f"Tool {tool['name']} schema must be object type"
            assert "properties" in schema, f"Tool {tool['name']} schema missing properties"

        print("  ✓ All tool definitions valid")

        print("\n  Tool Summary:")
        print("  " + "-" * 66)
        for tool in tool_defs:
            desc_preview = tool["description"][:55] + "..." if len(tool["description"]) > 55 else tool["description"]
            print(f"    {tool['name']:25} {desc_preview}")
        print("  " + "-" * 66)

        print("\n✅ Tool definitions test successful!\n")
        return True

    except Exception as e:
        print(f"\n❌ Tool definitions test failed: {e}\n")
        import traceback
        traceback.print_exc()
        return False


async def test_calculator_tool(registry):
    """Test calculator tool (no API calls required)"""
    print("=" * 70)
    print("Step 4: Testing Calculator Tool (No External APIs)")
    print("=" * 70)

    try:
        test_cases = [
            ("42 * 7", "294"),
            ("100 + 50", "150"),
            ("1000 / 8", "125.0"),
        ]

        for expression, expected in test_cases:
            print(f"  → Testing: {expression}")
            result = await registry.calculate({"expression": expression})

            assert not result.is_error, f"Calculator returned error for {expression}"
            assert len(result.content) > 0, "Result content is empty"
            assert "text" in result.content[0], "Result missing text field"

            result_text = result.content[0]["text"]
            assert expected in result_text, f"Expected {expected} in result, got: {result_text}"
            print(f"    ✓ Result: {result_text}")

        print("\n✅ Calculator tool test successful!\n")
        return True

    except Exception as e:
        print(f"\n❌ Calculator tool test failed: {e}\n")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Run all verification tests"""
    print("\n" + "=" * 70)
    print("BeeAI SDK Tool Registry - Simple Verification Test")
    print("=" * 70 + "\n")

    results = []

    # Test 1: Imports
    results.append(("Imports", test_imports()))

    if not results[-1][1]:
        print("\n❌ Cannot proceed - import failures detected")
        sys.exit(1)

    # Test 2: Initialization
    success, registry = test_tool_registry_initialization()
    results.append(("Initialization", success))

    if not success or registry is None:
        print("\n❌ Cannot proceed - initialization failed")
        sys.exit(1)

    # Test 3: Tool definitions
    results.append(("Tool Definitions", test_tool_definitions(registry)))

    # Test 4: Calculator (async)
    results.append(("Calculator Tool", await test_calculator_tool(registry)))

    # Summary
    print("=" * 70)
    print("Test Summary")
    print("=" * 70)

    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {test_name:30} {status}")

    all_passed = all(result[1] for result in results)

    print("=" * 70)
    if all_passed:
        print("✅ All tests passed! Tool registry is ready.")
    else:
        print("❌ Some tests failed. Review output above.")
    print("=" * 70 + "\n")

    return 0 if all_passed else 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
