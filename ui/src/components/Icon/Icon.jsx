import React from 'react'
import PropTypes from 'prop-types'
import { Image as BaseImage } from 'rebass/styled-components'

import styled, { theme } from 'style'

const Img = styled(BaseImage)`
  flex-shrink: 0;
  margin-bottom: 0;
`

const Icon = ({ name, size, color, ...props }) => {
  /* eslint-disable-next-line */
  const { default: src } = require(`icons/${name}.svg`)

  return <Img src={src} width={size} height={size} {...props} />
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
