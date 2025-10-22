import json
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime
from config import PROBLEMS_DIR, TOOLS_DIR, RESULTS_DIR, TEMPLATES_DIR

class FileManager:
    """Manage local JSON files for problems, tools, results, and templates"""
    
    def load_problems(self) -> List[Dict]:
        """Load all problems from data/problems/*.json"""
        problems = []
        
        for file_path in PROBLEMS_DIR.glob("*.json"):
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    
                    # Handle both single problem and array
                    if isinstance(data, list):
                        problems.extend(data)
                    else:
                        problems.append(data)
            except Exception as e:
                print(f"Error loading {file_path}: {e}")
        
        return problems
    
    def load_tools(self, tool_ids: Optional[List[str]] = None) -> List[Dict]:
        """Load tool descriptors from data/tools/*.json"""
        tools = []
        
        if tool_ids:
            # Load specific tools
            for tool_id in tool_ids:
                file_path = TOOLS_DIR / f"{tool_id}.json"
                if file_path.exists():
                    try:
                        with open(file_path, 'r') as f:
                            tools.append(json.load(f))
                    except Exception as e:
                        print(f"Error loading {tool_id}: {e}")
        else:
            # Load all tools
            for file_path in TOOLS_DIR.glob("*.json"):
                try:
                    with open(file_path, 'r') as f:
                        tools.append(json.load(f))
                except Exception as e:
                    print(f"Error loading {file_path}: {e}")
        
        return tools
    
    def load_templates(self) -> Dict[str, Dict]:
        """Load saved prompt templates (both system and user prompts)"""
        templates_file = TEMPLATES_DIR / "saved_templates.json"
        
        if templates_file.exists():
            try:
                with open(templates_file, 'r') as f:
                    data = json.load(f)
                    # Handle old format (just strings) and new format (dicts with system/user)
                    if data and isinstance(next(iter(data.values()), None), str):
                        # Convert old format to new format
                        return {name: {"system": content, "user": ""} for name, content in data.items()}
                    return data
            except:
                return {}
        return {}
    
    def save_template(self, name: str, system_content: str, user_content: str = ""):
        """Save both system and user prompt templates"""
        templates = self.load_templates()
        templates[name] = {
            "system": system_content,
            "user": user_content
        }
        
        templates_file = TEMPLATES_DIR / "saved_templates.json"
        with open(templates_file, 'w') as f:
            json.dump(templates, f, indent=2)
    
    def save_test_result(self, test_id: str, results: Dict, config: Dict):
        """Save test results to data/test_results/"""
        timestamp = datetime.utcnow().isoformat()
        
        data = {
            'test_id': test_id,
            'timestamp': timestamp,
            'results': results,
            'config': config,
            'metadata': results['metadata']
        }
        
        # Use timestamp in filename for easy sorting
        filename = f"{timestamp.replace(':', '-')}_{test_id}.json"
        file_path = RESULTS_DIR / filename
        
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)
    
    def load_test_history(self, limit: int = 50) -> List[Dict]:
        """Load recent test results"""
        results = []
        
        # Get all result files, sorted by modification time (newest first)
        files = sorted(
            RESULTS_DIR.glob("*.json"),
            key=lambda p: p.stat().st_mtime,
            reverse=True
        )
        
        for file_path in files[:limit]:
            try:
                with open(file_path, 'r') as f:
                    results.append(json.load(f))
            except Exception as e:
                print(f"Error loading {file_path}: {e}")
        
        return results