import React from 'react'
import { Container, Divider } from 'theme-ui'

import { Layout, SEO } from 'components/Layout'

import {
  TopSection,
  AboutSection,
  AboutNACCSection,
  RegionSection,
  ToolSection,
  GetInvolvedSection,
} from 'content/home'

const IndexPage = () => (
  <Layout>
    <TopSection />

    <Container sx={{ mt: 0 }}>
      <AboutSection />
      <Divider sx={{ mt: '6rem' }} />
      <AboutNACCSection />
      <Divider sx={{ mt: '6rem' }} />
      <ToolSection />
      <Divider sx={{ mt: '6rem' }} />
      <RegionSection />
      <Divider sx={{ mt: '6rem' }} />
      <GetInvolvedSection />
    </Container>
  </Layout>
)

export default IndexPage

export const Head = () => <SEO />
