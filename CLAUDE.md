# CLAUDE.md - Best Practices for xpressive-useragent-beeai

## Project Overview

This project implements **Pattern 5**: An intelligent EVI (Empathic Voice Interface) with triple-layer emotional intelligence powered by Claude Agent SDK and BeeAI Framework.

### Key Components

- `evi_interface_pattern5.py` - Main Pattern 5 implementation with Claude orchestration
- `beeai_sdk_tools.py` - Exposes BeeAI agents as Claude SDK tools
- `beeai_manager.py` - BeeAI multi-agent backend (Claude-powered)
- `evi_tools.py` - Quick response tools (weather, time, calculator)
- `query_router.py` - Not used (Claude handles routing)

## Architecture

```
User Speech → EVI (Emotion Detection)
                ↓
         Claude SDK Orchestrator
         (Intelligent Routing)
                ↓
    ┌───────────┴───────────┐
    ↓                       ↓
Quick Tools          BeeAI Agents
(weather, time)      (Claude-powered)
    ↓                       ↓
    │  Researcher Agent     │
    │  Analyst Agent        │
    │  Coordinator Agent    │
    └───────────┬───────────┘
                ↓
         Claude Synthesis
                ↓
    EVI Speech (Empathic)
```

## Triple-Layer Emotional Intelligence

### Layer 1: Hume EVI
- Voice transcription with emotion detection
- Prosody analysis (tone, pace, emphasis)
- Empathic speech synthesis
- Emotional context awareness

### Layer 2: Claude Orchestrator
- Intelligent tool selection based on query intent
- Multi-step reasoning and planning
- Context-aware conversation management
- Emotional tone matching

### Layer 3: BeeAI Agents (Claude-powered)
- Research specialist with nuanced understanding
- Strategic analyst with balanced perspectives
- Coordinator with sophisticated handoff logic
- All using `claude-3-5-sonnet-20241022`

## Critical Configuration

### Environment Variables

```bash
# Required
HUME_API_KEY=your_hume_api_key
HUME_CONFIG_ID=your_hume_config_id
ANTHROPIC_API_KEY=your_anthropic_api_key

# Optional
OPENWEATHER_API_KEY=your_openweather_api_key
```

### Audio Device Setup

**Problem**: Bluetooth headsets often present as TWO separate devices:
- Device N: Microphone only (`max_input_channels: 1, max_output_channels: 0`)
- Device N+1: Speakers only (`max_input_channels: 0, max_output_channels: 2`)

**Solution**: Use MacBook built-in devices for development:
- Input: MacBook Pro Microphone
- Output: MacBook Pro Speakers

Configure in System Settings → Sound

Check devices:
```python
import sounddevice as sd
print(sd.query_devices())
print(f'Input: device {sd.default.device[0]}')
print(f'Output: device {sd.default.device[1]}')
```

## Installation & Setup

### Prerequisites

```bash
# macOS system dependencies
brew install portaudio  # For audio I/O

# Python 3.10+ required
python --version  # Should be 3.10 or higher
```

### Python Environment

```bash
# Create virtual environment
python3 -m venv venv_beeai

# Activate
source venv_beeai/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit .env and add your API keys
# HUME_API_KEY, HUME_CONFIG_ID, ANTHROPIC_API_KEY
```

## Running the System

### Development Mode

```bash
python evi_interface_pattern5.py
```

### With Debug Logging

```python
# In Python REPL or script
from evi_interface_pattern5 import main
import asyncio

asyncio.run(main(debug_mode=True))
```

### Expected Flow

1. System starts, connects to EVI
2. Claude SDK and BeeAI managers initialize
3. User speaks → EVI transcribes with emotion
4. Claude analyzes and selects appropriate tool
5. Quick tool OR BeeAI agents process query
6. Claude synthesizes final response
7. EVI speaks with empathic delivery

## Key Differences from Other Patterns

### Pattern 3 vs Pattern 5

| Feature | Pattern 3 | Pattern 5 |
|---------|-----------|-----------|
| **Routing** | Regex heuristics | Claude SDK decision |
| **Router Module** | `query_router.py` | Built into Claude |
| **Backend** | CrewAI (sync) | BeeAI (async) |
| **Orchestration** | If/else logic | Agentic loop |
| **Backend LLM** | Various | Claude only |
| **Tool Execution** | `asyncio.to_thread` | Native async |
| **Emotional Intelligence** | EVI only | Triple-layer |

### Pattern 4 vs Pattern 5

| Feature | Pattern 4 | Pattern 5 |
|---------|-----------|-----------|
| **Backend** | CrewAI | BeeAI |
| **Agent Framework** | CrewAI Process | BeeAI HandoffTool |
| **Backend Execution** | Sync (threaded) | Async (native) |
| **Agent Collaboration** | Sequential process | Agent handoffs |

