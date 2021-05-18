import React from 'react'
import PropTypes from 'prop-types'
import { GatsbyImage as Image } from 'gatsby-plugin-image'

import styled, { themeGet } from 'style'

const Wrapper = styled.div`
  margin: 5rem 0;
  height: ${({ height }) => height};
  min-height: ${({ minHeight }) => minHeight};
  width: 100%;
  position: relative;
  overflow: hidden;
`

const StyledImage = styled(Image)`
  position: absolute !important;
  left: 0;
  right: 0;
  bottom: 0;
  top: 0;
  img {
    object-position: center ${({ position }) => position} !important;
  }
`

const ImageCredits = styled.div`
  color: ${themeGet('colors.grey.300')};
  background: rgba(0, 0, 0, 0.5);
  position: absolute;
  z-index: 1000;
  bottom: 0;
  right: 0;
  padding: 0.5em;
  font-size: smaller;
  text-align: right;

  a {
    color: ${themeGet('colors.grey.300')};
  }
`

const DividerImage = ({ image, height, minHeight, credits, position }) => (
  <Wrapper height={height} minHeight={minHeight}>
    <StyledImage image={image} position={position} />

    {credits ? (
      <ImageCredits>
        Photo:&nbsp;
        <a href={credits.url} target="_blank" rel="noopener noreferrer">
          {credits.author}
        </a>
      </ImageCredits>
    ) : null}
  </Wrapper>
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
