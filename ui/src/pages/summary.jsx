import React, { useState } from 'react'

// import { Text, HelpText as BaseHelpText } from 'components/Text'
import { Flex } from 'components/Grid'
import Layout from 'components/Layout'
import Sidebar from 'components/Sidebar'
import { Map } from 'components/Map'
import styled, { themeGet } from 'style'

const Wrapper = styled(Flex)`
  height: 100%;
`

const MapContainer = styled.div`
  position: relative;
  flex: 1 0 auto;
  height: 100%;
`

// const HelpText = styled(BaseHelpText).attrs({ mx: '1rem', mb: '1rem' })``

const SummaryPage = () => {
  return (
    <Layout title="Summarize">
      <Wrapper>
        <Sidebar>TODO</Sidebar>
        <MapContainer>
          <Map />
        </MapContainer>
      </Wrapper>
    </Layout>
  )
}

SummaryPage.propTypes = {}


export default SummaryPage
