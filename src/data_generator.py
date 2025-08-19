#!/usr/bin/env python3

import json
import os
import uuid
from typing import Dict, List, Any, Optional
from .tools import get_available_tools, get_tool_names


class InteractiveDataGenerator:
    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        self.tools = get_available_tools()
        self.tool_names = get_tool_names()
        self.current_conversation = []
        self.current_id = None
        
        # Ensure directories exist
        os.makedirs(os.path.join(data_dir, "train"), exist_ok=True)
        os.makedirs(os.path.join(data_dir, "eval"), exist_ok=True)
    
    def start_new_conversation(self):
        """Start a new conversation data entry."""
        self.current_conversation = []
        self.current_id = f"data_{uuid.uuid4().hex[:8]}"
        print(f"\n🆕 Starting new conversation: {self.current_id}")
        print("=" * 50)
    
    def add_message_to_history(self):
        """Add a message to the conversation history."""
        print("\nAdding message to conversation history:")
        
        # Get role
        while True:
            role = input("Enter role (user/assistant): ").strip().lower()
            if role in ["user", "assistant"]:
                break
            print("❌ Please enter 'user' or 'assistant'")
        
        # Get content
        content = input(f"Enter {role} message: ").strip()
        if not content:
            print("❌ Message cannot be empty")
            return False
        
        # Add to conversation
        message = {"role": role, "content": content}
        self.current_conversation.append(message)
        
        print(f"✅ Added {role} message to conversation")
        self._display_current_conversation()
        return True
    
    def create_expected_tool_call(self):
        """Create an expected tool call."""
        print("\nCreating expected tool call:")
        print("Available tools:")
        for i, tool_name in enumerate(self.tool_names, 1):
            tool = next(t for t in self.tools if t["function"]["name"] == tool_name)
            print(f"{i}. {tool_name} - {tool['function']['description']}")
        
        # Select tool
        while True:
            try:
                choice = int(input(f"\nSelect tool (1-{len(self.tool_names)}): "))
                if 1 <= choice <= len(self.tool_names):
                    selected_tool = self.tool_names[choice - 1]
                    break
                else:
                    print(f"❌ Please enter a number between 1 and {len(self.tool_names)}")
            except ValueError:
                print("❌ Please enter a valid number")
        
        # Get tool definition
        tool_def = next(t for t in self.tools if t["function"]["name"] == selected_tool)
        function_def = tool_def["function"]
        
        print(f"\n📝 Selected: {selected_tool}")
        print(f"Description: {function_def['description']}")
        
        # Build arguments
        arguments = {}
        properties = function_def["parameters"]["properties"]
        required = function_def["parameters"].get("required", [])
        
        print(f"\nFilling arguments for {selected_tool}:")
        print("-" * 30)
        
        for param_name, param_info in properties.items():
            is_required = param_name in required
            param_type = param_info["type"]
            description = param_info.get("description", "")
            
            prompt = f"{param_name}"
            if is_required:
                prompt += " (REQUIRED)"
            prompt += f" ({param_type})"
            if description:
                prompt += f" - {description}"
            
            if param_info.get("enum"):
                prompt += f" [Options: {', '.join(param_info['enum'])}]"
            
            # Add format hints for complex types
            if param_type == "array":
                prompt += "\n  Format: item1, item2, item3 (comma-separated)"
            elif param_type == "object":
                prompt += "\n  Format: key1:value1, key2:value2 OR {\"key1\":\"value1\",\"key2\":\"value2\"}"
            
            print(f"\n{prompt}")
            
            value = input("Enter value (press Enter to skip): ").strip()
            
            if value:
                # Type conversion
                if param_type == "integer":
                    try:
                        arguments[param_name] = int(value)
                    except ValueError:
                        print(f"⚠️ Invalid integer, storing as string")
                        arguments[param_name] = value
                elif param_type == "number":
                    try:
                        arguments[param_name] = float(value)
                    except ValueError:
                        print(f"⚠️ Invalid number, storing as string")
                        arguments[param_name] = value
                elif param_type == "boolean":
                    arguments[param_name] = value.lower() in ["true", "yes", "1", "y"]
                elif param_type == "array":
                    # Handle arrays - expect comma-separated values
                    if value.strip():
                        array_values = [item.strip() for item in value.split(",")]
                        arguments[param_name] = array_values
                    else:
                        arguments[param_name] = []
                elif param_type == "object":
                    # Handle objects - expect JSON string or key:value pairs
                    if value.startswith("{") and value.endswith("}"):
                        try:
                            arguments[param_name] = json.loads(value)
                        except json.JSONDecodeError:
                            print(f"⚠️ Invalid JSON object, storing as string")
                            arguments[param_name] = value
                    else:
                        # Convert key:value,key2:value2 format to dict
                        try:
                            obj = {}
                            if value.strip():
                                pairs = value.split(",")
                                for pair in pairs:
                                    if ":" in pair:
                                        key, val = pair.split(":", 1)
                                        obj[key.strip()] = val.strip()
                                arguments[param_name] = obj
                            else:
                                arguments[param_name] = {}
                        except Exception:
                            print(f"⚠️ Invalid object format, storing as string")
                            arguments[param_name] = value
                else:
                    arguments[param_name] = value
            elif is_required:
                print(f"⚠️ {param_name} is required but was left empty")
        
        expected_tool_call = {
            "name": selected_tool,
            "arguments": arguments
        }
        
        print(f"\n✅ Created expected tool call:")
        print(json.dumps(expected_tool_call, indent=2))
        
        return expected_tool_call
    
    def review_and_modify_data(self, expected_tool_call: Dict[str, Any]) -> tuple[bool, Dict[str, Any]]:
        """Review the complete data entry and allow modifications."""
        print("\n" + "=" * 60)
        print("📋 REVIEW CURRENT DATA ENTRY")
        print("=" * 60)
        
        print(f"ID: {self.current_id}")
        print(f"\nConversation History ({len(self.current_conversation)} messages):")
        self._display_current_conversation()
        
        print(f"\nExpected Tool Call:")
        print(json.dumps(expected_tool_call, indent=2))
        
        while True:
            print("\nOptions:")
            print("1. Save this data entry")
            print("2. Modify conversation history")
            print("3. Modify expected tool call")
            print("4. Discard this entry")
            
            choice = input("\nChoose option (1-4): ").strip()
            
            if choice == "1":
                return True, expected_tool_call
            elif choice == "2":
                self._modify_conversation_history()
            elif choice == "3":
                expected_tool_call = self._modify_tool_call(expected_tool_call)
            elif choice == "4":
                return False, expected_tool_call
            else:
                print("❌ Invalid choice. Please select 1-4.")
    
    def save_data_entry(self, expected_tool_call: Dict[str, Any], split: str = "train"):
        """Save the current data entry to a JSONL file."""
        data_entry = {
            "id": self.current_id,
            "history": self.current_conversation,
            "expected_tool_call": expected_tool_call
        }
        
        # Choose filename
        split_dir = os.path.join(self.data_dir, split)
        filename = f"{split}_data.jsonl"
        filepath = os.path.join(split_dir, filename)
        
        # Append to file
        with open(filepath, "a") as f:
            f.write(json.dumps(data_entry) + "\n")
        
        print(f"💾 Saved data entry to {filepath}")
        return True
    
    def _display_current_conversation(self):
        """Display the current conversation history."""
        for i, msg in enumerate(self.current_conversation, 1):
            role_emoji = "👤" if msg["role"] == "user" else "🤖"
            print(f"  {i}. {role_emoji} {msg['role']}: {msg['content']}")
    
    def _modify_conversation_history(self):
        """Allow modification of conversation history."""
        if not self.current_conversation:
            print("No conversation history to modify.")
            return
        
        while True:
            print("\nCurrent conversation history:")
            self._display_current_conversation()
            
            print("\nModification options:")
            print("1. Add new message")
            print("2. Edit existing message")
            print("3. Delete message")
            print("4. Done modifying")
            
            choice = input("Choose option (1-4): ").strip()
            
            if choice == "1":
                self.add_message_to_history()
            elif choice == "2":
                self._edit_message()
            elif choice == "3":
                self._delete_message()
            elif choice == "4":
                break
            else:
                print("❌ Invalid choice.")
    
    def _edit_message(self):
        """Edit an existing message."""
        if not self.current_conversation:
            return
        
        try:
            idx = int(input(f"Enter message number to edit (1-{len(self.current_conversation)}): ")) - 1
            if 0 <= idx < len(self.current_conversation):
                msg = self.current_conversation[idx]
                print(f"Current: {msg['role']}: {msg['content']}")
                
                new_content = input("Enter new content (press Enter to keep current): ").strip()
                if new_content:
                    self.current_conversation[idx]["content"] = new_content
                    print("✅ Message updated")
                else:
                    print("Message unchanged")
            else:
                print("❌ Invalid message number")
        except ValueError:
            print("❌ Please enter a valid number")
    
    def _delete_message(self):
        """Delete a message."""
        if not self.current_conversation:
            return
        
        try:
            idx = int(input(f"Enter message number to delete (1-{len(self.current_conversation)}): ")) - 1
            if 0 <= idx < len(self.current_conversation):
                deleted_msg = self.current_conversation.pop(idx)
                print(f"🗑️ Deleted: {deleted_msg['role']}: {deleted_msg['content']}")
            else:
                print("❌ Invalid message number")
        except ValueError:
            print("❌ Please enter a valid number")
    
    def _modify_tool_call(self, tool_call: Dict[str, Any]) -> Dict[str, Any]:
        """Modify the expected tool call."""
        print(f"\nModifying tool call: {tool_call['name']}")
        print("Current arguments:")
        for key, value in tool_call["arguments"].items():
            print(f"  {key}: {value}")
        
        # Get tool definition for validation
        tool_def = next(t for t in self.tools if t["function"]["name"] == tool_call["name"])
        properties = tool_def["function"]["parameters"]["properties"]
        
        new_arguments = tool_call["arguments"].copy()
        
        print(f"\nModify arguments (press Enter to keep current value):")
        for param_name, param_info in properties.items():
            current_value = new_arguments.get(param_name, "")
            param_type = param_info["type"]
            description = param_info.get("description", "")
            
            prompt = f"{param_name} ({param_type})"
            if description:
                prompt += f" - {description}"
            prompt += f"\nCurrent: {current_value}\nNew value: "
            
            new_value = input(prompt).strip()
            
            if new_value:
                # Type conversion
                if param_type == "integer":
                    try:
                        new_arguments[param_name] = int(new_value)
                    except ValueError:
                        print(f"⚠️ Invalid integer, storing as string")
                        new_arguments[param_name] = new_value
                elif param_type == "number":
                    try:
                        new_arguments[param_name] = float(new_value)
                    except ValueError:
                        print(f"⚠️ Invalid number, storing as string")
                        new_arguments[param_name] = new_value
                elif param_type == "boolean":
                    new_arguments[param_name] = new_value.lower() in ["true", "yes", "1", "y"]
                elif param_type == "array":
                    # Handle arrays - expect comma-separated values
                    if new_value.strip():
                        array_values = [item.strip() for item in new_value.split(",")]
                        new_arguments[param_name] = array_values
                    else:
                        new_arguments[param_name] = []
                elif param_type == "object":
                    # Handle objects - expect JSON string or key:value pairs
                    if new_value.startswith("{") and new_value.endswith("}"):
                        try:
                            new_arguments[param_name] = json.loads(new_value)
                        except json.JSONDecodeError:
                            print(f"⚠️ Invalid JSON object, storing as string")
                            new_arguments[param_name] = new_value
                    else:
                        # Convert key:value,key2:value2 format to dict
                        try:
                            obj = {}
                            if new_value.strip():
                                pairs = new_value.split(",")
                                for pair in pairs:
                                    if ":" in pair:
                                        key, val = pair.split(":", 1)
                                        obj[key.strip()] = val.strip()
                                new_arguments[param_name] = obj
                            else:
                                new_arguments[param_name] = {}
                        except Exception:
                            print(f"⚠️ Invalid object format, storing as string")
                            new_arguments[param_name] = new_value
                else:
                    new_arguments[param_name] = new_value
        
        return {
            "name": tool_call["name"],
            "arguments": new_arguments
        }
    
    def run_interactive_session(self):
        """Run the main interactive data generation session."""
        print("🎯 Interactive Data Generation for GEPA Optimization")
        print("=" * 60)
        print("This tool helps you create training and validation data for your sourcing concierge AI.")
        print("\nAvailable tools:")
        for tool_name in self.tool_names:
            tool = next(t for t in self.tools if t["function"]["name"] == tool_name)
            print(f"  • {tool_name}: {tool['function']['description']}")
        
        while True:
            try:
                self.start_new_conversation()
                
                # Build conversation history
                while True:
                    print(f"\nCurrent conversation has {len(self.current_conversation)} messages")
                    
                    print("\nWhat would you like to do?")
                    print("1. Add message to history")
                    print("2. Create expected tool call and finish this conversation")
                    print("3. Cancel this conversation")
                    
                    choice = input("Choose option (1-3): ").strip()
                    
                    if choice == "1":
                        self.add_message_to_history()
                    elif choice == "2":
                        if not self.current_conversation:
                            print("❌ Cannot create tool call without conversation history")
                            continue
                        
                        expected_tool_call = self.create_expected_tool_call()
                        
                        # Review and modify
                        should_save, expected_tool_call = self.review_and_modify_data(expected_tool_call)
                        
                        if should_save:
                            # Choose split
                            while True:
                                split = input("\nSave to (train/eval): ").strip().lower()
                                if split in ["train", "eval"]:
                                    break
                                print("❌ Please enter 'train' or 'eval'")
                            
                            self.save_data_entry(expected_tool_call, split)
                            print("✅ Data entry saved successfully!")
                        else:
                            print("🗑️ Data entry discarded")
                        
                        break
                    elif choice == "3":
                        print("❌ Conversation cancelled")
                        break
                    else:
                        print("❌ Invalid choice")
                
                # Ask to continue
                while True:
                    continue_choice = input("\nCreate another data entry? (y/n): ").strip().lower()
                    if continue_choice in ["y", "yes"]:
                        break
                    elif continue_choice in ["n", "no"]:
                        print("\n👋 Data generation session ended. Thank you!")
                        return
                    else:
                        print("❌ Please enter 'y' or 'n'")
                        
            except KeyboardInterrupt:
                print("\n\n👋 Data generation session interrupted. Goodbye!")
                return
            except Exception as e:
                print(f"\n❌ An error occurred: {str(e)}")
                continue_choice = input("Continue with data generation? (y/n): ").strip().lower()
                if continue_choice not in ["y", "yes"]:
                    return


def main():
    """Run the interactive data generator."""
    data_dir = "/Users/darshan/Documents/claude_code_projects/GEPA_implementation_for_aorora_supplies/data"
    generator = InteractiveDataGenerator(data_dir)
    generator.run_interactive_session()


if __name__ == "__main__":
    main()