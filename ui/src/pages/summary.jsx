import React, { useState } from 'react'

import { Text, HelpText } from 'components/Text'
import { Flex, Box } from 'components/Grid'
import Layout from 'components/Layout'
import Sidebar from 'components/Sidebar'
import UnitSearch from 'components/UnitSearch'
import { Map } from 'components/Map'
import { useBoundsData } from 'components/Data'
import {formatNumber} from 'util/format'
import styled, { themeGet } from 'style'
import { useSummaryData } from '../components/Data';


const Wrapper = styled(Flex)`
  height: 100%;
`

const SidebarContent = styled(Box).attrs({p: '1rem'})``

const MapContainer = styled.div`
  position: relative;
  flex: 1 0 auto;
  height: 100%;
`

const Intro = styled(Text).attrs({mb: '1rem'})``

const Note = styled(HelpText).attrs({mt: '3rem'})`
color: ${themeGet('colors.grey.600')};

`


const SummaryPage = () => {
  const {dams, miles} = useSummaryData()
  // TODO:
  const system = 'HUC'

const handleSearch = (searchFeature) => {
  console.log('TODO: set search feature', searchFeature)
}

  return (
    <Layout title="Summarize">
      <Wrapper>
        <Sidebar>
          

<SidebarContent>
<Intro>
          Across the Southeast, there are at least {formatNumber(dams, 0)} dams, resulting in an average
                            of {formatNumber(miles, 0)} miles of connected rivers and streams.
                            <br />
                            <br />
                            Click on a summary unit the map for more information about that area.

          </Intro>
<UnitSearch system={system} onSelect={handleSearch}/>

<Note>
Note: These statistics are based on <i>inventoried</i> dams. Because the inventory is
                            incomplete in many areas, areas with a high number of dams may simply represent areas that
                            have a more complete inventory.
</Note>


</SidebarContent>
        </Sidebar>
        <MapContainer>
          <Map />
        </MapContainer>
      </Wrapper>
    </Layout>
  )
}

SummaryPage.propTypes = {}


export default SummaryPage
