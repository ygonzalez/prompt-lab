import streamlit as st
from typing import List, Dict

def render_comparison():
    """Compare multiple test results side by side"""
    
    st.subheader("🔍 Compare Test Results")
    
    # Load history from file_manager
    if 'file_manager' not in st.session_state:
        st.error("File manager not initialized")
        return
    
    history = st.session_state.file_manager.load_test_history(limit=20)
    
    if len(history) < 2:
        st.info("Need at least 2 test results to compare")
        return
    
    # Test selection
    col1, col2 = st.columns(2)
    
    test_options = []
    for test in history:
        timestamp = test.get('timestamp', 'Unknown')[:19]
        problem_id = test.get('config', {}).get('problem_id', 'Unknown')
        cost = test.get('metadata', {}).get('cost_usd', 0)
        label = f"{timestamp} - {problem_id} (${cost:.4f})"
        test_options.append(label)
    
    with col1:
        selected_test1_idx = st.selectbox(
            "Select First Test",
            options=range(len(test_options)),
            format_func=lambda x: test_options[x]
        )
    
    with col2:
        selected_test2_idx = st.selectbox(
            "Select Second Test",
            options=range(len(test_options)),
            format_func=lambda x: test_options[x],
            index=1 if len(test_options) > 1 else 0
        )
    
    if selected_test1_idx == selected_test2_idx:
        st.warning("Please select different tests to compare")
        return
    
    test1 = history[selected_test1_idx]
    test2 = history[selected_test2_idx]
    
    st.divider()
    
    # Comparison tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Metrics", "🔧 Config", "💡 Solutions", "📈 Analysis"])
    
    with tab1:
        render_metrics_comparison(test1, test2)
    
    with tab2:
        render_config_comparison(test1, test2)
    
    with tab3:
        render_solutions_comparison(test1, test2)
    
    with tab4:
        render_analysis_comparison(test1, test2)

def render_metrics_comparison(test1: Dict, test2: Dict):
    """Compare metrics between two tests"""
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Test 1")
        metadata1 = test1.get('metadata', {})
        st.metric("Cost", f"${metadata1.get('cost_usd', 0):.4f}")
        st.metric("Tokens", f"{metadata1.get('tokens', 0):,}")
        st.metric("Latency", f"{metadata1.get('latency_ms', 0):.0f}ms")
        st.metric("Temperature", metadata1.get('temperature', 'N/A'))
    
    with col2:
        st.markdown("### Test 2")
        metadata2 = test2.get('metadata', {})
        
        # Calculate deltas
        cost_delta = metadata2.get('cost_usd', 0) - metadata1.get('cost_usd', 0)
        tokens_delta = metadata2.get('tokens', 0) - metadata1.get('tokens', 0)
        latency_delta = metadata2.get('latency_ms', 0) - metadata1.get('latency_ms', 0)
        
        st.metric("Cost", f"${metadata2.get('cost_usd', 0):.4f}", f"${cost_delta:+.4f}")
        st.metric("Tokens", f"{metadata2.get('tokens', 0):,}", f"{tokens_delta:+,}")
        st.metric("Latency", f"{metadata2.get('latency_ms', 0):.0f}ms", f"{latency_delta:+.0f}ms")
        st.metric("Temperature", metadata2.get('temperature', 'N/A'))

def render_config_comparison(test1: Dict, test2: Dict):
    """Compare configurations between two tests"""
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Test 1 Config")
        config1 = test1.get('config', {})
        st.markdown(f"**Problem ID:** {config1.get('problem_id', 'Unknown')}")
        st.markdown(f"**Domain:** {config1.get('domain', 'Unknown')}")
        st.markdown(f"**Level:** {config1.get('level', 'Unknown')}")
        st.markdown(f"**Tools:** {', '.join(config1.get('tools', []))}")
        
        with st.expander("Problem Text"):
            st.write(config1.get('problem_text', 'No text available'))
    
    with col2:
        st.markdown("### Test 2 Config")
        config2 = test2.get('config', {})
        st.markdown(f"**Problem ID:** {config2.get('problem_id', 'Unknown')}")
        st.markdown(f"**Domain:** {config2.get('domain', 'Unknown')}")
        st.markdown(f"**Level:** {config2.get('level', 'Unknown')}")
        st.markdown(f"**Tools:** {', '.join(config2.get('tools', []))}")
        
        with st.expander("Problem Text"):
            st.write(config2.get('problem_text', 'No text available'))

