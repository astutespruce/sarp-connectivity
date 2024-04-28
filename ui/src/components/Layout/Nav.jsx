import React from 'react'
import { Box, Flex } from 'theme-ui'
import {
  ChartBar,
  Fish,
  GlobeAmericas,
  SearchLocation,
  QuestionCircle,
  RulerVertical,
} from '@emotion-icons/fa-solid'

import { REGIONS } from 'config'
import { Link } from 'components/Link'
import { hasWindow } from 'util/dom'
import ClientOnly from './ClientOnly'
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

regions.push({ id: 'fhp', label: 'Fish Habitat Partnerships', url: '/fhp' })

const Nav = () => (
  <ClientOnly>
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
      <NavMenu
        label="Regions"
        items={regions}
        icon={<GlobeAmericas size="1em" />}
      />
      <Link
        to="/explore"
        sx={isActivePath('/explore') ? activeNavLinkCSS : navLinkCSS}
      >
        <Flex sx={{ alignItems: 'center', gap: '0.25rem' }}>
          <ChartBar size="1em" />
          <div>Explore &amp; Download</div>
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
        to="/survey"
        activeClassName="nav-active"
        sx={isActivePath('/survey') ? activeNavLinkCSS : navLinkCSS}
      >
        <Flex sx={{ alignItems: 'center', gap: '0.25rem' }}>
          <RulerVertical size="1em" />
          <div>Survey</div>
        </Flex>
      </Link>

      <Link
        to="/restoration"
        sx={isActivePath('/restoration') ? activeNavLinkCSS : navLinkCSS}
      >
        <Flex sx={{ alignItems: 'center', gap: '0.25rem' }}>
          <Fish size="1em" />
          <div>Restoration</div>
        </Flex>
      </Link>

      <Link to="/faq" sx={isActivePath('/faq') ? activeNavLinkCSS : navLinkCSS}>
        <Flex sx={{ alignItems: 'center', gap: '0.25rem' }}>
          <QuestionCircle size="1em" />
          <Box>FAQ</Box>
        </Flex>
      </Link>
    </Flex>
  </ClientOnly>
)

export default Nav
