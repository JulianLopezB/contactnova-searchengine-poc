import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import Article from './Article';
import { 
    Container, TextField, Button, Select, MenuItem, FormControl, 
    InputLabel, Typography, Box, CircularProgress, Grid, List, ListItem, ListItemText,
    Switch, FormControlLabel
} from '@mui/material';
import SearchIcon from '@mui/icons-material/Search';
import { styled, ThemeProvider } from '@mui/material/styles';
import { motion } from 'framer-motion';
import { theme } from '../theme';
import logo from '../logo.png';

const StyledButton = styled(Button)(({ theme }) => ({
    minWidth: '48px',
    width: '48px',
    height: '48px',
    borderRadius: '50%',
    padding: 0,
    color: theme.palette.primary.contrastText,
    backgroundColor: theme.palette.primary.main,
    '&:hover': {
        backgroundColor: theme.palette.primary.dark,
    },
    '&:disabled': {
        backgroundColor: theme.palette.action.disabledBackground,
    },
}));

const MotionListItem = motion(ListItem);

function Search() {
    const [query, setQuery] = useState('');
    const [results, setResults] = useState([]);
    const [categories, setCategories] = useState([]);
    const [selectedCategory, setSelectedCategory] = useState('');
    const [selectedArticle, setSelectedArticle] = useState(null);
    const [loading, setLoading] = useState(false);
    const [embeddingType, setEmbeddingType] = useState('openai');
    const [useLLMValidation, setUseLLMValidation] = useState(false);

    const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8080';

    const fetchCategories = useCallback(async () => {
        try {
            const response = await axios.get(`${API_BASE_URL}/categories`);
            setCategories(response.data);
        } catch (error) {
            console.error("Error fetching categories", error);
        }
    }, [API_BASE_URL]);

    useEffect(() => {
        fetchCategories();
    }, [fetchCategories]);

    const handleSearch = async () => {
        if (!query.trim()) {
            setResults([]);
            setSelectedArticle(null);
            return;
        }

        setLoading(true);
        try {
            const endpoint = useLLMValidation ? 'search-with-ai-validation' : 'search';
            const response = await axios.get(`${API_BASE_URL}/${endpoint}`, {
                params: { 
                    query, 
                    category: selectedCategory, 
                    embedding_type: embeddingType
                }
            });
            setResults(response.data);
            setSelectedArticle(null);
        } catch (error) {
            console.error("Error fetching search results", error);
            setResults([]);
        } finally {
            setLoading(false);
        }
    };

    const handleArticleClick = async (articleId) => {
        try {
            const response = await axios.get(`${API_BASE_URL}/article/${articleId}`, {
                params: { embedding_type: embeddingType }
            });
            setSelectedArticle(response.data);
        } catch (error) {
            console.error("Error fetching article details", error);
        }
    };

    return (
        <ThemeProvider theme={theme}>
            <Container maxWidth="lg" sx={{ backgroundColor: 'background.default', minHeight: 'calc(100vh - 64px)', py: 4 }}>
                <Box sx={{ display: 'flex', justifyContent: 'center', mb: 6, p: 2, backgroundColor: 'rgba(255, 255, 255, 0.8)', borderRadius: '12px', boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)' }}>
                    <img src={logo} alt="ContactNova Logo" style={{ height: '100px', width: 'auto', maxWidth: '100%' }} />
                </Box>
                <Box sx={{ display: 'flex', gap: 2, mb: 4 }}>
                    <FormControl fullWidth>
                        <InputLabel id="category-select-label">Grupo</InputLabel>
                        <Select
                            labelId="category-select-label"
                            value={selectedCategory}
                            label="Grupo"
                            onChange={(e) => setSelectedCategory(e.target.value)}
                        >
                            <MenuItem value="">Todos los grupos</MenuItem>
                            {categories.map((category, index) => (
                                <MenuItem key={index} value={category}>{category}</MenuItem>
                            ))}
                        </Select>
                    </FormControl>
                    <FormControl fullWidth>
                        <InputLabel id="embedding-type-label">Embedding Type</InputLabel>
                        <Select
                            labelId="embedding-type-label"
                            value={embeddingType}
                            label="Embedding Type"
                            onChange={(e) => setEmbeddingType(e.target.value)}
                        >
                            {/* <MenuItem value="openai">OpenAI</MenuItem> */}
                            <MenuItem value="openai-large">OpenAI-Large</MenuItem>
                            <MenuItem value="fasttext">FastText</MenuItem>
                        </Select>
                    </FormControl>
                    <TextField
                        fullWidth
                        variant="outlined"
                        value={query}
                        onChange={(e) => setQuery(e.target.value)}
                        placeholder="Enter your search query"
                        onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
                    />
                    <StyledButton 
                        onClick={handleSearch} 
                        disabled={loading}
                        aria-label="Search"
                    >
                        <SearchIcon />
                    </StyledButton>
                </Box>
                <Box sx={{ display: 'flex', justifyContent: 'flex-end', mb: 2 }}>
                    <FormControlLabel
                        control={
                            <Switch
                                checked={useLLMValidation}
                                onChange={(e) => setUseLLMValidation(e.target.checked)}
                                color="primary"
                            />
                        }
                        label="LLM Validation"
                    />
                </Box>
                {loading && (
                    <Box sx={{ display: 'flex', justifyContent: 'center', my: 4 }}>
                        <CircularProgress />
                    </Box>
                )}
                {!loading && (
                    <Grid container spacing={3}>
                        <Grid item xs={4}>
                            <Typography variant="h5" component="h2" gutterBottom sx={{ color: 'secondary.main' }}>
                                Resultados
                            </Typography>
                            {results.length > 0 ? (
                                <List>
                                    {results.map((result, index) => (
                                        <MotionListItem 
                                            key={index} 
                                            button 
                                            onClick={() => handleArticleClick(result.id)}
                                            selected={selectedArticle && selectedArticle.id === result.id}
                                            initial={{ opacity: 0, x: -20 }}
                                            animate={{ opacity: 1, x: 0 }}
                                            transition={{ duration: 0.3, delay: index * 0.1 }}
                                            sx={{
                                                mb: 1,
                                                borderRadius: '8px',
                                                '&:hover': {
                                                    backgroundColor: 'rgba(255, 0, 0, 0.1)',
                                                },
                                                '&.Mui-selected': {
                                                    backgroundColor: 'rgba(255, 0, 0, 0.2)',
                                                },
                                            }}
                                        >
                                            <ListItemText 
                                                primary={result.pregunta}
                                                secondary={`${result.grupo} - ${result.tema}`}
                                                primaryTypographyProps={{ fontWeight: 'bold' }}
                                            />
                                        </MotionListItem>
                                    ))}
                                </List>
                            ) : (
                                <Typography variant="body1" sx={{ mt: 2 }}>
                                    {query.trim() ? "No se encontraron resultados." : "Ingrese una consulta para buscar."}
                                </Typography>
                            )}
                        </Grid>
                        <Grid item xs={8}>
                            {selectedArticle && <Article article={selectedArticle} />}
                        </Grid>
                    </Grid>
                )}
            </Container>
        </ThemeProvider>
    );
}

export default Search;