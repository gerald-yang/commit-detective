import os
from typing import List, Dict, Any
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

class LLMService:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    async def analyze_commits(
        self,
        issue_description: str,
        commits: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Analyze commits using LLM to find potential fixes for the issue.
        """
        if not commits:
            return []

        # Prepare the prompt for the LLM
        prompt = self._create_analysis_prompt(issue_description, commits)
        
        try:
            # Get analysis from OpenAI
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a code analysis expert that helps identify which commits might fix a given issue."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3
            )
            
            # Parse the response and create analysis
            analysis = self._parse_llm_response(response.choices[0].message.content, commits)
            return analysis

        except Exception as e:
            raise Exception(f"Error analyzing commits: {str(e)}")

    def _create_analysis_prompt(self, issue_description: str, commits: List[Dict[str, Any]]) -> str:
        """
        Create a prompt for the LLM to analyze commits.
        """
        prompt = f"""Please analyze the following issue and commits to determine which commits might fix the issue.

Issue Description:
{issue_description}

Commits to analyze:
"""
        
        for commit in commits:
            prompt += f"""
Commit: {commit['hash']}
Message: {commit['message']}
Files changed: {', '.join(commit['files'])}
Diff:
{self._format_diff(commit['diff'])}

"""
        
        prompt += """
For each commit that might fix the issue:
1. Assign a relevance score from 0.0 to 1.0
2. Provide a brief explanation of why this commit might fix the issue
3. Format your response as a JSON array of objects with the following structure:
[
  {
    "commit_hash": "hash",
    "relevance_score": 0.0,
    "explanation": "explanation"
  }
]
"""
        return prompt

    def _format_diff(self, diff: Dict[str, str]) -> str:
        """
        Format the diff for better readability in the prompt.
        """
        formatted_diff = ""
        for file, changes in diff.items():
            formatted_diff += f"\nFile: {file}\n{changes}\n"
        return formatted_diff

    def _parse_llm_response(self, response: str, commits: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Parse the LLM response and combine it with commit information.
        """
        try:
            # Extract the JSON array from the response
            import json
            import re
            
            # Find JSON array in the response
            json_match = re.search(r'\[.*\]', response, re.DOTALL)
            if not json_match:
                raise Exception("Could not find JSON array in response")
            
            analysis = json.loads(json_match.group())
            
            # Combine analysis with commit information
            result = []
            for item in analysis:
                commit = next((c for c in commits if c['hash'] == item['commit_hash']), None)
                if commit:
                    result.append({
                        'commit_hash': commit['hash'],
                        'commit_message': commit['message'],
                        'relevance_score': item['relevance_score'],
                        'explanation': item['explanation']
                    })
            
            # Sort by relevance score
            result.sort(key=lambda x: x['relevance_score'], reverse=True)
            return result

        except Exception as e:
            raise Exception(f"Error parsing LLM response: {str(e)}") 