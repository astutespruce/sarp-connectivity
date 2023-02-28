const { darken } = require('@theme-ui/color')

module.exports = {
  useColorSchemeMediaQuery: false,
  useLocalStorage: false,
  breakpoints: ['40em', '52em', '64em'],
  colors: {
    white: '#FFF',
    black: '#000',
    link: '#1891ac',
    text: '#333',
    primary: '#1891ac',
    secondary: '#1891ac',
    highlight: '#ee7d14',
    // used for filters and selected points
    accent: '#c51b8a',
    blue: {
      1: '#e0f2fb',
      2: '#cce5f2',
      5: '#1891ac', // primary
      8: '#1f5f8b',
      9: '#253b6e',
    },
    grey: {
      0: '#f8f9f9',
      1: '#ebedee',
      2: '#dee1e3',
      3: '#cfd3d6',
      4: '#bec4c8',
      5: '#acb4b9',
      6: '#97a1a7',
      7: '#7f8a93',
      8: '#5f6e78',
      9: '#374047',
    },
  },
  fonts: {
    body: 'Verdana,Geneva,sans-serif',
    heading: 'Verdana,Geneva,sans-serif',
  },
  fontSizes: [12, 14, 16, 18, 24, 32, 48, 64, 72, 112],
  fontWeights: {
    body: 400,
    heading: 700,
    bold: 700,
  },
  lineHeights: {
    body: 1.4,
    heading: 1.2,
  },
  layout: {
    container: {
      px: ['1rem', '1rem', '0px'],
      mt: '2rem',
      mb: '4rem',
    },
  },
  sizes: {
    container: '960px',
  },
  text: {
    default: {
      display: 'block', // fix for theme-ui v6 (div => span)
    },
    help: {
      display: 'block',
      color: 'grey.7',
      fontSize: 1,
    },
    error: {
      color: 'highlight',
      fontSize: '0.8rem',
      overflowWrap: 'normal',
    },
    paragraph: {
      fontSize: [2, 3],
      large: {
        fontSize: '1.25rem',
      },
    },
    heading: {
      fontFamily: 'heading',
      fontWeight: 'heading',
      lineHeight: 'heading',
      section: {
        fontSize: ['1.5rem', '2rem'],
        mb: '1.5rem',
      },
    },
    field: {
      display: 'block',
      wordBreak: 'break-word',
      overflow: 'hidden',
      '& >span:first-of-type': {
        fontWeight: 'bold',
        fontSize: 3,
        borderBottom: '1px solid',
        borderBottomColor: 'grey.2',
        mb: '0.25rem',
        pb: '0.25rem',
      },
      '& > span + span': {
        ml: '1rem',
      },
      '&:not(:first-of-type)': {
        mt: '1.5rem',
      },
    },
  },
  buttons: {
    primary: {
      cursor: 'pointer',
      color: '#FFF',
      bg: 'primary',
      '&:hover': {
        bg: darken('primary', 0.1),
      },
    },
    disabled: {
      cursor: 'not-allowed',
      color: '#FFF',
      bg: 'grey.4',
    },
    secondary: {
      cursor: 'pointer',
      color: '#FFF',
      bg: 'grey.9',
      '&:hover': {
        bg: darken('secondary', 0.1),
      },
    },
    'toggle-active': {
      flex: '1 1 auto',
      cursor: 'pointer',
      color: '#FFF',
      bg: 'primary',
      '&:hover': {
        bg: darken('primary', 0.1),
      },
    },
    'toggle-inactive': {
      flex: '1 1 auto',
      cursor: 'pointer',
      color: 'grey.9',
      bg: 'blue.1',
      '&:hover': {
        bg: darken('blue.1', 0.1),
      },
    },
    warning: {
      cursor: 'pointer',
      bg: '#ea1b00',
      color: '#FFF',
    },
    close: {
      flex: '0 0 auto',
      display: 'flex',
      lineHeight: 1.2,
      overflow: 'hidden',
      height: '1rem',
      width: '1rem',
      padding: '0.1rem',
      boxSizing: 'content-box',
      borderRadius: '1rem',
      alignItems: 'center',
      justifyContent: 'center',
      cursor: 'pointer',
      outline: 'none',
      color: '#FFF',
      bg: 'grey.5',
      '&:hover': { bg: 'grey.9' },
    },
  },
  boxes: {
    section: {
      '&:not(:first-of-type)': {
        mt: '6rem',
      },
    },
    step: {
      display: 'flex',
      flex: '0 0 auto',
      color: '#FFF',
      bg: 'grey.9',
      borderRadius: '5em',
      width: '2.25rem',
      height: '2.25rem',
      alignItems: 'center',
      justifyContent: 'center',
      fontWeight: 'bold',
      mr: '0.75rem',
      fontSize: '1.25rem',
    },
  },
  images: {
    basemap: {
      border: '2px solid #FFF',
      boxShadow: '0 1px 5px rgba(0,0,0,0.65)',
      m: 0,
      width: '64px',
      height: '64px',
      borderRadius: '64px',
      '&:hover': {
        boxShadow: '0 1px 5px rgba(0,0,0,1)',
        borderColor: '#EEE',
      },
    },
    'basemap-active': {
      border: '2px solid',
      borderColor: 'highlight',
      boxShadow: '0 1px 5px rgba(0,0,0,0.65)',
      m: 0,
      width: '64px',
      height: '64px',
      borderRadius: '64px',
      '&:hover': {
        boxShadow: '0 1px 5px rgba(0,0,0,1)',
        borderColor: '#EEE',
      },
    },
  },
  forms: {
    'input-default': {
      border: '1px solid',
      borderColor: 'grey.5',
      borderRadius: '0.25rem',
      outline: 'none',
      py: '0.25rem',
      px: '0.5rem',
      width: '100%',
      '&:focus': {
        borderColor: 'primary',
      },
    },
    'input-invalid': {
      borderWidth: '1px 1px 1px 0.5rem',
      borderStyle: 'solid',
      borderColor: 'highlight',
      borderRadius: '0.25rem',
      outline: 'none',
      py: '0.25rem',
      px: '0.5rem',
      width: '100%',
    },
    textarea: {
      fontFamily: 'body',
      border: '1px solid',
      borderColor: 'grey.5',
      borderRadius: '0.25rem',
      outline: 'none',
      py: '0.25rem',
      px: '0.5rem',
      width: '100%',
      '&:focus': {
        borderColor: 'primary',
      },
    },
    'textarea-invalid': {
      fontFamily: 'body',
      borderWidth: '1px 1px 1px 0.5rem',
      borderStyle: 'solid',
      borderColor: 'highlight',
      borderRadius: '0.25rem',
      outline: 'none',
      py: '0.25rem',
      px: '0.5rem',
      width: '100%',
    },
  },
  styles: {
    root: {
      height: '100vh',
      overflowX: 'hidden',
      overflowY: 'hidden',
      margin: 0,
      body: {
        margin: 0,
        height: '100%',
        width: '100%',
      },
      '#___gatsby': {
        height: '100%',
      },
      '#___gatsby > *': {
        height: '100%',
      },
      fontFamily: 'body',
      fontWeight: 'body',
      lineHeight: 'body',
      h1: {
        variant: 'text.heading',
        fontSize: [5, 6],
      },
      h2: {
        variant: 'text.heading',
        fontSize: [4, 5],
      },
      h3: {
        variant: 'text.heading',
        fontSize: [3, 4],
      },
      h4: {
        variant: 'text.heading',
        fontSize: [2, 3],
      },
      a: {
        color: 'primary',
        textDecoration: 'none',
      },
      'a:hover': {
        textDecoration: 'underline',
      },
      ul: {
        pl: '1.25em',
        'li + li': {
          mt: '0.5em',
        },
      },
    },
    hr: {
      borderBottom: '0.5rem solid',
      borderBottomColor: 'blue.8',
      my: '2rem',
    },
  },
}
