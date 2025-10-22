import streamlit as st
import json
from typing import Dict, List

def render_results(results: Dict, test_id: str):
    """Display generated solutions with formatting and export options"""
    
    # Show metadata
    metadata = results.get('metadata', {})
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Cost", f"${metadata.get('cost_usd', 0):.4f}")
    with col2:
        st.metric("Tokens", f"{metadata.get('tokens', 0):,}")
    with col3:
        st.metric("Latency", f"{metadata.get('latency_ms', 0):.0f}ms")
    with col4:
        st.metric("Model", metadata.get('model', 'Unknown').split('-')[-1])
    
    st.divider()
    
    # Display solutions
    solutions = results.get('solutions', [])
    
    if not solutions:
        st.warning("No solutions generated")
        return
    
    # Tabs for different views
    tab1, tab2, tab3 = st.tabs(["📝 Solutions", "🏷️ Tags Analysis", "📤 Export"])
    
    with tab1:
        for idx, solution in enumerate(solutions, 1):
            with st.expander(f"**Solution {idx}: {solution.get('title', 'Untitled')}**", expanded=(idx==1)):
                # Main prompt
                st.markdown("**Conversation Starter:**")
                st.info(solution.get('prompt', 'No prompt available'))
                
                # Tools used
                tools_used = solution.get('tools_used', [])
                if tools_used:
                    st.markdown("**Tools Referenced:**")
                    tool_badges = " ".join([f"`{tool}`" for tool in tools_used])
                    st.markdown(tool_badges)
                
                # Tags
                tags = solution.get('tags', [])
                if tags:
                    st.markdown("**Tags:**")
                    tag_badges = " ".join([f"🏷️ {tag}" for tag in tags])
                    st.caption(tag_badges)
                
                # Copy button
                if st.button(f"📋 Copy Prompt", key=f"copy_{test_id}_{idx}"):
                    st.code(solution.get('prompt', ''), language=None)
                    st.success("✅ Ready to paste!")
    
    with tab2:
        # Analyze tags across all solutions
        all_tags = []
        tool_usage = {}
        
        for solution in solutions:
            all_tags.extend(solution.get('tags', []))
            for tool in solution.get('tools_used', []):
                tool_usage[tool] = tool_usage.get(tool, 0) + 1
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Tag Frequency:**")
            if all_tags:
                tag_freq = {}
                for tag in all_tags:
                    tag_freq[tag] = tag_freq.get(tag, 0) + 1
                
                for tag, count in sorted(tag_freq.items(), key=lambda x: x[1], reverse=True):
                    st.write(f"• {tag}: {count} occurrences")
            else:
                st.info("No tags found")
        
        with col2:
            st.markdown("**Tool Usage:**")
            if tool_usage:
                for tool, count in sorted(tool_usage.items(), key=lambda x: x[1], reverse=True):
                    percentage = (count / len(solutions)) * 100
                    st.write(f"• {tool}: {count} solutions ({percentage:.0f}%)")
            else:
                st.info("No tools referenced")
    
    with tab3:
        st.markdown("**Export Options**")
        
        # JSON export
        export_data = {
            "test_id": test_id,
            "metadata": metadata,
            "solutions": solutions
        }
        
        json_str = json.dumps(export_data, indent=2)
        
        st.download_button(
            label="📥 Download JSON",
            data=json_str,
            file_name=f"solutions_{test_id}.json",
            mime="application/json"
        )
        
        # Text export
        text_export = generate_text_export(solutions, metadata)
        
        st.download_button(
            label="📥 Download Text",
            data=text_export,
            file_name=f"solutions_{test_id}.txt",
            mime="text/plain"
        )
        
        # Preview
        with st.expander("Preview Export"):
            st.code(json_str[:1000] + "...", language="json")

def generate_text_export(solutions: List[Dict], metadata: Dict) -> str:
    """Generate a readable text export of solutions"""
    
    text = "=" * 60 + "\n"
    text += "PROMPT LAB SOLUTIONS EXPORT\n"
    text += "=" * 60 + "\n\n"
    
    # Metadata
    text += "METADATA:\n"
    text += f"- Model: {metadata.get('model', 'Unknown')}\n"
    text += f"- Temperature: {metadata.get('temperature', 'Unknown')}\n"
    text += f"- Cost: ${metadata.get('cost_usd', 0):.4f}\n"
    text += f"- Tokens: {metadata.get('tokens', 0):,}\n"
    text += f"- Latency: {metadata.get('latency_ms', 0):.0f}ms\n"
    text += "\n" + "-" * 60 + "\n\n"
    
    # Solutions
    text += "SOLUTIONS:\n\n"
    
    for idx, solution in enumerate(solutions, 1):
        text += f"Solution {idx}: {solution.get('title', 'Untitled')}\n"
        text += "=" * 40 + "\n\n"
        
        text += "Prompt:\n"
        text += solution.get('prompt', 'No prompt available') + "\n\n"
        
        if solution.get('tools_used'):
            text += f"Tools: {', '.join(solution['tools_used'])}\n"
        
        if solution.get('tags'):
            text += f"Tags: {', '.join(solution['tags'])}\n"
        
        text += "\n" + "-" * 40 + "\n\n"
    
    return text