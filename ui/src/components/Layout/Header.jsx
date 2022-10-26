import React from 'react'
import { ChartBar, SearchLocation, Download } from '@emotion-icons/fa-solid'
import { Box, Flex, Image, Text, Heading } from 'theme-ui'

import { Link } from 'components/Link'
import { siteMetadata } from 'constants'
import { hasWindow } from 'util/dom'
import LogoSVG from 'images/logo.svg'

const navLinkCSS = {
  textDecoration: 'none',
  py: '0.25rem',
  px: '0.5rem',
  display: 'block',
  color: '#fff !important',
  borderRadius: '6px',
  '&:hover': {
    bg: 'blue.8',
  },
}

const activeNavLinkCSS = {
  ...navLinkCSS,
  bg: 'primary',
}

const isActivePath = (path) =>
  hasWindow && window.location.href.search(path) !== -1

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
      <Heading
        as="h1"
        sx={{
          flex: '0 0 auto',
          m: 0,
          lineHeight: 1,
          fontSize: '1.5rem',
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
                  width: '2rem',
                  height: '2rem',
                }}
              />
            </Box>
            <Text sx={{ display: ['none', 'none', 'unset'] }}>{title}</Text>
            <Text sx={{ display: ['unset', 'unset', 'none'] }}>
              {shortTitle}
            </Text>
          </Flex>
        </Link>
      </Heading>
      <Flex
        sx={{
          alignItems: 'center',
          fontSize: '1rem',
        }}
      >
        <Link
          to="/summary"
          sx={isActivePath('/summary') ? activeNavLinkCSS : navLinkCSS}
        >
          <Flex sx={{ alignItems: 'center' }}>
            <ChartBar size="1em" style={{ marginRight: '0.25em' }} />
            <div>Summarize</div>
          </Flex>
        </Link>
        <Link
          to="/priority"
          activeClassName="nav-active"
          sx={isActivePath('/priority') ? activeNavLinkCSS : navLinkCSS}
        >
          <Flex sx={{ alignItems: 'center' }}>
            <SearchLocation size="1em" style={{ marginRight: '0.25em' }} />
            <div>Prioritize</div>
          </Flex>
        </Link>
        <Link
          to="/download"
          sx={isActivePath('/download') ? activeNavLinkCSS : navLinkCSS}
        >
          <Flex sx={{ alignItems: 'center' }}>
            <Download size="1em" style={{ marginRight: '0.25em' }} />
            <div>Download</div>
          </Flex>
        </Link>
      </Flex>
    </Flex>
  )
}

export default Header
