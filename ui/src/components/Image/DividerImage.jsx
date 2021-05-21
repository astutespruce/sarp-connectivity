import React from 'react'
import PropTypes from 'prop-types'
import { Box } from 'theme-ui'
import { GatsbyImage } from 'gatsby-plugin-image'

import ImageCredits from './Credits'

const DividerImage = ({ image, height, minHeight, credits, position }) => (
  <Box
    sx={{
      my: '5rem',
      height,
      minHeight,
      width: '100%',
      overflow: 'hidden',
      position: 'relative',
      img: {
        objectPosition: `center ${position}`,
      },
    }}
  >
    <GatsbyImage image={image} />

    {credits ? <ImageCredits {...credits} /> : null}
  </Box>
)

DividerImage.propTypes = {
  image: PropTypes.any.isRequired,
  height: PropTypes.string,
  minHeight: PropTypes.string,
  credits: PropTypes.shape({
    url: PropTypes.string,
    author: PropTypes.string.isRequired,
  }),
  position: PropTypes.string,
}

DividerImage.defaultProps = {
  height: '50vh',
  minHeight: '6rem',
  credits: null,
  position: 'center',
}

export default DividerImage
