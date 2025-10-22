import anthropic
import json
import time
import os
from typing import List, Dict
from dotenv import load_dotenv
from config import CLAUDE_MODEL, CLAUDE_INPUT_PRICE, CLAUDE_OUTPUT_PRICE

# Load environment variables
load_dotenv()

class ClaudeClient:
    def __init__(self):
        """Initialize Claude client with API key from .env"""
        api_key = os.getenv('ANTHROPIC_API_KEY')
        
        if not api_key:
            raise Exception(
                "ANTHROPIC_API_KEY not found. "
                "Create a .env file with: ANTHROPIC_API_KEY=sk-ant-your-key"
            )
        
        self.client = anthropic.Anthropic(api_key=api_key)
    
    def generate(
        self,
        problem: str,
        problem_id: str,
        tools: List[Dict],  # Now receives full tool objects
        system_prompt: str,
        user_prompt_template: str = None,
        temperature: float = 0.8,
        max_tokens: int = 4000
    ) -> Dict:
        """Generate 5 solution approaches using Claude"""
        
        # Build user prompt
        user_prompt = self._build_user_prompt(problem, tools, user_prompt_template)
        
        # Call Claude API
        start_time = time.time()
        
        try:
            response = self.client.messages.create(
                model=CLAUDE_MODEL,
                max_tokens=max_tokens,
                temperature=temperature,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": user_prompt}
                ]
            )
        except Exception as e:
            raise Exception(f"Claude API error: {e}")
        
        latency_ms = (time.time() - start_time) * 1000
        
        # Parse response
        tool_ids = [t['tool_id'] for t in tools]
        solutions = self._parse_response(response.content[0].text, tool_ids)
        
        # Calculate cost
        input_cost = (response.usage.input_tokens / 1_000_000) * CLAUDE_INPUT_PRICE
        output_cost = (response.usage.output_tokens / 1_000_000) * CLAUDE_OUTPUT_PRICE
        total_cost = input_cost + output_cost
        
        return {
            "solutions": solutions,
            "metadata": {
                "tokens": response.usage.input_tokens + response.usage.output_tokens,
                "input_tokens": response.usage.input_tokens,
                "output_tokens": response.usage.output_tokens,
                "cost_usd": total_cost,
                "latency_ms": latency_ms,
                "model": CLAUDE_MODEL,
                "temperature": temperature
            }
        }
    
    def _build_user_prompt(self, problem: str, tools: List[Dict], user_prompt_template: str = None) -> str:
        """Build the user prompt with problem and tool context"""
        
        # Build tool text first
        tool_text = ""
        for tool in tools:
            # Handle both new format (with sub_systems) and simple format
            if 'sub_systems' in tool:
                # New complex format with sub_systems
                main_system = tool.get('main_system', 'Unknown Tool')
                tool_text += f"\n### {main_system}\n"
                tool_text += f"- **Integration Score**: {tool.get('integration_score', 'N/A')}/10\n"
                
                # Process sub-systems
                for sub_id, sub_system in tool.get('sub_systems', {}).items():
                    tool_text += f"\n#### {sub_system.get('system_name', sub_id)}\n"
                    tool_text += f"- **Description**: {sub_system.get('description', 'No description')}\n"
                    
                    # Extract key capabilities from inputs
                    if 'inputs' in sub_system:
                        capabilities = []
                        for input_name, input_data in sub_system['inputs'].items():
                            if 'attributes' in input_data:
                                attrs = input_data['attributes']
                                if isinstance(attrs, dict):
                                    for key, value in attrs.items():
                                        if isinstance(value, str) and '_' not in key:
                                            capabilities.append(value)
                        if capabilities:
                            tool_text += f"- **Capabilities**: {', '.join(capabilities[:5])}\n"
            else:
                # Simple format (original)
                tool_text += f"\n### {tool.get('display_name', tool.get('tool_id'))}\n"
                tool_text += f"- **ID**: `{tool.get('tool_id')}`\n"
                tool_text += f"- **Category**: {tool.get('category', 'Unknown')}\n"
                tool_text += f"- **Integration**: {tool.get('integration_status', 'Unknown')}\n"
                
                if 'inputs' in tool:
                    tool_text += "- **What you can get from it**:\n"
                    for input_name, input_data in tool.get('inputs', {}).items():
                        use_cases = input_data.get('use_cases', [])
                        if use_cases:
                            tool_text += f"  - {', '.join(use_cases)}\n"
            
            tool_text += "\n"
        
        # Use custom template if provided, otherwise use default
        if user_prompt_template:
            # Replace variables in the template
            return user_prompt_template.format(
                problem=problem,
                tools=tool_text
            )
        else:
            # Default template
            return f"""
Problem to Solve:
{problem}

Available Tools and Their Capabilities:
{tool_text}

Your Task:
Generate exactly 5 distinct solution approaches that address this problem.
Each solution should be formatted as specified in your system instructions.

Remember:
- Be specific about HOW to use each tool (screenshots, exports, manual steps)
- Don't assume integrations that don't exist
- Make it feel like advice from a helpful friend
- Each prompt should be immediately usable by copying to an LLM
- Include tools when they genuinely enhance the solution
- Some solutions may use 2-3 tools, others may use none
- Pure AI solutions are perfectly acceptable when appropriate
"""
    
    def _parse_response(self, response_text: str, tool_ids: List[str]) -> List[Dict]:
        """Parse Claude's response into structured solutions"""
        
        try:
            parsed = json.loads(response_text)
            solutions = parsed.get('solutions', [])
            
            # Validate structure
            for solution in solutions:
                if 'title' not in solution:
                    solution['title'] = "Untitled Solution"
                if 'prompt' not in solution:
                    solution['prompt'] = "No prompt generated"
                if 'tools_used' not in solution:
                    solution['tools_used'] = []
                if 'tags' not in solution:
                    solution['tags'] = []
            
            return solutions
            
        except json.JSONDecodeError:
            return [{
                "title": "Raw Response (JSON Parse Failed)",
                "prompt": response_text,
                "tools_used": tool_ids,
                "tags": ["parse_error"]
            }]