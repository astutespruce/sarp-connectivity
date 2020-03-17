import React from 'react'

import { Flex } from 'components/Grid'
import {
  OutboundLink as BaseOutboundLink,
  Link as BaseLink,
} from 'components/Link'
import styled, { themeGet } from 'style'

import { siteMetadata } from '../../../gatsby-config'

const { version: dataVersion, date: dataDate } = siteMetadata

const Wrapper = styled(Flex).attrs({
  as: 'footer',
  alignItems: 'center',
  justifyContent: 'space-between',
  py: '0.25rem',
  px: '0.5rem',
})`
  background-color: ${themeGet('colors.primary.900')};
  color: #fff;
  flex: 0 0 auto;
  border-top: ${themeGet('colors.grey.900')};
  font-size: 0.7rem;
`

const OutboundLink = styled(BaseOutboundLink)`
  color: #fff !important;
  text-decoration: none;
`

const InternalLink = styled(BaseLink)`
  color: #fff !important;
  text-decoration: none;
`

const Footer = () => {
  return (
    <Wrapper>
      <div>
        <OutboundLink to="https://southeastaquatics.net/">
          Southeast Aquatic Resources Partnership
        </OutboundLink>
        &nbsp;&nbsp;|&nbsp;&nbsp;
        <OutboundLink to="https://southeastaquatics.net/about/contact-us">
          Contact Us
        </OutboundLink>
        &nbsp;&nbsp;|&nbsp;&nbsp;
        <InternalLink to="/terms">Terms of Use</InternalLink>
      </div>

      <div>
        Data version: {dataVersion} ({dataDate})
      </div>

      <div>
        Created by the&nbsp;
        <OutboundLink to="https://consbio.org">
          Conservation Biology Institute
        </OutboundLink>{' '}
        and{' '}
        <OutboundLink to="https://astutespruce.com">
          Astute Spruce, LLC
        </OutboundLink>
      </div>
    </Wrapper>
  )
}

export default Footer
