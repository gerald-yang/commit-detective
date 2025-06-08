import React, { useState } from 'react';
import {
  Container,
  Paper,
  Typography,
  TextField,
  Button,
  Box,
  CircularProgress,
  List,
  ListItem,
  ListItemText,
  Divider,
  Chip,
  FormControlLabel,
  Checkbox,
} from '@mui/material';
import axios from 'axios';

function App() {
  const [formData, setFormData] = useState({
    description: '',
    sourceFiles: '',
    currentCommit: '',
    repositoryUrl: '',
    saveOnly: false,
  });
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState([]);
  const [error, setError] = useState('');

  const handleInputChange = (e) => {
    const { name, value, checked } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: e.target.type === 'checkbox' ? checked : value,
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setResults([]);

    try {
      const response = await axios.post('http://localhost:8000/api/analyze', {
        description: formData.description,
        source_files: formData.sourceFiles.split(',').map((file) => file.trim()),
        current_commit: formData.currentCommit,
        repository_url: formData.repositoryUrl || undefined,
        save_only: formData.saveOnly,
      });

      setResults(response.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'An error occurred while analyzing commits');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Container maxWidth="md" sx={{ py: 4 }}>
      <Typography variant="h3" component="h1" gutterBottom align="center">
        Commit Detective
      </Typography>

      <Paper elevation={3} sx={{ p: 3, mb: 4 }}>
        <form onSubmit={handleSubmit}>
          <TextField
            fullWidth
            multiline
            rows={4}
            label="Issue Description"
            name="description"
            value={formData.description}
            onChange={handleInputChange}
            margin="normal"
            required={!formData.saveOnly}
            disabled={formData.saveOnly}
          />

          <TextField
            fullWidth
            label="Source Files (comma-separated)"
            name="sourceFiles"
            value={formData.sourceFiles}
            onChange={handleInputChange}
            margin="normal"
            required
            helperText="Enter file paths separated by commas"
          />

          <TextField
            fullWidth
            label="Current Commit Hash"
            name="currentCommit"
            value={formData.currentCommit}
            onChange={handleInputChange}
            margin="normal"
            required
          />

          <TextField
            fullWidth
            label="Repository URL (optional)"
            name="repositoryUrl"
            value={formData.repositoryUrl}
            onChange={handleInputChange}
            margin="normal"
            helperText="Leave empty to use current directory"
          />

          <FormControlLabel
            control={
              <Checkbox
                name="saveOnly"
                checked={formData.saveOnly}
                onChange={handleInputChange}
              />
            }
            label="Save commits to file only (no LLM analysis)"
            sx={{ mt: 2 }}
          />

          <Box sx={{ mt: 2, display: 'flex', justifyContent: 'center' }}>
            <Button
              type="submit"
              variant="contained"
              color="primary"
              disabled={loading}
              size="large"
            >
              {loading ? <CircularProgress size={24} /> : 'Analyze Commits'}
            </Button>
          </Box>
        </form>
      </Paper>

      {error && (
        <Paper elevation={3} sx={{ p: 3, mb: 4, bgcolor: '#ffebee' }}>
          <Typography color="error">{error}</Typography>
        </Paper>
      )}

      {results.length > 0 && (
        <Paper elevation={3} sx={{ p: 3 }}>
          <Typography variant="h5" gutterBottom>
            {formData.saveOnly ? 'Saved Commits' : 'Potential Fix Commits'}
          </Typography>
          <List>
            {results.map((result, index) => (
              <React.Fragment key={result.commit_hash}>
                <ListItem alignItems="flex-start">
                  <ListItemText
                    primary={
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <Typography variant="subtitle1" component="span">
                          {result.commit_hash}
                        </Typography>
                        {!formData.saveOnly && (
                          <Chip
                            label={`${Math.round(result.relevance_score * 100)}% match`}
                            color={result.relevance_score > 0.7 ? 'success' : 'primary'}
                            size="small"
                          />
                        )}
                      </Box>
                    }
                    secondary={
                      <>
                        <Typography
                          component="span"
                          variant="body2"
                          color="text.primary"
                          sx={{ display: 'block', mt: 1 }}
                        >
                          {result.commit_message}
                        </Typography>
                        <Typography
                          component="span"
                          variant="body2"
                          color="text.secondary"
                          sx={{ display: 'block', mt: 1 }}
                        >
                          {result.explanation}
                        </Typography>
                      </>
                    }
                  />
                </ListItem>
                {index < results.length - 1 && <Divider />}
              </React.Fragment>
            ))}
          </List>
        </Paper>
      )}
    </Container>
  );
}

export default App; 