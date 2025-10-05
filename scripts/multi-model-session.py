#!/usr/bin/env python3
"""
Multi-Model Workshop Session Runner
No Docker, no MCP - just API calls and markdown files
"""

import os
from datetime import datetime
from pathlib import Path

# You'll need: pip install anthropic openai google-generativeai

def run_workshop_session(prompt: str, models: list = None):
    """
    Run a multi-model workshop session
    
    Args:
        prompt: The question/topic for all models
        models: List of model names to include (default: all available)
    """
    
    if models is None:
        models = ['claude', 'gpt', 'gemini']  # Add more as needed
    
    # Create session directory
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    session_dir = Path(f"sessions/session-{timestamp}")
    session_dir.mkdir(parents=True, exist_ok=True)
    
    # Save prompt
    (session_dir / "prompt.md").write_text(f"# Workshop Prompt\n\n{prompt}")
    
    responses = {}
    
    # Call each model (add your API keys as environment variables)
    if 'claude' in models and os.getenv('ANTHROPIC_API_KEY'):
        responses['claude'] = call_claude(prompt)
    
    if 'gpt' in models and os.getenv('OPENAI_API_KEY'):
        responses['gpt'] = call_gpt(prompt)
    
    if 'gemini' in models and os.getenv('GOOGLE_API_KEY'):
        responses['gemini'] = call_gemini(prompt)
    
    # Save each response
    for model_name, response in responses.items():
        filename = f"{model_name}.md"
        (session_dir / filename).write_text(
            f"# {model_name.title()} Response\n\n{response}"
        )
    
    # Create synthesis prompt (for next iteration)
    synthesis_prompt = create_synthesis_prompt(prompt, responses)
    (session_dir / "synthesis-prompt.md").write_text(synthesis_prompt)
    
    print(f"✅ Session complete: {session_dir}")
    print(f"📝 {len(responses)} model responses saved")
    print(f"🔄 Next: Run synthesis with generated prompt")
    
    return session_dir

def call_claude(prompt: str) -> str:
    """Call Claude API"""
    import anthropic
    client = anthropic.Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
    
    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=4000,
        messages=[{"role": "user", "content": prompt}]
    )
    
    return message.content[0].text

def call_gpt(prompt: str) -> str:
    """Call OpenAI API"""
    import openai
    client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )
    
    return response.choices[0].message.content

def call_gemini(prompt: str) -> str:
    """Call Gemini API"""
    import google.generativeai as genai
    genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))
    
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content(prompt)
    
    return response.text

def create_synthesis_prompt(original_prompt: str, responses: dict) -> str:
    """Create prompt for synthesis round"""
    prompt = f"# Synthesis Round\n\n"
    prompt += f"## Original Prompt\n{original_prompt}\n\n"
    prompt += f"## Model Responses\n\n"
    
    for model_name, response in responses.items():
        prompt += f"### {model_name.title()}\n{response[:500]}...\n\n"
    
    prompt += """## Synthesis Task
    Review all responses above and:
    1. Identify common themes
    2. Note unique insights from each model
    3. Synthesize into unified perspective
    4. Highlight remaining questions or tensions
    """
    
    return prompt

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python multi-model-session.py 'Your prompt here'")
        sys.exit(1)
    
    prompt = sys.argv[1]
    run_workshop_session(prompt)