"""
Pattern 5 EVI Interface with BeeAI + Claude Agent SDK Integration
Intelligent routing and orchestration using Claude Agent SDK with BeeAI backend
"""

import asyncio
import base64
import os
import logging
from datetime import datetime
from typing import Optional, Dict, Any
from dotenv import load_dotenv

# Hume SDK
from hume.client import AsyncHumeClient
from hume import MicrophoneInterface, Stream
from hume.empathic_voice.chat.socket_client import ChatConnectOptions
from hume.empathic_voice import SubscribeEvent
from hume.empathic_voice.types import AssistantInput
from hume.tts import PostedUtterance, PostedUtteranceVoiceWithId
import sounddevice as sd
import numpy as np

# Claude Agent SDK
try:
    from anthropic import Anthropic
except ImportError:
    print("⚠️  Claude Agent SDK not installed. Install with: pip install anthropic")
    print("    For now, Pattern 5 will fall back to direct LLM calls")
    Anthropic = None

# Our custom tools (BeeAI-powered)
from beeai_sdk_tools import BeeAISDKToolRegistry, ToolResult

load_dotenv()


def setup_logging(debug_mode: bool = True):
    """
    Set up structured logging for Pattern 5 system.
    """
    os.makedirs('logs', exist_ok=True)

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    log_file = f'logs/pattern5_session_{timestamp}.log'

    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ],
        force=True
    )

    # Set console handler level
    root_logger = logging.getLogger()
    for handler in root_logger.handlers:
        if isinstance(handler, logging.StreamHandler) and not isinstance(handler, logging.FileHandler):
            handler.setLevel(logging.INFO if not debug_mode else logging.DEBUG)

    # Configure third-party loggers
    logging.getLogger('websockets').setLevel(logging.WARNING)
    logging.getLogger('hume').setLevel(logging.INFO)
    logging.getLogger('httpx').setLevel(logging.WARNING)
    logging.getLogger('httpcore').setLevel(logging.WARNING)
    logging.getLogger('anthropic').setLevel(logging.INFO)

    loggers = {
        'interface': logging.getLogger('pattern5.interface'),
        'orchestration': logging.getLogger('pattern5.orchestration'),
        'tools': logging.getLogger('pattern5.tools'),
        'beeai': logging.getLogger('pattern5.beeai'),
    }

    logging.info(f"Pattern 5 logging initialized. Session log: {log_file}")

    return loggers


