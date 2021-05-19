const { lighten, darken } = require('@theme-ui/color')

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

    // primary: {
    //   100: '#e0f2fb',
    //   200: '#cce5f2',
    //   500: '#1891ac',
    //   800: '#1f5f8b',
    //   900: '#253b6e',
    // },

    blue: {
      1: '#e0f2fb',
      2: '#cce5f2',
      5: '#1891ac', // primary
      8: '#1f5f8b',
      9: '#253b6e',
    },

    // secondary: {
    //   500: '#1891ac',
    //   600: '#147b92',
    // },
    // highlight: {
    //   500: '#ee7d14',
    // },
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
    // accent: {
    //   500: '#c51b8a',
    // },
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
      maxWidth: '960px',
    },
    // sidebar: {
    //   width: ['100%', '468px'],
    //   borderRightWidth: ['0px', '1px'],
    //   borderRightColor: 'grey.8',
    // },
  },
  text: {
    default: {
      display: 'block', // fix for theme-ui v6 (div => span)
    },
    help: {
      display: 'block',
      color: 'grey.7',
    },
    heading: {
      fontFamily: 'heading',
      fontWeight: 'heading',
      lineHeight: 'heading',
      //   bar: {
      //     textAlign: 'center',
      //     p: '1rem',
      //     mb: '2rem',
      //     bg: 'grey.1',
      //     borderBottom: '1px solid',
      //     borderTop: '1px solid',
      //     borderBottomColor: 'grey.3',
      //     borderTopColor: 'grey.3',
      //   },
      //   block: {
      //     fontSize: [3, 4],
      //     pb: '0.5rem',
      //   },
    },
    // blockHeading: {
    //   fontFamily: 'heading',
    //   fontWeight: 'heading',
    //   lineHeight: 'heading',
    //   fontSize: [3, 4],
    //   pb: '0.5rem',
    // },
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
  //   alerts: {
  //     error: {
  //       color: '#FFF',
  //       bg: 'error',
  //     },
  //   },
  buttons: {
    primary: {
      cursor: 'pointer',
      bg: 'primary',
      '&:hover': {
        bg: darken('primary', 0.1),
      },
    },
    secondary: {
      cursor: 'pointer',
      color: 'grey.9',
      bg: 'secondary',
      '&:hover': {
        bg: darken('secondary', 0.1),
      },
    },
    warning: {
      cursor: 'pointer',
      color: '#ea1b00',
    },
    disabled: {
      bg: 'grey.3',
    },
    //   accent: {
    //     cursor: 'pointer',
    //     color: '#FFF',
    //     bg: 'accent',
    //   },
    close: {
      cursor: 'pointer',
      outline: 'none',
      background: 'none',
      color: 'grey.5',
      '&:hover': { color: 'grey.9' },
    },
  },
  grids: {
    thirds: {
      gap: 3,
    },
    half: {
      gap: 5,
    },
  },
  //   boxes: {
  //     section: {
  //       mt: '6rem',
  //       pt: '3rem',
  //       borderTop: '0.5rem solid',
  //       borderTopColor: 'grey.9',
  //     },
  //   },
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
      p: {
        fontSize: [2, 3],
      },
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
        margin: 0,
        pl: '1.25em',
        'li + li': {
          mt: '0.25em',
        },
      },
    },
    // hr: {
    //   color: 'grey.2',
    //   my: '2rem',
    //   space: {
    //     color: 'grey.2',
    //     my: '4rem',
    //   },
    //   wide: {
    //     height: '0.5rem',
    //     bg: 'grey.9',
    //     borderBottom: 'none',
    //   },
    // },
    // also used for filter bars
    progress: {
      color: 'primary',
      bg: 'grey.2',
      height: '1rem',
    },
  },
}
