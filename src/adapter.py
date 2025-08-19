import json
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

from gepa import EvaluationBatch, GEPAResult, GEPAAdapter
from .dataset import ChatDataInstance, SourcingDatasetLoader
from .tools import get_available_tools


@dataclass
class ToolCallTrajectory:
    conversation_history: List[Dict[str, str]]
    predicted_tool_call: Optional[Dict[str, Any]]
    expected_tool_call: Dict[str, Any]
    error_message: Optional[str] = None
    success: bool = False


@dataclass
class ToolCallOutput:
    predicted_tool_call: Optional[Dict[str, Any]]
    confidence: float
    reasoning: str


class SourcingConciergeGEPAAdapter(GEPAAdapter):
    def __init__(self, light_client, heavy_client, data_loader: SourcingDatasetLoader):
        self.light_client = light_client
        self.heavy_client = heavy_client
        self.data_loader = data_loader
        self.tool_definitions = data_loader.get_tool_definitions()
    
    def evaluate(self, 
                data_batch: List[ChatDataInstance], 
                candidate: Dict[str, str], 
                capture_traces: bool = False) -> EvaluationBatch:
        
        trajectories = []
        outputs = []
        scores = []
        
        system_prompt = candidate.get("system_prompt", "")
        
        for instance in data_batch:
            try:
                trajectory, output, score = self._evaluate_single_instance(
                    instance, system_prompt
                )
                trajectories.append(trajectory)
                outputs.append(output)
                scores.append(score)
            except Exception as e:
                # Handle individual failures gracefully
                trajectories.append(ToolCallTrajectory(
                    conversation_history=instance.history,
                    predicted_tool_call=None,
                    expected_tool_call=instance.expected_tool_call,
                    error_message=str(e),
                    success=False
                ))
                outputs.append(ToolCallOutput(
                    predicted_tool_call=None,
                    confidence=0.0,
                    reasoning=f"Error: {str(e)}"
                ))
                scores.append(0.0)
        
        return EvaluationBatch(
            trajectories=trajectories,
            outputs=outputs,
            scores=scores
        )
    
    def _evaluate_single_instance(self, 
                                 instance: ChatDataInstance, 
                                 system_prompt: str) -> tuple:
        
        # Prepare messages for the model
        messages = [{"role": "system", "content": system_prompt}]
        messages.extend(instance.history)
        
        # Call the model with tool definitions using Portkey
        try:
            response = self.light_client.chat.completions.create(
                messages=messages,
                tools=self.tool_definitions,
                tool_choice="required"
            )
            
            # Extract tool call from response
            predicted_tool_call = None
            if response.choices[0].message.tool_calls:
                tool_call = response.choices[0].message.tool_calls[0]
                predicted_tool_call = {
                    "name": tool_call.function.name,
                    "arguments": json.loads(tool_call.function.arguments)
                }
            
            # Calculate score based on correctness
            score = self._calculate_score(predicted_tool_call, instance.expected_tool_call)
            
            trajectory = ToolCallTrajectory(
                conversation_history=instance.history,
                predicted_tool_call=predicted_tool_call,
                expected_tool_call=instance.expected_tool_call,
                success=score > 0.5
            )
            
            output = ToolCallOutput(
                predicted_tool_call=predicted_tool_call,
                confidence=1.0 if predicted_tool_call else 0.0,
                reasoning=response.choices[0].message.content or ""
            )
            
            return trajectory, output, score
            
        except Exception as e:
            raise Exception(f"Model call failed: {str(e)}")
    
    def _calculate_score(self, 
                        predicted: Optional[Dict[str, Any]], 
                        expected: Dict[str, Any]) -> float:
        if not predicted:
            return 0.0
        
        # Check if tool name matches
        if predicted["name"] != expected["name"]:
            return 0.0
        
        # Check argument correctness
        predicted_args = predicted.get("arguments", {})
        expected_args = expected.get("arguments", {})
        
        if not expected_args:
            return 1.0 if predicted["name"] == expected["name"] else 0.0
        
        # Calculate argument match score
        total_args = len(expected_args)
        correct_args = 0
        
        for key, expected_value in expected_args.items():
            if key in predicted_args and predicted_args[key] == expected_value:
                correct_args += 1
        
        # Tool name correct (0.5) + argument accuracy (0.5)
        return 0.5 + 0.5 * (correct_args / total_args if total_args > 0 else 1.0)
    
    def make_reflective_dataset(self, 
                               candidate: Dict[str, str],
                               evaluation_batch: EvaluationBatch, 
                               components_to_update: List[str]) -> Dict[str, List[Dict[str, Any]]]:
        
        ret_d: Dict[str, List[Dict[str, Any]]] = {}
        
        assert len(components_to_update) == 1, f"Expected 1 component to update, got {len(components_to_update)}"
        comp = components_to_update[0]
        
        items: List[Dict[str, Any]] = []
        trace_instances = list(zip(evaluation_batch.trajectories, evaluation_batch.scores, evaluation_batch.outputs, strict=False))
        
        for trajectory, score, output in trace_instances:
            # Format conversation history as input
            conversation_lines = []
            for msg in trajectory.conversation_history:
                conversation_lines.append(f"{msg['role'].title()}: {msg['content']}")
            input_text = "\n".join(conversation_lines)
            
            # Format the generated tool call as output
            if trajectory.predicted_tool_call:
                generated_output = f"Tool call: {trajectory.predicted_tool_call['name']}({trajectory.predicted_tool_call.get('arguments', {})})"
            else:
                generated_output = "No tool call made"
            
            # Create feedback based on performance
            if score >= 1.0:
                feedback = f"The tool call is correct. Successfully called {trajectory.expected_tool_call['name']} with proper arguments."
            else:
                expected_call = f"{trajectory.expected_tool_call['name']}({trajectory.expected_tool_call.get('arguments', {})})"
                error_analysis = self._analyze_error(trajectory, output)
                feedback = f"The tool call is incorrect. Expected: {expected_call}. Error: {error_analysis}"
            
            # Create the sample in GEPA's expected format
            d = {
                "Inputs": input_text,
                "Generated Outputs": generated_output,
                "Feedback": feedback,
            }
            
            items.append(d)
        
        ret_d[comp] = items
        
        if len(items) == 0:
            raise Exception("No valid predictions found for any module.")
        print(ret_d)
        return ret_d
    
    def _analyze_error(self, 
                      trajectory: ToolCallTrajectory, 
                      output: ToolCallOutput) -> str:
        if not trajectory.predicted_tool_call:
            return "No tool call was made"
        
        if trajectory.predicted_tool_call["name"] != trajectory.expected_tool_call["name"]:
            return f"Wrong tool selected: predicted {trajectory.predicted_tool_call['name']}, expected {trajectory.expected_tool_call['name']}"
        
        pred_args = trajectory.predicted_tool_call.get("arguments", {})
        exp_args = trajectory.expected_tool_call.get("arguments", {})
        
        missing_args = set(exp_args.keys()) - set(pred_args.keys())
        incorrect_args = {k: (pred_args[k], exp_args[k]) for k in exp_args 
                         if k in pred_args and pred_args[k] != exp_args[k]}
        
        error_parts = []
        if missing_args:
            error_parts.append(f"Missing arguments: {list(missing_args)}")
        if incorrect_args:
            error_parts.append(f"Incorrect arguments: {incorrect_args}")
        
        return "; ".join(error_parts) if error_parts else "Unknown error"