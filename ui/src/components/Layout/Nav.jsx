import React from 'react'
import { Flex } from 'theme-ui'
import {
  ChartBar,
  SearchLocation,
  Download,
  QuestionCircle,
} from '@emotion-icons/fa-solid'

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
      fontSize: [1, 1, '1rem'],
      position: 'relative',
      zIndex: 10000,
      gap: '0.25rem',
      flexWrap: 'wrap',
      justifyContent: 'flex-end',
    }}
  >
    <NavMenu label="Explore regions" items={regions} />
    <Link
      to="/summary"
      sx={isActivePath('/summary') ? activeNavLinkCSS : navLinkCSS}
    >
      <Flex sx={{ alignItems: 'center', gap: '0.25rem' }}>
        <ChartBar size="1em" />
        <div>Summarize</div>
      </Flex>
    </Link>
    <Link
      to="/priority"
      activeClassName="nav-active"
      sx={isActivePath('/priority') ? activeNavLinkCSS : navLinkCSS}
    >
      <Flex sx={{ alignItems: 'center', gap: '0.25rem' }}>
        <SearchLocation size="1em" />
        <div>Prioritize</div>
      </Flex>
    </Link>
    <Link
      to="/download"
      sx={isActivePath('/download') ? activeNavLinkCSS : navLinkCSS}
    >
      <Flex sx={{ alignItems: 'center', gap: '0.25rem' }}>
        <Download size="1em" />
        <div>Download</div>
      </Flex>
    </Link>
    <Link to="/faq" sx={isActivePath('/faq') ? activeNavLinkCSS : navLinkCSS}>
      <Flex sx={{ alignItems: 'center', gap: '0.25rem' }}>
        <QuestionCircle size="1em" />
        <div>FAQ</div>
      </Flex>
    </Link>
  </Flex>
)

export default Nav
