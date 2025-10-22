import streamlit as st
import json
from datetime import datetime
import uuid
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from services.claude_client import ClaudeClient
from services.file_manager import FileManager
from services.cost_tracker import CostTracker
from components.results_display import render_results
from config import APP_TITLE, APP_ICON, PAGE_LAYOUT, DEFAULT_SYSTEM_PROMPT, DEFAULT_USER_PROMPT

# Page config
st.set_page_config(
    page_title="Loom Prompt Lab",
    page_icon=APP_ICON,
    layout=PAGE_LAYOUT,
    initial_sidebar_state="expanded"
)

# Initialize clients
if 'claude_client' not in st.session_state:
    try:
        st.session_state.claude_client = ClaudeClient()
    except Exception as e:
        st.error(f"❌ Failed to initialize Claude client: {e}")
        st.info("💡 Make sure you have a .env file with ANTHROPIC_API_KEY")
        st.stop()

if 'file_manager' not in st.session_state:
    st.session_state.file_manager = FileManager()

if 'cost_tracker' not in st.session_state:
    st.session_state.cost_tracker = CostTracker()

# Initialize session state
if 'current_results' not in st.session_state:
    st.session_state.current_results = None
if 'current_test_id' not in st.session_state:
    st.session_state.current_test_id = None
if 'selected_problem' not in st.session_state:
    st.session_state.selected_problem = None

