import React from 'react'
import PropTypes from 'prop-types'
import { Image } from 'theme-ui'

const Icon = ({ name, size, sx, ...props }) => {
  /* eslint-disable-next-line */
  const { default: src } = require(`icons/${name}.svg`)

  return (
    <Image
      src={src}
      {...props}
      sx={{ flex: '0 0 auto', mb: 0, width: size, height: size, ...sx }}
    />
  )
}

Icon.propTypes = {
  name: PropTypes.string.isRequired,
  size: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
  sx: PropTypes.object,
}

Icon.defaultProps = {
  size: '1em',
  sx: {},
}

export default Icon
