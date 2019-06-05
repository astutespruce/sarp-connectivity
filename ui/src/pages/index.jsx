import React from 'react'

import Layout from 'components/Layout'
import { Container } from 'components/Grid'
import { Link } from 'components/Link'
import Map from 'components/Map'
import styled from 'style'

const Section = styled.section`
  h3 {
    margin-bottom: 0.25rem;
  }

  &:not(:first-child) {
    margin-top: 3rem;
  }
`

const IndexPage = () => (
  <Layout>
    <Container my="2rem">TODO</Container>
  </Layout>
)

export default IndexPage
