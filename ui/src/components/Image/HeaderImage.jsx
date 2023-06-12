import React from 'react'
import PropTypes from 'prop-types'
import { Box, Container, Heading } from 'theme-ui'
import { GatsbyImage } from 'gatsby-plugin-image'

import ImageCredits from './Credits'

const HeaderImage = ({
  image,
  height,
  minHeight,
  maxHeight,
  title,
  subtitle,
  credits,
  caption,
}) => (
  <Box
    sx={{
      position: 'relative',
      height,
      minHeight,
      maxHeight: maxHeight || height,
    }}
  >
    <GatsbyImage
      image={image}
      style={{
        position: 'relative',
        top: 0,
        zIndex: 0,
        height,
        minHeight,
        maxHeight: maxHeight || height,
      }}
      alt=""
    />

    <Box
      sx={{
        mt: 0,
        overflow: 'hidden',
        width: '100%',
        position: 'absolute',
        zIndex: 2,
        top: 0,
        bottom: 0,
        left: 0,
        right: 0,
      }}
    >
      {title && (
        <Box
          sx={{
            background:
              'linear-gradient(to top, transparent 0, rgba(0,0,0,0.25) 1rem, rgba(0,0,0,0.4) 3rem)',
            py: ['2rem', '3rem'],
          }}
        >
          <Container
            sx={{
              p: '1rem',
              borderTop: '3px solid #FFF',
              borderBottom: '3px solid #FFF',
              textShadow: '1px 1px 3px #000',
              color: '#FFF',
              lineHeight: 1.1,
            }}
          >
            <Heading
              as="h1"
              sx={{
                m: 0,
                fontSize: '3rem',
              }}
            >
              {title}
            </Heading>

            {subtitle && (
              <Heading
                as="h2"
                sx={{
                  margin: '0.5rem 0 0 0',
                  fontWeight: 'normal',
                  fontSize: '1.5rem',
                }}
              >
                {subtitle}
              </Heading>
            )}
          </Container>
        </Box>
      )}
    </Box>
    {credits ? <ImageCredits caption={caption} {...credits} /> : null}
  </Box>
)

HeaderImage.propTypes = {
  image: PropTypes.any.isRequired,
  height: PropTypes.string,
  minHeight: PropTypes.string,
  maxHeight: PropTypes.string,
  title: PropTypes.string,
  subtitle: PropTypes.string,
  credits: PropTypes.shape({
    url: PropTypes.string.isRequired,
    author: PropTypes.string.isRequired,
  }),
  caption: PropTypes.string,
}

HeaderImage.defaultProps = {
  height: '60vh',
  minHeight: '20rem',
  maxHeight: null,
  title: null,
  subtitle: null,
  credits: null,
  caption: null,
}

export default HeaderImage
