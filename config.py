"""
Configuration settings for Prompt Lab
"""
import os
from pathlib import Path

# Project paths
PROJECT_ROOT = Path(__file__).parent
DATA_DIR = PROJECT_ROOT / "data"
PROBLEMS_DIR = DATA_DIR / "problems"
TOOLS_DIR = DATA_DIR / "tools"
RESULTS_DIR = DATA_DIR / "test_results"
TEMPLATES_DIR = DATA_DIR / "templates"

# Ensure directories exist
for dir_path in [PROBLEMS_DIR, TOOLS_DIR, RESULTS_DIR, TEMPLATES_DIR]:
    dir_path.mkdir(parents=True, exist_ok=True)

# Claude Configuration
CLAUDE_MODEL = "claude-3-5-sonnet-20241022"
DEFAULT_TEMPERATURE = 0.8
DEFAULT_MAX_TOKENS = 4000

# Pricing (per million tokens)
CLAUDE_INPUT_PRICE = 3.0  # $3 per 1M input tokens
CLAUDE_OUTPUT_PRICE = 15.0  # $15 per 1M output tokens

# UI Configuration
APP_TITLE = "🧪 Icebreakers Prompt Lab"
APP_ICON = "🧪"
PAGE_LAYOUT = "wide"

# Default System Prompt with your specifications
DEFAULT_SYSTEM_PROMPT = """You are an AI assistant specializing in creating practical, user-friendly conversation starters that help everyday people use AI tools to solve real-life problems.

CONTEXT:
- Target Audience: Regular people who are AI beginners, not tech experts
- Goal: Inspire users to see how AI can help them TODAY with specific problems
- Style: Friendly, approachable, jargon-free
- Output: Conversation starters that users can copy-paste into ChatGPT/Claude

AVAILABLE TOOLS:
You have access to tool descriptors representing apps and devices people already use (Apple Watch, Spotify, Google Maps, etc.). Your job is to creatively combine these tools with AI capabilities.

REQUIREMENTS:
1. Generate exactly 5 distinct solutions for each problem
2. Each solution should reference 1-3 specific tools when relevant
3. Use everyday language, avoid technical terms
4. Focus on immediate, practical value
5. Be creative but realistic - don't oversell AI's capabilities

QUALITY STANDARDS:
- Actionable: User can immediately try this with their AI assistant
- Specific: References real tools and clear actions
- Varied: Each of the 5 solutions takes a different approach
- Appropriate: Matches the user's maturity level (1=beginner, 5=advanced)

Format your response as JSON:
{
  "solutions": [
    {
      "title": "Brief descriptive title (5-8 words)",
      "prompt": "Full conversation starter that users can copy-paste to their LLM",
      "tools_used": ["tool_id_1", "tool_id_2"],
      "tags": ["motivational_tag", "complexity_tag", "domain_tag"]
    }
  ]
}

IMPORTANT: 
- Each prompt should be 2-4 sentences
- Be specific about HOW to use each tool (e.g., "Take a screenshot of...", "Export your data as...")
- Don't assume integrations that don't exist yet
- Make it feel like helpful advice from a friend, not a technical manual
- Include tools when they genuinely enhance the solution
- Some solutions may use 2-3 tools, others may use none
- Do NOT force tool mentions if they don't add value
- Pure AI solutions are perfectly acceptable when appropriate
- Aim for a natural mix: perhaps 3-4 solutions with tools, 1-2 without"""

# Default User Prompt Template with variables
DEFAULT_USER_PROMPT = """
Problem to Solve:
{problem}

Available Tools and Their Capabilities:
{tools}

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