def render_generate_mode():
    """Main generation interface"""
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("Configuration")
        
        # 1. Problem Selection
        with st.expander("📋 Select Problem", expanded=True):
            problems = st.session_state.file_manager.load_problems()
            
            if not problems:
                st.warning("⚠️ No problems found")
                st.info("Add JSON files to `data/problems/`")
                return
            
            # Filters
            domains = sorted(set(p.get('domain', 'Unknown') for p in problems))
            selected_domain = st.selectbox("Domain", ['All'] + domains)
            
            filtered_problems = problems
            if selected_domain != 'All':
                filtered_problems = [p for p in problems if p.get('domain') == selected_domain]
            
            if filtered_problems and 'level' in filtered_problems[0]:
                levels = sorted(set(p.get('level', 1) for p in filtered_problems))
                selected_level = st.selectbox("Maturity Level", ['All'] + levels)
                
                if selected_level != 'All':
                    filtered_problems = [p for p in filtered_problems if p.get('level') == selected_level]
            
            # Problem dropdown
            problem_display = [
                f"{p.get('problem_id', 'unknown')}: {p.get('problem_text', '')[:50]}..."
                for p in filtered_problems
            ]
            
            if problem_display:
                selected_idx = st.selectbox(
                    "Problem",
                    options=range(len(problem_display)),
                    format_func=lambda i: problem_display[i]
                )
                st.session_state.selected_problem = filtered_problems[selected_idx]
            else:
                st.warning("No problems match filters")
                st.session_state.selected_problem = None
        
        # 2. Tool Selection
        with st.expander("🔧 Select Tools", expanded=True):
            all_tools = st.session_state.file_manager.load_tools()
            
            if not all_tools:
                st.warning("⚠️ No tools found")
                st.info("Add JSON files to `data/tools/`")
                selected_tool_objects = []
            else:
                # Extract tool IDs and names
                tool_info = []
                for tool in all_tools:
                    if 'tool_id' in tool:
                        # Simple format
                        tool_info.append({
                            'id': tool['tool_id'],
                            'name': tool.get('display_name', tool['tool_id']),
                            'category': tool.get('category', 'Other'),
                            'tool': tool
                        })
                    elif 'main_system' in tool:
                        # Complex format - use main_system as ID
                        tool_id = tool['main_system'].lower().replace(' ', '_')
                        tool_info.append({
                            'id': tool_id,
                            'name': tool['main_system'],
                            'category': 'Integration',
                            'tool': tool
                        })
                
                # Filter by category
                tool_categories = sorted(set(t['category'] for t in tool_info))
                selected_categories = st.multiselect(
                    "Filter by Category",
                    options=tool_categories,
                    default=tool_categories
                )
                
                filtered_tools = [t for t in tool_info if t['category'] in selected_categories]
                
                # Tool selection
                selected_tool_ids = st.multiselect(
                    "Tools to Include",
                    options=[t['id'] for t in filtered_tools],
                    default=[],
                    format_func=lambda x: next(
                        (t['name'] for t in tool_info if t['id'] == x),
                        x
                    )
                )
                
                # Get full tool objects for selected IDs
                selected_tool_objects = [
                    t['tool'] for t in tool_info if t['id'] in selected_tool_ids
                ]
        
        # 3. Prompt Templates
        with st.expander("✍️ Prompt Templates", expanded=True):
            templates = st.session_state.file_manager.load_templates()
            template_options = ['Default'] + list(templates.keys())
            
            selected_template_name = st.selectbox("Load Template", options=template_options)
            
            # Load template values
            if selected_template_name == 'Default':
                initial_system_prompt = DEFAULT_SYSTEM_PROMPT
                initial_user_prompt = DEFAULT_USER_PROMPT
            else:
                template_data = templates[selected_template_name]
                if isinstance(template_data, dict):
                    initial_system_prompt = template_data.get('system', DEFAULT_SYSTEM_PROMPT)
                    initial_user_prompt = template_data.get('user', DEFAULT_USER_PROMPT)
                else:
                    # Handle old format (just string)
                    initial_system_prompt = template_data
                    initial_user_prompt = DEFAULT_USER_PROMPT
            
            # System Prompt
            st.markdown("**System Prompt** (sets overall behavior)")
            system_prompt = st.text_area(
                "System Prompt",
                value=initial_system_prompt,
                height=200,
                label_visibility="collapsed",
                help="This prompt sets the AI's overall behavior, tone, and output format"
            )
            
            # User Prompt Template
            st.markdown("**User Prompt Template** (specific request)")
            st.caption("Use {problem} and {tools} as variables that will be replaced with actual data")
            user_prompt = st.text_area(
                "User Prompt",
                value=initial_user_prompt,
                height=150,
                label_visibility="collapsed",
                help="This template is used for each request. Variables: {problem}, {tools}"
            )
            
            # Save template
            col_name, col_save = st.columns([3, 1])
            with col_name:
                new_template_name = st.text_input(
                    "Save as",
                    placeholder="my-template-v1",
                    label_visibility="collapsed"
                )
            with col_save:
                if st.button("💾", use_container_width=True):
                    if new_template_name:
                        st.session_state.file_manager.save_template(
                            new_template_name,
                            system_prompt,
                            user_prompt
                        )
                        st.success(f"✅ Saved")
                        st.rerun()
        
        # 4. Settings
        with st.expander("⚙️ Settings"):
            temperature = st.slider("Temperature", 0.0, 1.0, 0.8, 0.1)
            max_tokens = st.number_input("Max Tokens", 1000, 8000, 4000, 500)
        
        # Generate Button
        st.divider()
        
        can_generate = (
            st.session_state.selected_problem is not None and
            len(selected_tool_objects) > 0 and
            system_prompt.strip() != ""
        )
        
        if st.button(
            "🚀 Generate Solutions",
            type="primary",
            use_container_width=True,
            disabled=not can_generate
        ):
            with st.spinner("🤔 Generating..."):
                try:
                    problem = st.session_state.selected_problem
                    
                    # Ensure all tools have a tool_id
                    for tool in selected_tool_objects:
                        if 'tool_id' not in tool and 'main_system' in tool:
                            tool['tool_id'] = tool['main_system'].lower().replace(' ', '_')
                    
                    results = st.session_state.claude_client.generate(
                        problem=problem.get('problem_text'),
                        problem_id=problem.get('problem_id', 'unknown'),
                        tools=selected_tool_objects,
                        system_prompt=system_prompt,
                        user_prompt_template=user_prompt,
                        temperature=temperature,
                        max_tokens=max_tokens
                    )
                    
                    # Track cost
                    st.session_state.cost_tracker.add_test(
                        results['metadata']['tokens'],
                        results['metadata']['cost_usd']
                    )
                    
                    # Save results
                    test_id = str(uuid.uuid4())
                    st.session_state.file_manager.save_test_result(
                        test_id=test_id,
                        results=results,
                        config={
                            'problem_id': problem.get('problem_id'),
                            'problem_text': problem.get('problem_text'),
                            'domain': problem.get('domain'),
                            'level': problem.get('level'),
                            'tools': [t.get('tool_id', t.get('main_system', 'unknown')) for t in selected_tool_objects],
                            'temperature': temperature,
                            'max_tokens': max_tokens
                        }
                    )
                    
                    st.session_state.current_results = results
                    st.session_state.current_test_id = test_id
                    
                    st.success("✅ Done!")
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
    
    with col2:
        st.subheader("Results")
        
        if st.session_state.current_results:
            render_results(st.session_state.current_results, st.session_state.current_test_id)
        else:
            st.info("👈 Configure and generate to see results")


