# Interactive Data Generator Guide

## 🚀 New Features

### 1. Back Navigation System (⬅️)
Navigate back to previous steps if you make a mistake:
- Press `0` or type `back` to return to previous menus
- Navigation stack tracks your path through the interface
- Available throughout the conversation building process

### 2. Copy & Modify Existing Data (📋)
Reuse and modify existing conversation data:
- Search and browse all existing data entries
- Copy conversation history from any previous entry
- Modify copied data to create variations
- Search by ID for quick finding

## 🎯 Main Features

### Main Menu Options:
1. **Create new data entry** - Start fresh conversation
2. **Copy and modify existing data entry** - Reuse existing data
3. **Exit** - End session

### Conversation Builder:
1. **Add message to conversation** - Build conversation step by step
2. **Create expected tool call and finish** - Define the expected AI response
3. **Modify conversation history** - Edit, delete, or reorder messages
4. **← Go back to previous step** - Navigate backwards (when available)
5. **Cancel and return to main menu** - Exit current conversation

## 📝 Usage Examples

### Creating New Data Entry:
```
1. Choose "Create new data entry" from main menu
2. Add messages alternating between user and assistant
3. When conversation is complete, create expected tool call
4. Review and save to train/eval split
```

### Copying Existing Data:
```
1. Choose "Copy and modify existing data entry"
2. Browse or search existing entries by ID
3. Select entry to copy
4. Modify conversation as needed
5. Create new expected tool call
6. Save as new entry
```

### Back Navigation:
```
- At any step, look for "← Go back" option
- Type "0" in menus or "back" in text inputs
- System remembers your previous state
- Navigation stack clears when starting new conversation
```

## 🛠️ Tool Call Parameters

### submit_request:
- **Required**: product_or_service, quantity_or_scope, delivery_terms, origin, delivery_location, b2b_or_b2c
- **Optional**: documents (array), specifications (object)

### cancel_request:
- **Required**: request_id, content

### reply_to_buyer:
- **Required**: text

## 💡 Tips

1. **Use Copy Feature**: Save time by copying similar conversations
2. **Navigate Back**: Don't restart if you make a mistake - just go back
3. **Search by ID**: Use partial ID matching to find specific entries
4. **Preview Conversations**: See conversation previews before copying
5. **Modify Freely**: Edit copied conversations to create variations

## 🎨 Data Format

Each entry is saved as JSONL with:
```json
{
  "id": "unique_identifier", 
  "history": [
    {"role": "user", "content": "message"},
    {"role": "assistant", "content": "response"}
  ],
  "expected_tool_call": {
    "name": "tool_name",
    "arguments": {...}
  }
}
```

## 🏃 Quick Start

1. Run: `pipenv run python generate_data.py`
2. Choose option 1 or 2 from main menu
3. Follow prompts to build conversations
4. Use back navigation if you need to correct mistakes
5. Copy existing data to create variations efficiently