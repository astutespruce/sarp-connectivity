import React from 'react'
import PropTypes from 'prop-types'
import { Image as BaseImage } from 'rebass/styled-components'

import styled, { theme } from 'style'

const Icon = ({ name, size, color, ...props }) => {
  /* eslint-disable-next-line */
  const svg = require(`icons/${name}.svg`)

  const Img = styled(BaseImage).attrs({
    src: svg,
    width: size,
    height: size,
    ...props,
  })`
    flex-shrink: 0;
    /* height: ${size};
    width: ${size}; */
    margin-bottom: 0;
  `

  return <Img />
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