class Pattern5EVIInterface:
    """
    Pattern 5 EVI Interface with Claude Agent SDK + BeeAI Integration.

    Architecture:
    1. User speaks → Hume EVI transcribes (with emotional context)
    2. Claude Agent SDK orchestrates with intelligent tool selection
    3. Tools execute (quick tools or BeeAI agent backend)
    4. Response returned through EVI
    5. Hume EVI speaks response (with emotional intelligence)

    Triple-layer emotional intelligence:
    - Layer 1: EVI emotion detection and empathic speech
    - Layer 2: Claude orchestration with context awareness
    - Layer 3: BeeAI agents powered by Claude for nuanced understanding
    """

    def __init__(self, enable_metrics: bool = True, debug_mode: bool = False):
        """
        Initialize Pattern 5 EVI Interface.

        Args:
            enable_metrics: Track tool usage and performance metrics
            debug_mode: Enable verbose debug logging
        """
        # API Keys
        self.hume_api_key = os.getenv("HUME_API_KEY")
        self.hume_config_id = os.getenv("HUME_CONFIG_ID")
        self.hume_voice_id = os.getenv("HUME_VOICE_ID", "661ab31e-c4d6-4a16-952a-b5806a9b4ad1")  # Default to retrieved voice
        self.anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")

        if not self.hume_api_key:
            raise ValueError("HUME_API_KEY environment variable is required")
        if not self.hume_config_id:
            raise ValueError("HUME_CONFIG_ID environment variable is required")
        if not self.anthropic_api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable is required")

        # Set up logging
        self.loggers = setup_logging(debug_mode=debug_mode)
        self.logger = self.loggers['interface']

        self.logger.info("Initializing Pattern 5 EVI Interface with Claude + BeeAI")

        # Initialize Hume client
        self.hume_client = AsyncHumeClient(api_key=self.hume_api_key)

        # Initialize Claude client
        if Anthropic:
            self.claude_client = Anthropic(api_key=self.anthropic_api_key)
            self.logger.info("Claude Agent SDK client initialized")
        else:
            self.claude_client = None
            self.logger.warning("Claude Agent SDK not available")

        # Initialize tool registry (BeeAI-powered)
        self.tool_registry = BeeAISDKToolRegistry(
            verbose=debug_mode,
            claude_client=self.claude_client
        )
        self.logger.info(f"BeeAI tool registry initialized with {len(self.tool_registry.get_tool_definitions())} tools")

        # Conversation state
        self.conversation_history = []
        self.socket = None
        self.stream = None

        # Metrics tracking
        self.enable_metrics = enable_metrics
        self.metrics = {
            'total_queries': 0,
            'tool_calls': {},
            'avg_response_time': 0,
            'conversation_turns': []
        }

        self.logger.debug("Pattern 5 EVI Interface initialized successfully")

    async def start_conversation(self):
        """Start the Pattern 5 conversation session"""

        async def on_open():
            print("\n" + "="*70)
            print("🎙️  Pattern 5 EVI System Ready (Claude + BeeAI)")
            print("="*70)
            print("Features:")
            print("  ✓ Claude Agent SDK intelligent orchestration")
            print("  ✓ LLM-powered tool routing")
            print("  ✓ BeeAI multi-agent backend (Claude-powered)")
            print("  ✓ Triple-layer emotional intelligence")
            print("  ✓ Multi-step reasoning capability")
            print("\nStart speaking!")
            print("="*70 + "\n")

        async def on_message(message: SubscribeEvent):
            """Handle messages from EVI with Claude SDK orchestration"""
            self.logger.debug(f"Message type: {message.type}")

            # Handle user messages
            if message.type == "user_message" and message.message.content:
                user_text = message.message.content
                print(f"\n👤 User: {user_text}")
                self.logger.info(f"User message received: {user_text}")

                # Process with Claude SDK orchestration
                await self._process_with_claude_sdk(user_text)

            # Log assistant messages
            elif message.type == "assistant_message":
                print(f"🔊 EVI: {message.message.content}")
                self.logger.info(f"EVI response: {message.message.content}")

            elif message.type == "audio_output":
                self.logger.info(f"🎵 Audio output received: {len(message.data) if hasattr(message, 'data') else 0} bytes")
                # Route audio to stream for playback
                if self.stream and hasattr(message, 'data'):
                    audio_bytes = base64.b64decode(message.data)
                    await self.stream.queue.put(audio_bytes)
                    self.logger.debug("Audio routed to playback stream")

        async def on_error(error):
            print(f"❌ Error: {error}")
            self.logger.error(f"EVI error: {error}", exc_info=True)

        async def on_close():
            print("\n👋 Conversation ended")
            self.logger.info("EVI conversation session ended")
            if self.enable_metrics:
                self._print_metrics()

        # Connect to EVI
        options = ChatConnectOptions(config_id=self.hume_config_id)
        self.stream = Stream.new()

        async with self.hume_client.empathic_voice.chat.connect_with_callbacks(
            options=options,
            on_open=on_open,
            on_message=on_message,
            on_error=on_error,
            on_close=on_close
        ) as socket:
            self.socket = socket

            # Start microphone interface
            self.logger.info("Starting microphone interface")

            await MicrophoneInterface.start(
                socket,
                allow_user_interrupt=False,
                byte_stream=self.stream
            )

            self.logger.info("Microphone interface started successfully")
            print("🎤 Microphone active. Press Ctrl+C to stop.\n")

            try:
                await asyncio.Event().wait()
            except KeyboardInterrupt:
                self.logger.info("User interrupted session with Ctrl+C")
                print("\n🛑 Shutting down...")

    async def _process_with_claude_sdk(self, user_text: str):
        """
        Process user query using Claude Agent SDK for intelligent orchestration.
        This is the core of Pattern 5.
        """
        import time
        start_time = time.time()

        self.metrics['total_queries'] += 1
        orchestration_logger = self.loggers['orchestration']

        print(f"\n🧠 Claude SDK orchestrating response...")
        orchestration_logger.info(f"Processing query: {user_text}")

        # Add to conversation history
        self.conversation_history.append({
            "role": "user",
            "content": user_text
        })

        try:
            # Call Claude with tool use capability
            # Returns tuple: (response_text, used_beeai_tools)
            response, used_beeai = await self._call_claude_with_tools(user_text)

            elapsed = time.time() - start_time
            orchestration_logger.info(f"Claude SDK processing completed in {elapsed:.2f}s")

            # Route response based on tool usage
            if response:
                if used_beeai:
                    # Use TTS for BeeAI responses to avoid autonomous EVI responses
                    orchestration_logger.info("Routing to TTS (BeeAI tools used)")
                    print("   🎵 Using TTS for consistent voice delivery...")
                    await self._send_via_tts(response)
                else:
                    # Use EVI for simple responses
                    orchestration_logger.info("Routing to EVI (simple query)")
                    await self._send_to_evi(response)

                # Track metrics
                self.metrics['conversation_turns'].append({
                    'query': user_text,
                    'response': response[:100] + "..." if len(response) > 100 else response,
                    'time': elapsed,
                    'used_beeai': used_beeai
                })

        except Exception as e:
            print(f"❌ Claude SDK error: {e}")
            orchestration_logger.error(f"Claude SDK processing error: {e}", exc_info=True)

            error_response = "I encountered an issue processing your request. Could you try rephrasing that?"
            await self._send_to_evi(error_response)

    async def _call_claude_with_tools(self, user_message: str):
        """
        Call Claude API with tool use capability.

        This implements the agentic loop:
        1. Send message with available tools
        2. If Claude wants to use a tool, execute it
        3. Send tool result back to Claude
        4. Repeat until Claude provides final response

        Returns:
            tuple: (response_text, used_beeai_tools)
        """
        orchestration_logger = self.loggers['orchestration']

        if not self.claude_client:
            # Fallback: no tool use, just return a simple response
            orchestration_logger.warning("Claude SDK not available, using fallback")
            return ("Claude SDK is not configured. Please install the anthropic package.", False)

        # Get tool definitions
        tools = self.tool_registry.get_tool_definitions()

        # Track if BeeAI tools were used
        beeai_tools = {"consult_research_team", "analyze_topic", "compare_items"}
        used_beeai = False

        # System prompt for voice assistant behavior with BeeAI context
        system_prompt = """You are an intelligent voice assistant with access to various tools.

Your capabilities:
- Quick information tools: weather, time, calculator
- Research and analysis tools: BeeAI-powered research team, topic analysis, comparisons
  (All BeeAI agents use Claude for emotional intelligence and nuanced understanding)

Tool Usage Guidelines (IMPORTANT):
1. **Use tools ONLY when you need current, accurate, real-time data:**
   - get_weather: ONLY when user asks for specific current weather ("What's weather in NYC now?")
   - get_time: ONLY when user asks for current time in a location ("What time is it in Tokyo?")
   - calculate: ONLY for actual math calculations user provides

2. **Use your knowledge for general information:**
   - General weather patterns: "What's summer weather like?" → Use knowledge, not tool
   - Time zone facts: "How many time zones in USA?" → Use knowledge, not tool
   - Math concepts: "What is calculus?" → Use knowledge, not tool

3. **Use BeeAI research team for complex queries:**
   - consult_research_team: For questions requiring research, current trends, multi-step analysis
   - analyze_topic: For deep dives, comprehensive reviews, technical explanations
   - compare_items: For comparing technologies, approaches, or concepts

   The BeeAI agents are powered by Claude and have access to Wikipedia and reasoning tools.
   They excel at nuanced understanding and emotional intelligence.

4. **Tool chaining for complex queries:**
   - Example: "What's weather in Paris and what's a famous landmark?" → Chain weather + research
   - Example: "Analyze the differences between Python and JavaScript" → Use compare_items

5. **Keep responses concise and natural for voice delivery:**
   - Your response will be spoken aloud by an empathic voice AI
   - Be conversational and friendly
   - Match the emotional tone of the user's query
   - Avoid overly technical language unless requested

Remember: Be smart about tool usage - don't call tools unnecessarily, but use them when you need
real-time data or deep analysis. The BeeAI backend provides sophisticated multi-agent analysis
when needed."""

        # Build conversation messages
        messages = self.conversation_history.copy()

        # Agentic loop with tool use
        max_iterations = 5  # Prevent infinite loops
        iteration = 0

        while iteration < max_iterations:
            iteration += 1
            orchestration_logger.debug(f"Claude SDK iteration {iteration}")

            # Call Claude
            response = self.claude_client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=4096,
                system=system_prompt,
                tools=tools,
                messages=messages
            )

            orchestration_logger.debug(f"Claude response stop_reason: {response.stop_reason}")

            # Check if Claude wants to use a tool
            if response.stop_reason == "tool_use":
                # Extract tool use from response
                tool_use_block = None
                for block in response.content:
                    if block.type == "tool_use":
                        tool_use_block = block
                        break

                if tool_use_block:
                    tool_name = tool_use_block.name
                    tool_input = tool_use_block.input
                    tool_use_id = tool_use_block.id

                    print(f"   🔧 Using tool: {tool_name}")
                    orchestration_logger.info(f"Tool requested: {tool_name} with input: {tool_input}")

                    # Track if BeeAI tools are used
                    if tool_name in beeai_tools:
                        used_beeai = True
                        orchestration_logger.info(f"BeeAI tool detected: {tool_name}")

                    # Track metrics
                    if tool_name not in self.metrics['tool_calls']:
                        self.metrics['tool_calls'][tool_name] = 0
                    self.metrics['tool_calls'][tool_name] += 1

                    # Send immediate acknowledgment for long-running operations
                    if tool_name in beeai_tools:
                        ack_message = "Let me analyze that for you. This will take a moment."
                        await self._send_to_evi(ack_message)
                        orchestration_logger.info("Sent acknowledgment for BeeAI operation")

                    # Execute the tool
                    tool_result = await self.tool_registry.execute_tool(tool_name, tool_input)

                    orchestration_logger.debug(f"Tool result: {tool_result.content}")

                    # Add assistant's tool use to conversation
                    messages.append({
                        "role": "assistant",
                        "content": response.content
                    })

                    # Add tool result to conversation
                    messages.append({
                        "role": "user",
                        "content": [
                            {
                                "type": "tool_result",
                                "tool_use_id": tool_use_id,
                                "content": tool_result.content[0]["text"]
                            }
                        ]
                    })

                    # Continue loop to get Claude's next response
                    continue

            # If we get here, Claude provided a final text response
            final_response = ""
            for block in response.content:
                if hasattr(block, "text"):
                    final_response += block.text

            orchestration_logger.info(f"Final response generated: {final_response[:100]}...")
            orchestration_logger.info(f"BeeAI tools used: {used_beeai}")

            # Add to conversation history
            self.conversation_history.append({
                "role": "assistant",
                "content": final_response
            })

            return (final_response, used_beeai)

        # Max iterations reached
        orchestration_logger.warning(f"Max iterations ({max_iterations}) reached in agentic loop")
        return ("I've processed your request, but it took longer than expected. Could you try asking in a different way?", used_beeai)

    async def _send_to_evi(self, text: str):
        """Send text to EVI to be spoken (may trigger autonomous responses)"""
        if self.socket and text:
            self.logger.debug(f"Sending to EVI for playback: {text[:100]}...")
            await self.socket.send_assistant_input(AssistantInput(text=text))
            self.logger.info("Assistant input sent to EVI for speech synthesis")

    async def _send_via_tts(self, text: str):
        """
        Send text via Hume TTS directly (bypasses EVI conversational layer).
        Prevents autonomous EVI responses during complex BeeAI outputs.
        """
        if not text:
            return

        self.logger.debug(f"Sending to Hume TTS: {text[:100]}...")

        try:
            # Create TTS utterance with the same voice as EVI config
            utterance = PostedUtterance(
                text=text,
                voice=PostedUtteranceVoiceWithId(id=self.hume_voice_id)
            )

            self.logger.debug(f"Using voice ID: {self.hume_voice_id}")

            # Stream audio from TTS API
            async for chunk in self.hume_client.tts.synthesize_json_streaming(
                utterances=[utterance],
                strip_headers=True
            ):
                # Route audio to the same playback stream EVI uses
                if self.stream and hasattr(chunk, 'data'):
                    audio_bytes = base64.b64decode(chunk.data)
                    await self.stream.queue.put(audio_bytes)
                    self.logger.debug(
                        f"TTS audio chunk: {len(audio_bytes)} bytes"
                    )

            self.logger.info("TTS speech synthesis completed")

        except Exception as e:
            self.logger.error(f"TTS synthesis error: {e}", exc_info=True)
            # Fallback to EVI if TTS fails
            self.logger.warning("Falling back to EVI for speech synthesis")
            await self._send_to_evi(text)

    def _print_metrics(self):
        """Print session metrics"""
        print("\n" + "="*70)
        print("📊 Pattern 5 Session Metrics")
        print("="*70)
        print(f"Total Queries: {self.metrics['total_queries']}")
        print(f"\nTool Usage:")

        if self.metrics['tool_calls']:
            for tool_name, count in sorted(self.metrics['tool_calls'].items(), key=lambda x: x[1], reverse=True):
                print(f"  - {tool_name}: {count} calls")
        else:
            print("  - No tools were used")

        if self.metrics['conversation_turns']:
            avg_time = sum(t['time'] for t in self.metrics['conversation_turns']) / len(self.metrics['conversation_turns'])
            print(f"\nAverage Response Time: {avg_time:.2f}s")

            print("\nConversation Summary:")
            for i, turn in enumerate(self.metrics['conversation_turns'], 1):
                print(f"  {i}. {turn['query'][:50]}... ({turn['time']:.2f}s)")

        print("="*70 + "\n")


async def main(debug_mode: bool = False):
    """Main entry point for Pattern 5"""
    print("="*70)
    print("Pattern 5: EVI + Claude + BeeAI Integration")
    print("="*70)

    try:
        evi = Pattern5EVIInterface(enable_metrics=True, debug_mode=debug_mode)
        await evi.start_conversation()
    except ValueError as e:
        print(f"\n❌ Configuration Error: {e}")
        print("\nRequired environment variables:")
        print("  - HUME_API_KEY")
        print("  - HUME_CONFIG_ID")
        print("  - ANTHROPIC_API_KEY")
        print("\nPlease set these in your .env file")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Pattern 5 ended by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
