# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

EchoNote is an AI-powered meeting notes app with real-time transcription and offline support. It's a fork of [Hyprnote](https://github.com/fastrepl/hyprnote), built as a Tauri 2 desktop app (React + Rust) with supporting web/API services.

**License**: GPL-3.0

## Common Commands

### Development
```bash
pnpm -F desktop dev          # Run desktop app in dev mode
pnpm -F web dev              # Run web app
pnpm -F api dev              # Run API server
```

### Formatting & Validation
```bash
dprint fmt                   # Format all code (REQUIRED - do not use cargo fmt)
pnpm -r typecheck            # TypeScript checking after TS changes
cargo check                  # Rust checking after Rust changes
pnpm lint                    # Run oxlint
```

### Testing
```bash
cargo test -p <crate>        # Run tests for a specific crate
cargo test -p <crate> <test> # Run a single test
pnpm -F <package> test       # Run tests for a JS package
```

### Infrastructure
```bash
task supabase-start          # Start local Supabase
task stripe                  # Listen to Stripe webhooks
```

## Architecture

### Workspace Structure
- **apps/desktop**: Main Tauri desktop app (React frontend in `src/`, Rust backend in `src-tauri/`)
- **apps/web**: Marketing/docs site (TanStack Start)
- **apps/api**: Backend API (Hono + Bun)
- **crates/**: 80+ Rust libraries for audio processing, transcription, LLM integration
- **plugins/**: 40+ Tauri plugins for native features (calendar, contacts, audio, search, etc.)
- **packages/**: Shared TS packages (`@hypr/ui`, `@hypr/utils`, `@hypr/store`, etc.)

### Key Tech Stack
- **Frontend**: React 19, TailwindCSS 4, TanStack Query/Router/Form
- **Desktop**: Tauri 2.9 with custom Rust plugins
- **Audio**: Multiple STT providers (Whisper local, Deepgram, Azure, AWS, OpenAI)
- **AI**: Vercel AI SDK supporting Claude, GPT, Gemini, local models (Ollama/LM Studio)

### Rust Toolchain
Pinned to 1.92.0 via `rust-toolchain.toml`.

## Code Conventions

@./AGENTS.md
