import React from 'react'

import { Box, Flex, Image, Text, Heading } from 'theme-ui'

import { Link } from 'components/Link'
import { siteMetadata } from 'config'
import LogoSVG from 'images/logo.svg'
import Nav from './Nav'

const Header = () => {
  const { title, shortTitle } = siteMetadata
  return (
    <Flex
      as="header"
      sx={{
        flex: '0 0 auto',
        alignItems: 'center',
        justifyContent: 'space-between',
        py: '0.3rem',
        pl: '0.15rem',
        pr: '1rem',
        bg: 'blue.9',
        borderBottom: '4px solid',
        borderBottomColor: 'blue.8',
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
        <Link to="/">
          <Flex
            sx={{
              alignItems: 'center',
              flexWrap: 'wrap',
            }}
          >
            <Box sx={{ mr: '0.5rem' }}>
              <Image
                src={LogoSVG}
                sx={{
                  fill: '#fff',
                  mr: '0.25rem',
                  width: '2.25rem',
                  height: '2.25rem',
                }}
              />
            </Box>
            <Box sx={{ display: ['none', 'none', 'unset'], lineHeight: 1 }}>
              <Text sx={{ fontSize: 1, fontStyle: 'italic' }}>National</Text>
              <Heading
                as="h1"
                sx={{
                  m: 0,
                  fontSize: '1.25rem',
                  fontWeight: 'normal',
                }}
              >
                Aquatic Barrier Inventory & Prioritization Tool
              </Heading>
            </Box>
            <Heading
              as="h1"
              sx={{
                display: ['unset', 'unset', 'none'],
                lineHeight: 1,
                fontSize: '1.5rem',
              }}
            >
              {shortTitle}
            </Heading>
          </Flex>
        </Link>
      </Box>
      <Nav />
    </Flex>
  )
}

export default Header