## BeeAI Framework Specifics

### Agent Creation Pattern

```python
from beeai_framework.agents.requirement import RequirementAgent
from beeai_framework.backend import ChatModel
from beeai_framework.tools import ThinkTool, WikipediaTool

agent = RequirementAgent(
    name="SpecialistName",
    llm=ChatModel.from_name("anthropic:claude-3-5-sonnet-20241022"),
    tools=[ThinkTool(), WikipediaTool()],
    role="Specialist Role",
    instructions="Detailed instructions for the agent..."
)
```

### Agent Handoffs

```python
from beeai_framework.tools import HandoffTool

coordinator = RequirementAgent(
    name="Coordinator",
    tools=[
        ThinkTool(),
        HandoffTool(specialist_agent,
                   name="ConsultSpecialist",
                   description="When to use this specialist")
    ],
    ...
)
```

### Running Agents

```python
# BeeAI is async-native
result = await agent.run(query)

# Extract response
if hasattr(result, 'content'):
    response = result.content
elif isinstance(result, str):
    response = result
else:
    response = str(result)
```

## Claude SDK Tool Integration

### Tool Definition Format

```python
{
    "name": "tool_name",
    "description": "What this tool does and when to use it",
    "input_schema": {
        "type": "object",
        "properties": {
            "param_name": {
                "type": "string",
                "description": "Parameter description"
            }
        },
        "required": ["param_name"]
    }
}
```

### Tool Execution

```python
async def execute_tool(self, tool_name: str, args: Dict[str, Any]) -> ToolResult:
    # Execute the tool
    result = await self.tool_method(args)

    # Return standardized format
    return ToolResult(
        content=[{"type": "text", "text": result_text}],
        is_error=False
    )
```

### Agentic Loop

```python
while iteration < max_iterations:
    # 1. Call Claude with tools
    response = claude_client.messages.create(
        model="claude-3-5-sonnet-20241022",
        tools=tool_definitions,
        messages=conversation_history
    )

    # 2. Check if tool use requested
    if response.stop_reason == "tool_use":
        tool_result = await execute_tool(...)
        # 3. Add result to conversation
        # 4. Continue loop
    else:
        # 5. Return final response
        return final_text
```

## Development Best Practices

### 1. Logging

The project uses structured logging with two outputs:
- **Console**: Clean user-friendly messages (INFO level)
- **File**: Detailed debug logs in `logs/pattern5_session_*.log`

Enable debug mode for troubleshooting:
```python
evi = Pattern5EVIInterface(debug_mode=True)
```

### 2. Error Handling

Always wrap operations in try-except with fallback:
```python
try:
    result = await beeai_manager.process_complex_query(query)
    await self._send_to_evi(result)
except Exception as e:
    self.logger.error(f"BeeAI error: {e}", exc_info=True)
    fallback = "I encountered an issue. Could you rephrase that?"
    await self._send_to_evi(fallback)
```

### 3. Code Organization

**DO**:
- Keep tool definitions in `beeai_sdk_tools.py`
- Keep agent configuration in `beeai_manager.py`
- Keep EVI interface clean in `evi_interface_pattern5.py`