def render_solutions_comparison(test1: Dict, test2: Dict):
    """Compare solutions between two tests"""
    
    solutions1 = test1.get('results', {}).get('solutions', [])
    solutions2 = test2.get('results', {}).get('solutions', [])
    
    # Side-by-side solution comparison
    for idx in range(max(len(solutions1), len(solutions2))):
        st.markdown(f"### Solution {idx + 1}")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if idx < len(solutions1):
                sol = solutions1[idx]
                st.markdown(f"**{sol.get('title', 'Untitled')}**")
                st.info(sol.get('prompt', 'No prompt'))
                if sol.get('tools_used'):
                    st.caption(f"Tools: {', '.join(sol['tools_used'])}")
                if sol.get('tags'):
                    st.caption(f"Tags: {', '.join(sol['tags'])}")
            else:
                st.info("No solution at this index")
        
        with col2:
            if idx < len(solutions2):
                sol = solutions2[idx]
                st.markdown(f"**{sol.get('title', 'Untitled')}**")
                st.info(sol.get('prompt', 'No prompt'))
                if sol.get('tools_used'):
                    st.caption(f"Tools: {', '.join(sol['tools_used'])}")
                if sol.get('tags'):
                    st.caption(f"Tags: {', '.join(sol['tags'])}")
            else:
                st.info("No solution at this index")
        
        st.divider()

def render_analysis_comparison(test1: Dict, test2: Dict):
    """Analyze differences between two tests"""
    
    st.markdown("### Comparative Analysis")
    
    solutions1 = test1.get('results', {}).get('solutions', [])
    solutions2 = test2.get('results', {}).get('solutions', [])
    
    # Tool usage analysis
    tools1 = set()
    tools2 = set()
    
    for sol in solutions1:
        tools1.update(sol.get('tools_used', []))
    
    for sol in solutions2:
        tools2.update(sol.get('tools_used', []))
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**Tools in Test 1 Only:**")
        unique_tools1 = tools1 - tools2
        if unique_tools1:
            for tool in unique_tools1:
                st.write(f"• {tool}")
        else:
            st.info("None")
    
    with col2:
        st.markdown("**Common Tools:**")
        common_tools = tools1 & tools2
        if common_tools:
            for tool in common_tools:
                st.write(f"• {tool}")
        else:
            st.info("None")
    
    with col3:
        st.markdown("**Tools in Test 2 Only:**")
        unique_tools2 = tools2 - tools1
        if unique_tools2:
            for tool in unique_tools2:
                st.write(f"• {tool}")
        else:
            st.info("None")
    
    st.divider()
    
    # Tag analysis
    tags1 = []
    tags2 = []
    
    for sol in solutions1:
        tags1.extend(sol.get('tags', []))
    
    for sol in solutions2:
        tags2.extend(sol.get('tags', []))
    
    st.markdown("### Tag Distribution")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Test 1 Tags:**")
        if tags1:
            tag_freq1 = {}
            for tag in tags1:
                tag_freq1[tag] = tag_freq1.get(tag, 0) + 1
            for tag, count in sorted(tag_freq1.items(), key=lambda x: x[1], reverse=True):
                st.write(f"• {tag}: {count}")
        else:
            st.info("No tags")
    
    with col2:
        st.markdown("**Test 2 Tags:**")
        if tags2:
            tag_freq2 = {}
            for tag in tags2:
                tag_freq2[tag] = tag_freq2.get(tag, 0) + 1
            for tag, count in sorted(tag_freq2.items(), key=lambda x: x[1], reverse=True):
                st.write(f"• {tag}: {count}")
        else:
            st.info("No tags")