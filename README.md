# Icebreakers Prompt Lab

A simple local tool for testing AI prompt generation strategies that help everyday people use AI tools to solve real-life problems.

## Quick Start (Local Development)

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Set Up API Key
```bash
# Create .env file
cp .env.example .env

# Edit .env and add your Anthropic API key
# ANTHROPIC_API_KEY=sk-ant-your-key-here
```

### 3. Add Your Data
Put your files in the `data/` folders:
- `data/problems/*.json` - Problem statements
- `data/tools/*.json` - Tool descriptors

### 4. Run
```bash
streamlit run app.py
```

Open your browser to `http://localhost:8501`

## Deployment to Streamlit Community Cloud

### 1. Fork/Clone Repository
Push your code to GitHub (make sure `.env` is NOT included)

### 2. Deploy on Streamlit Cloud
1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Connect your GitHub repository
3. Select `app.py` as the main file

### 3. Add Secrets
In your Streamlit app settings, go to "Secrets" and add:
```toml
ANTHROPIC_API_KEY = "sk-ant-your-api-key-here"
```

### 4. Deploy
Click "Deploy" and your app will be live!

**Security Note**: Never commit your `.env` file or API keys to GitHub. Always use Streamlit Secrets for deployment.

## Data Format

### Problems (data/problems/*.json)
```json
[
  {
    "problem_id": "nutrition_l1_001",
    "domain": "health",
    "subdomain": "nutrition",
    "level": 1,
    "problem_text": "I want to understand how different foods affect my energy"
  }
]
```

### Tools (data/tools/*.json)

#### Simple Format
```json
{
  "tool_id": "apple_watch",
  "display_name": "Apple Watch",
  "category": "health_fitness",
  "integration_status": "screenshot_only",
  "inputs": {
    "screenshot": {
      "data_type": "image",
      "use_cases": ["Daily step count", "Heart rate"]
    }
  },
  "tags": {
    "data_types": ["steps", "heart_rate"],
    "domains": ["health", "fitness"]
  }
}
```

#### Complex Format (with sub-systems)
```json
{
  "main_system": "Google Maps",
  "integration_score": 7.0,
  "sub_systems": {
    "google_maps_mobile_app": {
      "system_name": "Google Maps Mobile App",
      "description": "Primary consumer navigation app",
      "inputs": {
        "screenshot": {
          "use_cases": ["Extract route information"]
        }
      }
    }
  }
}
```

## Features

- ✅ Generate 5 AI conversation starters per problem
- ✅ Test different prompt templates  
- ✅ Track costs in real-time
- ✅ Save/load templates
- ✅ View test history
- ✅ Compare results side-by-side
- ✅ Export as JSON or text
- ✅ Support for complex tool formats

## Cost Tracking

The app tracks:
- Tokens used per generation
- Estimated API costs
- Total spending across session

All data is stored locally in `data/test_results/`

## Prompt Philosophy

The system is designed to:
- Create practical, user-friendly conversation starters
- Help everyday people (not tech experts) use AI tools
- Focus on immediate, actionable value
- Use everyday language, avoiding technical jargon
- Balance tool usage (3-4 solutions with tools, 1-2 pure AI)

## System Prompt Template

The default system prompt emphasizes:
- **Target Audience**: Regular people who are AI beginners
- **Goal**: Inspire users to see how AI can help them TODAY
- **Style**: Friendly, approachable, jargon-free
- **Output**: Copy-paste ready conversation starters

## Project Structure

```
prompt-lab/
├── app.py                    # Main Streamlit application
├── config.py                 # Configuration settings
├── requirements.txt          # Python dependencies
├── .env                     # API keys (create from .env.example)
├── services/                # Business logic
│   ├── claude_client.py    # Claude API integration
│   ├── file_manager.py     # Local file operations
│   └── cost_tracker.py     # Usage and cost tracking
├── components/              # UI components
│   ├── results_display.py  # Solution display
│   └── comparison_view.py  # Test comparison
└── data/                   # Local data storage
    ├── problems/           # Problem JSON files
    ├── tools/              # Tool descriptor JSON files
    ├── test_results/       # Generated test results
    └── templates/          # Saved prompt templates
```

## Tips for Best Results

1. **Problem Selection**: Choose problems that are specific but relatable
2. **Tool Selection**: Pick 2-4 tools that genuinely relate to the problem
3. **Temperature**: Use 0.7-0.9 for creative variety
4. **Maturity Levels**: 
   - Level 1: Complete beginners
   - Level 2: Some experience
   - Level 3: Regular users
   - Level 4: Advanced users
   - Level 5: Power users

## Troubleshooting

### API Key Issues
- Make sure `.env` file exists with your Anthropic API key
- Verify the key starts with `sk-ant-`

### No Problems/Tools Found
- Add JSON files to `data/problems/` and `data/tools/`
- Check JSON syntax is valid

### Generation Errors
- Check your internet connection
- Verify API key has sufficient credits
- Try reducing max_tokens if hitting limits

## License

MIT License - Use freely for testing and development