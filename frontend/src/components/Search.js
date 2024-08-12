import React, { useState, useEffect } from 'react';
import axios from 'axios';
import Article from './Article';
import { 
    Container, TextField, Button, Select, MenuItem, FormControl, 
    InputLabel, Typography, Box, CircularProgress, Grid, List, ListItem, ListItemText
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

    useEffect(() => {
        fetchCategories();
    }, []);

    const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8080';

    const fetchCategories = async () => {
        try {
            const response = await axios.get(`${API_BASE_URL}/categories`);
            setCategories(response.data);
        } catch (error) {
            console.error("Error fetching categories", error);
        }
    };

    const handleSearch = async () => {
        if (!query.trim()) {
            // Handle empty query
            setResults([]);
            setSelectedArticle(null);
            return;
        }

        setLoading(true);
        try {
            const response = await axios.get(`${API_BASE_URL}/search`, {
                params: { query, category: selectedCategory }
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
            const response = await axios.get(`${API_BASE_URL}/article/${articleId}`);
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