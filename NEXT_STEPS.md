# Next Steps for Pattern 5 Development

## Current Status (2025-10-16)

✅ **Hybrid TTS Routing - WORKING**
- Simple queries (weather, time, calculator) → EVI path
- Complex queries (BeeAI tools) → TTS path
- Successfully eliminates male voice interjections during complex responses
- Voice consistency maintained across both paths

## Verified Functionality

**Simple Query Routing:**
- Queries using `get_weather`, `get_time`, `calculate` route to EVI
- Leverages EVI's emotional intelligence and prosody
- Fast response times (~1-2 seconds)

**Complex Query Routing:**
- Queries using `consult_research_team`, `analyze_topic`, `compare_items` route to TTS
- Bypasses EVI's autonomous response layer
- Consistent female voice throughout (no male voice interruptions)
- Response times: ~10-25 seconds for BeeAI processing

## Issue: Timing Mechanisms for Complex Queries

### Problem
Complex queries have significant latency (10-25 seconds) while BeeAI agents process:
1. User asks question
2. EVI sends acknowledgment: "Let me analyze that for you. This will take a moment."
3. **Long silence during BeeAI processing (10-25s)**
4. Response finally delivered via TTS

**User experience issue:** Extended silence after acknowledgment makes the system feel unresponsive.

### Proposed Solutions to Investigate

#### Option 1: Streaming Progress Updates
Leverage BeeAI's event observation system to provide real-time updates:

```python
async def _stream_progress_updates(self, data, event):
    """Stream BeeAI execution progress to user"""
    if event.path == "agent.thinking":
        await self._send_via_tts("Analyzing your question...")
    elif event.path == "agent.tool_execution":
        if "wikipedia" in event.creator:
            await self._send_via_tts("Researching relevant information...")
    elif event.path == "agent.handoff":
        await self._send_via_tts("Consulting our research specialist...")
```

**Pros:**
- User stays engaged during processing
- Transparent about what's happening
- Utilizes existing BeeAI event system

**Cons:**
- May feel chatty/verbose
- Multiple TTS calls could overlap
- Timing interruptions carefully is complex

#### Option 2: Background Music/Tones
Play subtle ambient sound during processing:

```python
async def _play_thinking_tone(self):
    """Play gentle thinking tone during BeeAI processing"""
    # Play subtle ambient sound or musical tone
    # Signals system is working without verbal interruption
```

**Pros:**
- Non-intrusive
- Clear signal of activity
- No semantic content to interrupt

**Cons:**
- Requires additional audio file/generation
- May conflict with audio stream routing
- Cultural considerations for tone choice

#### Option 3: Periodic "Still Working" Prompts
Brief updates at intervals if processing exceeds threshold:

```python
async def _monitor_processing_time(self, start_time):
    """Send periodic updates for long-running operations"""
    while processing:
        elapsed = time.time() - start_time
        if elapsed > 10:
            await self._send_via_tts("Still working on that...")
        await asyncio.sleep(8)
```

**Pros:**
- Only speaks when necessary
- Prevents "is it frozen?" moments
- Simpler than full streaming

**Cons:**
- May interrupt at awkward moments
- Timing complexity
- Could annoy users if too frequent

#### Option 4: EVI Interstitial Responses
Let EVI generate conversational filler during wait:

```python
# During BeeAI processing, allow EVI to respond to:
# - "Are you still there?"
# - "What's taking so long?"
# - User small talk

# But suppress autonomous responses to the original query
```

**Pros:**
- Maintains conversational flow
- Leverages EVI's emotional intelligence
- Handles unexpected user interjections

**Cons:**
- Complex state management
- Risk of EVI responding to original query
- May confuse conversation flow

#### Option 5: Hybrid: Quick Summary + Detailed Response
Provide immediate short answer, then detailed analysis:

```python
# 1. Claude provides quick summary from knowledge (immediate)
await self._send_via_tts("AI agents are trending toward multimodal capabilities. Let me get you the latest details...")

# 2. BeeAI provides detailed research (10-25s later)
detailed_response = await beeai.process_complex_query(...)
await self._send_via_tts(detailed_response)
```

**Pros:**
- Immediate engagement
- User gets value quickly
- Detailed info follows naturally

**Cons:**
- Two separate responses to track
- May feel disjointed
- Harder to synthesize coherently

### Recommended Approach

**Start with Option 3 (Periodic Updates) + Option 1 (Key Milestones)**

Combine the best of both:
1. Acknowledge immediately: "Let me research that for you."
2. At key BeeAI milestones, update: "Consulting specialists..." (on handoff)
3. If >15 seconds, brief update: "Almost done..."
4. Deliver final response via TTS

**Implementation priorities:**
1. Add timing thresholds to orchestration layer
2. Hook into BeeAI event observation for key milestones
3. Test optimal update frequency with users
4. Consider making update style configurable

### Additional Considerations

**Leverage BeeAI's Observability:**
- Already implemented event observation in `beeai_manager.py:220-224`
- Events available: start, update, success, error, retry
- Can detect tool usage, handoffs, thinking steps

**Voice Pacing:**
- Updates should use TTS (consistent voice)
- Keep updates very brief (3-5 words max)
- Ensure updates don't overlap with final response

**User Control:**
- Consider config option for update verbosity
- Allow users to disable progress updates
- Different modes: silent, minimal, verbose

## Future Enhancements

### Performance Optimization
- Cache common BeeAI queries
- Parallel tool execution where possible
- Optimize agent prompts for faster reasoning

### BeeAI Integration
- Custom agents for specific domains
- Memory persistence across sessions
- Dynamic agent selection based on query type

### Voice & Audio
- Emotion-aware TTS parameter tuning
- Voice cloning for personalization
- Multi-voice support (different agents = different voices?)

### Observability
- Real-time dashboard of agent execution
- Query performance analytics
- User interaction patterns

---

**Last Updated:** 2025-10-16
**Status:** Hybrid TTS routing verified working, investigating timing improvements
**Next Action:** Implement periodic progress updates for complex queries
