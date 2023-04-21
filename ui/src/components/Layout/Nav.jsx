import React from 'react'
import { Flex } from 'theme-ui'
import { ChartBar, SearchLocation, Download } from '@emotion-icons/fa-solid'

import { REGIONS } from 'config'
import { hasWindow } from 'util/dom'
import { Link } from 'components/Link'
import NavMenu from './NavMenu'

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

const regions = Object.values(REGIONS)
  .map(({ name: label, ...rest }) => ({ label, ...rest }))
  .sort(({ order: a }, { order: b }) => (a < b ? -1 : 1))

const Nav = () => (
  <Flex
    sx={{
      alignItems: 'center',
      fontSize: '1rem',
      position: 'relative',
      zIndex: 10000,
    }}
  >
    <NavMenu label="Explore regions" items={regions} />
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
)

export default Nav
