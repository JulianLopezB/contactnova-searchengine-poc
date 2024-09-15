import React from 'react';
import { Typography, Paper, Box, Chip } from '@mui/material';
import { motion } from 'framer-motion';

const MotionPaper = motion(Paper);

function Article({ article }) {
    return (
        <MotionPaper
            elevation={2}
            sx={{
                p: 3,
                height: '100%',
                overflow: 'auto',
                backgroundColor: 'background.paper',
                borderRadius: (theme) => theme.shape.borderRadius,
            }}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
        >
            <Typography variant="h4" component="h2" gutterBottom sx={{ color: 'text.primary' }}>
                {article.pregunta}
            </Typography>
            <Box sx={{ display: 'flex', gap: 2, mb: 2 }}>
                <Chip label={`Grupo: ${article.grupo}`} color="primary" variant="outlined" />
                <Chip label={`Tema: ${article.tema}`} color="secondary" variant="outlined" />
            </Box>
            <Box sx={{ mt: 2 }}>
                <Typography component="div" dangerouslySetInnerHTML={{ __html: article.respuesta }} />
            </Box>
        </MotionPaper>
    );
}

export default Article;