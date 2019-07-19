const breakpoints = ['40em', '52em', '64em']

const colors = {
  white: '#FFF',
  black: '#000',
  link: '#1891ac',
  primary: {
    100: '#e0f2fb',
    200: '#cce5f2',
    500: '#1891ac',
    800: '#1f5f8b',
    900: '#253b6e',
  },
  secondary: {
    500: '#1891ac',
    600: '#147b92',
  },
  highlight: {
    500: '#ee7d14',
  },
  grey: {
    0: '#f8f9f9',
    100: '#ebedee',
    200: '#dee1e3',
    300: '#cfd3d6',
    400: '#bec4c8',
    500: '#acb4b9',
    600: '#97a1a7',
    700: '#7f8a93',
    800: '#5f6e78',
    900: '#374047',
  },
  // used for filters and selected points
  accent: {
    500: '#c51b8a',
  },
}

const buttons = {
  default: {
    type: 'button',
    backgroundColor: colors.grey[900],
  },
  primary: {
    backgroundColor: colors.primary[500],
  },
  secondary: {
    backgroundColor: colors.secondary[500],
  },
  warning: {
    backgroundColor: '#ea1b00',
  },
  disabled: {
    backgroundColor: colors.grey[300],
  },
}

const theme = {
  breakpoints,
  colors,
  buttons,
}

export default theme
