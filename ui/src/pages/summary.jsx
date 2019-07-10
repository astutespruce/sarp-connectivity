import React, { useState } from 'react'

import { Text, HelpText } from 'components/Text'
import { Flex, Box } from 'components/Grid'
import Layout from 'components/Layout'
import Sidebar from 'components/Sidebar'
import UnitSearch from 'components/UnitSearch'
import { TopBar } from 'components/Map'
import {Map, UnitDetails} from 'components/Summary'
import { useSummaryData } from 'components/Data'
import { ToggleButton } from 'components/Button'
import { formatNumber } from 'util/format'
import styled, { themeGet } from 'style'
import { SYSTEMS } from '../../config/constants'

const Wrapper = styled(Flex)`
  height: 100%;
`

const SidebarContent = styled(Box).attrs({ p: '1rem' })``

const MapContainer = styled.div`
  position: relative;
  flex: 1 0 auto;
  height: 100%;
`

const Intro = styled(Text).attrs({ mb: '1rem' })``

const Note = styled(HelpText).attrs({ mt: '3rem' })`
  color: ${themeGet('colors.grey.600')};
`

const TopBarToggle = styled(ToggleButton)`
  margin: 0 1rem;

  button {
    text-transform: lowercase;
    padding: 0.25rem 0.5rem;
    font-size: 0.9rem;
  }
`

const barrierTypeOptions = [
  { value: 'dams', label: 'dams' },
  { value: 'barriers', label: 'road-related barriers' },
]

const systemOptions = Object.entries(SYSTEMS).map(([value, label]) => ({
  value,
  label,
}))

const SummaryPage = () => {
  const { dams, miles } = useSummaryData()
  const [system, setSystem] = useState('HUC')
  const [barrierType, setBarrierType] = useState('dams')
  const [searchFeature, setSearchFeature] = useState(null)
  const [selectedUnit, setSelectedUnit] = useState(null)

  const handleSearch = nextSearchFeature => {
    setSearchFeature(nextSearchFeature)
  }

  const handleSetBarrierType = nextBarrierType => {
    setBarrierType(nextBarrierType)
  }

  const handleSetSystem = nextSystem => {
    setSystem(nextSystem)
    setSelectedUnit(null)
  }

  const handleSelectUnit = feature => {
    setSelectedUnit(feature)
  }

  const handleDetailsClose = () => {
    setSelectedUnit(null)
    setSearchFeature(null)
  }

  return (
    <Layout title="Summarize">
      <Wrapper>
        <Sidebar>
        {selectedUnit !== null ? (
              <UnitDetails summaryUnit={selectedUnit} barrierType={barrierType} onClose={handleDetailsClose}/>
            ) : (
          <SidebarContent>
            <Intro>
              Across the Southeast, there are at least {formatNumber(dams, 0)}{' '}
              dams, resulting in an average of {formatNumber(miles, 0)} miles of
              connected rivers and streams.
              <br />
              <br />
              Click on a summary unit the map for more information about that
              area.
            </Intro>
            <UnitSearch system={system} onSelect={handleSearch} />

            <Note>
              Note: These statistics are based on <i>inventoried</i> dams.
              Because the inventory is incomplete in many areas, areas with a
              high number of dams may simply represent areas that have a more
              complete inventory.
            </Note>
          </SidebarContent>
          )}
        </Sidebar>
        <MapContainer>
          <Map
            barrierType={barrierType}
            system={system}
            searchFeature={searchFeature}
            selectedUnit={selectedUnit}
            onSelectUnit={handleSelectUnit}
          />
          <TopBar>
            Show:
            <TopBarToggle
              value={barrierType}
              options={barrierTypeOptions}
              onChange={handleSetBarrierType}
            />
            by
            <TopBarToggle
              value={system}
              options={systemOptions}
              onChange={handleSetSystem}
            />
          </TopBar>
        </MapContainer>
      </Wrapper>
    </Layout>
  )
}

SummaryPage.propTypes = {}

export default SummaryPage
