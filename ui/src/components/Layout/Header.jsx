import React from 'react'

import { Box, Flex, Image, Heading } from 'theme-ui'

import { siteMetadata } from 'config'
import { Link, OutboundLink } from 'components/Link'
import NACCLogoSVG from 'images/nacc_logo_white.svg'
import Nav from './Nav'

const { naccURL } = siteMetadata

const Header = () => (
  <Flex
    as="header"
    sx={{
      flex: '0 0 auto',
      alignItems: 'center',
      justifyContent: 'space-between',
      py: '0.3rem',
      pl: '0.15rem',
      pr: '1rem',
      bg: 'blue.8',
      borderBottom: '4px solid',
      borderBottomColor: 'blue.9',
    }}
  >
    <Box
      sx={{
        flex: '0 0 auto',
        'a, a:hover': {
          textDecoration: 'none',
          color: '#fff',
        },
      }}
    >
      <Flex sx={{ gap: '1rem', alignItems: 'flex-end' }}>
        <Box sx={{ flex: '0 0 auto' }}>
          <OutboundLink to={naccURL}>
            <Image
              src={NACCLogoSVG}
              sx={{
                width: ['4rem', '4rem', '5.5rem'],
              }}
            />
          </OutboundLink>
        </Box>
        <Box
          sx={{ flex: '0 0 auto', borderLeft: '1px solid #FFF', pl: '1rem' }}
        >
          <Link to="/">
            <Flex
              sx={{
                alignItems: 'center',
                flexWrap: 'wrap',
              }}
            >
              <Box sx={{ display: ['none', 'none', 'unset'], lineHeight: 1 }}>
                <Heading
                  as="h1"
                  sx={{
                    m: 0,
                    fontSize: '1.25rem',
                    fontWeight: 'normal',
                  }}
                >
                  Aquatic Barrier Inventory <br />& Prioritization Tool
                </Heading>
              </Box>
              <Heading
                as="h1"
                sx={{
                  display: ['unset', 'unset', 'none'],
                  lineHeight: 1,
                  fontSize: '1.25rem',
                  fontWeight: 'normal',

                  mr: '0.25rem',
                }}
              >
                Aquatic Barrier Tool
              </Heading>
            </Flex>
          </Link>
        </Box>
      </Flex>
    </Box>
    <Nav />
  </Flex>
)

export default Header
