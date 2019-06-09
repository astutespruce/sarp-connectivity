import React from 'react'
import PropTypes from 'prop-types'

import styled, {theme} from 'style'

const Icon = ({ name, size, color, ...props }) => {
  /* eslint-disable-next-line */
  const svg = require(`icons/${name}.svg`)

  const SVG = styled(svg)`
    flex-shrink: 0;
    height: ${size};
    width: ${size};
  `

  return <SVG {...props} />
}

Icon.propTypes = {
  name: PropTypes.string.isRequired,
  size: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
  color: PropTypes.string,
}

Icon.defaultProps = {
  size: '1em',
  color: theme.colors.primary[500],
}

export default Icon
