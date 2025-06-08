# Commit Detective

A tool that helps developers identify which commits might fix their issues by analyzing commit history and using LLM to match issue descriptions with commit changes.

## Features

- Submit detailed issue descriptions
- Specify relevant source files
- Provide current commit ID
- Get a list of potential fix commits
- AI-powered commit analysis
- Option to save commits to file without LLM analysis

## Project Structure

```
commit-detective/
├── backend/           # FastAPI backend
│   ├── app/
│   │   ├── api/      # API endpoints
│   │   ├── core/     # Core functionality
│   │   ├── models/   # Data models
│   │   └── services/ # Business logic
│   └── tests/        # Backend tests
├── frontend/         # React frontend
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   └── services/
│   └── public/
└── docs/            # Documentation
```

## Setup

### Backend

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
cd backend
pip install -r requirements.txt
```

3. Run the development server:
```bash
uvicorn app.main:app --reload
```

### Frontend

1. Install dependencies:
```bash
cd frontend
npm install
```

2. Run the development server:
```bash
npm start
```

3. If react-script is not found, install it directly and run step 2
```bash
npm install react-scripts --save-dev
```

## Environment Variables

Create a `.env` file in the backend directory with the following variables:

```
OPENAI_API_KEY=your_openai_api_key  # Only required if using LLM analysis
```

## Usage

1. **Full Analysis Mode**
   - Fill in the issue description
   - Specify source files
   - Provide current commit hash
   - Optionally provide repository URL
   - Click "Analyze Commits" to get AI-powered analysis

2. **Save-Only Mode**
   - Check "Save commits to file only" checkbox
   - Specify source files
   - Provide current commit hash
   - Optionally provide repository URL
   - Click "Analyze Commits" to save commits to a JSON file
   - No OpenAI API key required in this mode

## License

MIT
