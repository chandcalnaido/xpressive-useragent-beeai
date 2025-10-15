# Xpressive UserAgent - BeeAI Experiment

Experimental repository for integrating [BeeAI Framework](https://github.com/i-am-bee/beeai-framework) with Hume EVI (Empathic Voice Interface).

## Overview

This project explores replacing CrewAI with BeeAI framework for intelligent voice interface routing. It implements an EVI system that routes user queries between quick response tools and BeeAI multi-agent backend based on query complexity.

## Architecture

```
User Speech → EVI Transcription → Query Router
                                      ↓
                        ┌─────────────┴──────────────┐
                        ↓                            ↓
                   Quick Tools                   BeeAI Agents
                   (< 1 second)                 (3-10 sec)
                        ↓                            ↓
                        └─────────────┬──────────────┘
                                      ↓
                           EVI Speech Synthesis
                                      ↓
                              Audio Playback
```

## Components

- **Query Router** - Analyzes query complexity and routes appropriately
- **Quick Tools** - Fast response tools (weather, time, calculator)
- **BeeAI Manager** - Multi-agent backend for complex queries
- **EVI Interface** - Voice interaction layer

## Status

🚧 **Work in Progress** - Initial setup phase

This is an experimental fork to test BeeAI framework capabilities as an alternative to CrewAI.

## Original Project

Based on [xpressive userAgent](https://github.com/chandc/xpressive-useragent) Pattern 3 implementation.

## License

TBD
