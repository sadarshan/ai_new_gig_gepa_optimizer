# GEPA Sourcing Concierge Optimization

This project uses GEPA (Gradient-free Evolutionary Prompt Adaptation) to optimize prompts for a sourcing concierge AI that helps buyers find products and services through tool calling.

## Setup

1. **Install dependencies:**
   ```bash
   pipenv install
   ```

2. **Configure environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env with your Portkey credentials
   ```

3. **Prepare your dataset:**
   - Add training data to `data/train/` as `.jsonl` files
   - Add evaluation data to `data/eval/` as `.jsonl` files
   - Each line should have format: `{"id": "...", "history": [...], "expected_tool_call": {...}}`

## Usage

```bash
pipenv run python main.py
```

## Configuration

### Portkey Setup (Required)

Set one of these options in your `.env` file:

**Option 1: Config ID (Recommended)**
```env
PORTKEY_API_KEY=pk-your-api-key
PORTKEY_CONFIG_ID=your-config-id
```

**Option 2: Virtual Key**
```env
PORTKEY_API_KEY=pk-your-api-key
PORTKEY_VIRTUAL_KEY=your-virtual-key
```

**Option 3: Direct Provider**
```env
PORTKEY_API_KEY=pk-your-api-key
# Uses default: provider=openai, model=gpt-4
```

### Data Format

Each dataset entry should follow this JSON structure:

```json
{
  "id": "unique_identifier",
  "history": [
    {"role": "user", "content": "I need 100 laptops for my company"},
    {"role": "assistant", "content": "I can help with that. What's your budget range?"}
  ],
  "expected_tool_call": {
    "name": "reply_to_buyer",
    "arguments": {
      "message": "I can help with that. What's your budget range per laptop?",
      "message_type": "question",
      "requires_response": true
    }
  }
}
```

## Available Tools

The system optimizes for these three tools:

1. **submit_request()** - Submit sourcing requests to suppliers
2. **cancel_request()** - Cancel existing requests
3. **reply_to_buyer()** - Send messages/questions to buyers

## File Structure

```
├── data/
│   ├── train/           # Training data (.jsonl files)
│   └── eval/            # Evaluation data (.jsonl files)
├── src/
│   ├── tools.py         # Tool definitions
│   ├── dataset.py       # Dataset loader
│   ├── adapter.py       # GEPA adapter
│   └── optimize.py      # Optimization logic
├── config/
│   └── config.py        # Configuration
├── main.py              # Entry point
└── .env                 # Environment variables
```

## Output

Results are saved to `optimization_results/` including:
- Best optimized prompt
- Performance metrics
- Optimization history