def render_history_mode():
    """View past test runs"""
    st.subheader("📚 Test History")
    
    history = st.session_state.file_manager.load_test_history(limit=50)
    
    if not history:
        st.info("No history yet")
        return
    
    st.markdown(f"Showing {len(history)} recent tests")
    
    for idx, test in enumerate(history):
        timestamp = test.get('timestamp', 'Unknown')[:19]
        problem_id = test.get('config', {}).get('problem_id', 'Unknown')
        cost = test.get('metadata', {}).get('cost_usd', 0)
        tokens = test.get('metadata', {}).get('tokens', 0)
        
        with st.expander(f"**{idx+1}.** {timestamp} - {problem_id} (${cost:.4f}, {tokens:,} tokens)"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Config**")
                st.json(test.get('config', {}))
            
            with col2:
                st.markdown("**Metadata**")
                st.json(test.get('metadata', {}))
            
            st.markdown("---")
            st.markdown("**Solutions**")
            
            for sol_idx, sol in enumerate(test.get('results', {}).get('solutions', []), 1):
                st.markdown(f"**{sol_idx}. {sol.get('title')}**")
                st.markdown(sol.get('prompt'))
                st.caption(f"Tools: {', '.join(sol.get('tools_used', []))}")
                if sol_idx < len(test.get('results', {}).get('solutions', [])):
                    st.markdown("")

# Title
st.title(APP_TITLE)
st.markdown("*Test and iterate on prompt generation strategies - All data stored locally*")

# Sidebar
with st.sidebar:
    st.header("⚙️ Settings")
    
    mode = st.radio(
        "Mode",
        ["🚀 Generate New", "📚 View History"],
        index=0,
        label_visibility="collapsed"
    )
    
    st.divider()
    
    # Cost tracker
    st.header("💰 Session Costs")
    total_cost = st.session_state.cost_tracker.get_total_cost()
    total_tokens = st.session_state.cost_tracker.get_total_tokens()
    test_count = st.session_state.cost_tracker.get_test_count()
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Cost", f"${total_cost:.4f}")
    with col2:
        st.metric("Tests", test_count)
    
    st.metric("Tokens", f"{total_tokens:,}")
    
    if st.button("🔄 Reset", use_container_width=True):
        st.session_state.cost_tracker.reset()
        st.rerun()
    
    st.divider()
    
    # Data location info
    with st.expander("📁 Data Location"):
        st.markdown("""
        **Problems:** `data/problems/*.json`  
        **Tools:** `data/tools/*.json`  
        **Results:** `data/test_results/`  
        **Templates:** `data/templates/`
        """)

# Main content
if mode == "🚀 Generate New":
    render_generate_mode()
elif mode == "📚 View History":
    render_history_mode()