**DON'T**:
- Use `query_router.py` (Claude handles routing)
- Modify `evi_tools.py` (reused from Pattern 3)
- Use `asyncio.to_thread` for BeeAI (it's async-native)

### 4. Testing Components

**Test BeeAI manager standalone:**
```bash
python beeai_manager.py
```

**Test tool registry:**
```bash
python beeai_sdk_tools.py
```

**Test full system:**
```bash
python evi_interface_pattern5.py
```

## Common Issues & Solutions

### Issue: No Audio Playback

**Symptoms**:
- Audio bytes received in logs
- No sound from speakers

**Diagnosis**:
```python
import sounddevice as sd
devices = sd.query_devices()
out = devices[sd.default.device[1]]
print(f"Output: {out['name']}, channels: {out['max_output_channels']}")
```

**Solution**:
- If `max_output_channels: 0`, change system output device
- Use MacBook speakers or ensure Bluetooth device output is selected

### Issue: BeeAI Initialization Fails

**Error**: `Failed to initialize LLM anthropic:claude-3-5-sonnet-20241022`

**Check**:
```bash
echo $ANTHROPIC_API_KEY  # Should show your API key
```

**Solution**:
- Verify `ANTHROPIC_API_KEY` is set in `.env`
- Ensure API key has correct permissions
- Check API key format: `sk-ant-...`

### Issue: Claude Agent SDK Tool Use Fails

**Error**: `Tool requested but execution failed`

**Debug**:
1. Check tool definitions match Claude SDK format
2. Verify tool method is async
3. Check tool result format (must be `ToolResult` with content list)

**Solution**:
```python
# Correct tool result format
return ToolResult(
    content=[{"type": "text", "text": "Result text here"}],
    is_error=False
)
```

### Issue: Microphone Not Working

**Check device configuration**:
```bash
python -c "import sounddevice as sd; print(sd.query_devices())"
```

Look for device with `max_input_channels > 0` and ensure it's set as system default.

## Model Configuration

### Current Setup (Recommended)

```python
# All Claude agents use same model
model_name = "anthropic:claude-3-5-sonnet-20241022"
```

### Alternative Models

```python
# Opus for maximum intelligence (slower, more expensive)
model_name = "anthropic:claude-3-opus-20240229"

# Haiku for faster responses (less capable)
model_name = "anthropic:claude-3-haiku-20240307"

# OpenAI (requires OPENAI_API_KEY)
model_name = "openai:gpt-4"
```

**Note**: For offline/local models, see future documentation on Ollama integration.

## System Prompt Guidelines

The Claude orchestrator uses a carefully crafted system prompt (evi_interface_pattern5.py:249-293):

### Key Principles

1. **Tool Usage Discipline**: Use tools only for real-time data
2. **Knowledge First**: Use Claude's knowledge for general info
3. **Voice Optimization**: Keep responses concise and conversational
4. **Emotional Awareness**: Match user's emotional tone
5. **BeeAI Escalation**: Route complex queries to BeeAI backend

### Customizing the Prompt

Edit `evi_interface_pattern5.py:249` to adjust:
- Tool usage guidelines
- Response style and tone
- When to escalate to BeeAI
- Voice delivery instructions

## Metrics Tracking

Session metrics are automatically tracked when enabled:
```python
evi = Pattern5EVIInterface(enable_metrics=True)
```

Metrics shown at end of session:
- Total queries processed
- Tool usage breakdown
- Average response time
- Conversation summary

## Git Workflow

Current branch: `main`

**Before committing**:
1. Test audio playback works
2. Verify Claude routing with test queries
3. Check BeeAI agents initialize correctly
4. Run in debug mode to catch issues

**Commit message format**:
```
Component: Brief description

- Detailed change 1
- Detailed change 2

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
```

## Performance Characteristics

### Response Times

- **Quick tools**: < 1 second (weather, time, calc)
- **Claude routing**: 200-500ms additional overhead
- **BeeAI simple**: 3-5 seconds
- **BeeAI complex**: 10-20 seconds
- **Total with BeeAI**: ~4-21 seconds (vs 0.5-1s for quick tools)

### Cost Estimates (per query)

- **Quick tool only**: $0.01 (Claude routing only)
- **BeeAI consultation**: $0.05-0.15 (multiple Claude calls)
- **Complex multi-step**: $0.20-0.50 (agent handoffs + synthesis)

**Note**: Using `claude-3-5-sonnet-20241022`. Opus would be 3-5x more expensive.

## Future Improvements

### Planned Enhancements

1. **Offline Mode**: Ollama integration for local models
2. **Memory**: Conversation persistence across sessions
3. **Agent Customization**: User-defined specialist agents
4. **Performance**: Response caching for common queries
5. **Multimodal**: Image input for BeeAI agents

### Research Directions

- Emotion-aware tool selection
- Dynamic agent creation based on query type
- Cross-agent learning and optimization
- Real-time model switching (Sonnet → Opus for complex)

## Troubleshooting Checklist

Audio issues:
- [ ] Check system default audio devices
- [ ] Verify `max_output_channels > 0` for output device
- [ ] Check logs for `audio_output` messages
- [ ] Test with MacBook built-in devices

Claude SDK issues:
- [ ] Verify `ANTHROPIC_API_KEY` in `.env`
- [ ] Check API key has correct format and permissions
- [ ] Ensure tool definitions match Claude SDK spec
- [ ] Verify async/await used correctly

BeeAI issues:
- [ ] Check BeeAI manager initialization
- [ ] Verify agent handoff configurations
- [ ] Test standalone with `python beeai_manager.py`
- [ ] Check agent tool availability

Routing issues:
- [ ] Enable debug logging
- [ ] Check Claude system prompt
- [ ] Verify tool descriptions are clear
- [ ] Monitor tool selection in logs

## Resources

- Hume EVI Documentation: https://dev.hume.ai/docs/empathic-voice-interface-evi
- BeeAI Framework: https://github.com/i-am-bee/beeai-framework
- Claude API Docs: https://docs.anthropic.com/claude/reference
- sounddevice docs: https://python-sounddevice.readthedocs.io/

---

**Last Updated**: 2025-10-15
**Pattern**: Pattern 5 (EVI + Claude + BeeAI)
**Python Version**: 3.10+
**Primary Model**: claude-3-5-sonnet-20241022
