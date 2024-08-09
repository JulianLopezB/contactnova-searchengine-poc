import { createTheme } from '@mui/material/styles';

export const theme = createTheme({
  palette: {
    primary: {
      main: '#FF0000', // Red from the logo
    },
    secondary: {
      main: '#000000', // Black from the logo
    },
    background: {
      default: '#F5F5F5', // Light gray background
      paper: '#FFFFFF',
    },
    text: {
      primary: '#333333',
      secondary: '#666666',
    },
  },
  typography: {
    fontFamily: 'Roboto, Arial, sans-serif',
  },
  shape: {
    borderRadius: 8,
  },
});