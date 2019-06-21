import React from 'react'
import { Image } from 'rebass'

import { OutboundLink } from 'components/Link'
import { Columns } from 'components/Grid'
import styled, { themeGet } from 'style'
import CBILogoImage from 'images/cbi_logo.png'

import { Section, NarrowColumn, WideColumn } from '../styles'

const Content = styled.div`
  margin-bottom: 4rem;
`

const CBILogo = styled(Image).attrs({ src: CBILogoImage })`
  height: 54px;
`

const Divider = styled.div`
  height: 0.5rem;
  background-color: ${themeGet('colors.primary.800')};
  margin-bottom: 2rem;
`

const Credits = () => {
  return (
    <Section>
      <Divider />
      <Content>
        <Columns>
          <WideColumn>
            <p>
              This application was created by{' '}
              <a href="mailto:bcward@consbio.org">Brendan C. Ward</a> at
              the&nbsp;
              <OutboundLink to="https://consbio.org">
                Conservation Biology Institute
              </OutboundLink>
              &nbsp; (CBI) in partnership with{' '}
              <a href="mailto:jessica@southeastaquatics.net">Jessica Graham</a>{' '}
              and <a href="mailto:kat@southeastaquatics.net">Kat Hoenke</a> at
              the&nbsp;
              <OutboundLink to="https://southeastaquatics.net/">
                Southeast Aquatic Resources Partnership
              </OutboundLink>
              . CBI provides science and software development to support the
              conservation of biodiversity.
            </p>
          </WideColumn>
          <NarrowColumn>
            <CBILogo />
          </NarrowColumn>
        </Columns>
        <p>
          <br />
          This project was supported in part by grants from the&nbsp;
          <OutboundLink to="https://www.fws.gov/fisheries/fish-passage.html">
            U.S. Fish and Wildlife Service Fish Passage Program
          </OutboundLink>
          , the&nbsp;
          <OutboundLink to="https://gcpolcc.org/">
            Gulf Coastal Plains and Ozarks Landscape Conservation Cooperative
          </OutboundLink>
          , and the&nbsp;
          <OutboundLink to="https://myfwc.com/conservation/special-initiatives/fwli/grant/">
            Florida State Wildlife Grants Program
          </OutboundLink>
          .
        </p>
      </Content>
    </Section>
  )
}

export default Credits
