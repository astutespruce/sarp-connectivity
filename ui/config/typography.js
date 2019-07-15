import Typography from 'typography'

import { theme } from 'style'

const typographyTheme = {
  baseFontSize: '16px',
  baseLineHeight: 1.4,
  headerFontFamily: ['Verdana', 'Geneva', 'sans-serif'],
  bodyFontFamily: ['Verdana', 'Geneva', 'sans-serif'],
  bodyWeight: 400,
  headerWeight: 700,
  boldWeight: 700,
  scaleRatio: 1.4,
  overrideThemeStyles: () => ({
    html: {
      height: '100%',
      overflowY: 'hidden',
    },
    body: {
      height: '100%',
      width: '100%',
    },
    // Set height on containing notes to 100% so that full screen map layouts work
    '#___gatsby': {
      height: '100%',
    },
    '#___gatsby > *': {
      height: '100%',
    },
    button: {
      outline: 'none',
      cursor: 'pointer',
    },
    'a, a:visited, a:active': {
      color: theme.colors.link,
      textDecoration: 'none',
    },
  }),
}

const typography = new Typography(typographyTheme)

export default typography
