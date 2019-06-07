import React from 'react'

import { Flex } from 'components/Grid'
import { OutboundLink } from 'components/Link'
import styled, { themeGet } from 'style'

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
  font-size: 0.8rem;
`

const Link = styled(OutboundLink).attrs({
  target: 'blank',
  rel: 'noopener noreferrer',
})`
  color: #fff !important;
  text-decoration: none;
`

const Footer = () => {
  return (
    <Wrapper>
      <div>
        <Link to="https://southeastaquatics.net/">
          Southeast Aquatic Resources Partnership
        </Link>
        &nbsp;&nbsp;|&nbsp;&nbsp;
        <Link to="https://southeastaquatics.net/about/contact-us">
          Contact Us
        </Link>
      </div>
      <div>
        Created by the&nbsp;
        <Link to="https://consbio.org">
          Conservation Biology Institute
        </Link> and{' '}
        <Link to="https://astutespruce.com">Astute Spruce, LLC</Link>
      </div>
    </Wrapper>
  )
}

export default Footer
