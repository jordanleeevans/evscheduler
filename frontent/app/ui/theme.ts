import { createTheme } from "@mui/material/styles";

// Neo-brutalism soft: warm palette, offset solid shadows, visible borders,
// bold type — but muted tones instead of harsh black-on-white.

const BORDER_COLOR = "#2b2b2b";
const SHADOW = `4px 4px 0px ${BORDER_COLOR}`;

const theme = createTheme({
  palette: {
    background: {
      default: "#faf7f2", // warm off-white
      paper: "#fff8ee", // slightly warmer card surface
    },
    text: {
      primary: "#2b2b2b",
      secondary: "#5c5346",
    },
    primary: {
      main: "#e8a838", // dusty amber
      contrastText: "#2b2b2b",
    },
    secondary: {
      main: "#a8c5a0", // sage green
      contrastText: "#2b2b2b",
    },
    error: {
      main: "#d94f3d",
    },
  },

  typography: {
    fontFamily: "Roboto, sans-serif",
    h1: { fontWeight: 800 },
    h2: { fontWeight: 800 },
    h3: { fontWeight: 700 },
    h4: { fontWeight: 700 },
    h5: { fontWeight: 600 },
    h6: { fontWeight: 600 },
  },

  shape: {
    // Slightly rounded — "soft" in soft-brutalism
    borderRadius: 6,
  },

  components: {
    MuiCssBaseline: {
      styleOverrides: {
        body: {
          backgroundColor: "#faf7f2",
        },
      },
    },

    // Cards get the signature offset shadow + visible border
    MuiCard: {
      styleOverrides: {
        root: {
          border: `2px solid ${BORDER_COLOR}`,
          boxShadow: SHADOW,
          transition: "box-shadow 0.15s ease, transform 0.15s ease",
          "&:hover": {
            boxShadow: `6px 6px 0px ${BORDER_COLOR}`,
            transform: "translate(-1px, -1px)",
          },
        },
      },
    },

    // Contained buttons: bordered, offset shadow, no MUI elevation ripple effect
    MuiButton: {
      styleOverrides: {
        containedPrimary: {
          border: `2px solid ${BORDER_COLOR}`,
          boxShadow: SHADOW,
          "&:hover": {
            boxShadow: `6px 6px 0px ${BORDER_COLOR}`,
            transform: "translate(-1px, -1px)",
          },
          "&:active": {
            boxShadow: "2px 2px 0px #2b2b2b",
            transform: "translate(1px, 1px)",
          },
        },
      },
      defaultProps: {
        disableElevation: true,
      },
    },

    // Text fields: flat border, no floating label shadow
    MuiOutlinedInput: {
      styleOverrides: {
        root: {
          borderRadius: 6,
          "& .MuiOutlinedInput-notchedOutline": {
            borderColor: BORDER_COLOR,
            borderWidth: 2,
          },
        },
      },
    },

    // Paper surfaces (dialogs, popovers, etc.)
    MuiPaper: {
      styleOverrides: {
        root: {
          backgroundImage: "none",
        },
        elevation1: {
          boxShadow: SHADOW,
          border: `2px solid ${BORDER_COLOR}`,
        },
      },
    },
  },
});

export default theme;
