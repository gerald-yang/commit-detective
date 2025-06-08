from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from app.services.git_service import GitService
from app.services.llm_service import LLMService
import json
from datetime import datetime

router = APIRouter()
git_service = GitService()
llm_service = LLMService()

class IssueRequest(BaseModel):
    description: str
    source_files: List[str]
    current_commit: str
    repository_url: Optional[str] = None
    save_only: bool = False

class CommitAnalysis(BaseModel):
    commit_hash: str
    commit_message: str
    relevance_score: float
    explanation: str

@router.post("/analyze", response_model=List[CommitAnalysis])
async def analyze_issue(request: IssueRequest):
    try:
        # Get commits after the current commit
        commits = await git_service.get_commits_after(
            request.current_commit,
            request.source_files,
            request.repository_url
        )
        
        if request.save_only:
            # Save commits to a file
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"commits_{timestamp}.json"
            
            # Format commits for saving
            commits_to_save = [{
                'hash': commit['hash'],
                'message': commit['message'],
                'author': commit['author'],
                'date': commit['date'],
                'files': commit['files']
            } for commit in commits]
            
            with open(filename, 'w') as f:
                json.dump(commits_to_save, f, indent=2)
            
            return [{
                'commit_hash': commit['hash'],
                'commit_message': commit['message'],
                'relevance_score': 1.0,
                'explanation': f"Saved {len(commits)} commits to {filename}"
            }]
        
        # Analyze commits using LLM
        analysis = await llm_service.analyze_commits(
            request.description,
            commits
        )
        
        return analysis
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def health_check():
    return {"status": "healthy"} 