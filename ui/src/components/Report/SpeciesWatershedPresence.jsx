import React from 'react'
import PropTypes from 'prop-types'
import { Text, View } from '@react-pdf/renderer'

import { SALMONID_ESU, TROUT } from 'config'
import { formatNumber } from 'util/format'

import { Bold, Flex, List, ListItem, Section } from './elements'

const SpeciesWatershedPresence = ({
  barrierType,
  tespp,
  statesgcnspp,
  regionalsgcnspp,
  trout,
  salmonidesu,
  ...props
}) => {
  const troutSpp = trout ? trout.split(',').map((code) => TROUT[code]) : []

  return (
    <Section
      title="Species information for this subwatershed"
      {...props}
      wrap={false}
    >
      <View>
        <Text>
          Data sources in the subwatershed containing this{' '}
          {barrierType === 'dams' ? 'dam' : 'road-related barrier'} have
          recorded:
        </Text>
      </View>

      <Flex style={{ marginTop: 24 }}>
        <View
          style={{
            flex: '1 1 25%',
          }}
        >
          <Text>
            <Bold>{formatNumber(tespp)}</Bold> federally-listed threatened and
            endangered aquatic species
          </Text>
        </View>

        <View
          style={{
            flex: '1 1 25%',
            marginLeft: 14,
            paddingLeft: 14,
            borderLeft: '1px solid #cfd3d6',
          }}
        >
          <Text>
            <Bold>{statesgcnspp}</Bold> state-listed aquatic Species of Greatest
            Conservation Need (SGCN)
          </Text>
        </View>

        <View
          style={{
            flex: '1 1 25%',
            marginLeft: 14,
            paddingLeft: 14,
            borderLeft: '1px solid #cfd3d6',
          }}
        >
          <Text>
            <Bold>{regionalsgcnspp}</Bold> regionally-listed aquatic Species of
            Greatest Conservation Need
          </Text>
        </View>
      </Flex>

      <View style={{ marginTop: 14 }}>
        <Text>
          {trout
            ? `This subwatershed includes recorded observations of ${troutSpp.join(troutSpp.length === 2 ? ' and ' : ', ')}.`
            : 'No interior or eastern native trout species have been recorded in this subwatershed.'}
        </Text>
      </View>

      {salmonidesu ? (
        <View style={{ marginTop: 14 }}>
          <Text>
            This subwatershed falls within the following salmon Evolutionarily
            Significant Units (ESU) / steelhead trout Discrete Population
            Segments (DPS):
          </Text>
          <List style={{ marginLeft: 12 }}>
            {salmonidesu.split(',').map((code) => (
              <ListItem key={code}>
                <Text>{SALMONID_ESU[code]}</Text>
              </ListItem>
            ))}
          </List>
        </View>
      ) : null}

      <Text style={{ color: '#7f8a93', marginTop: 24, fontSize: 10 }}>
        Note: State and regionally listed species of greatest conservation need
        may include state-listed threatened and endangered species. Trout
        species presence is based on occurrences of Apache, brook, bull,
        cutthroat, Gila, lake, and redband trout species. Species information is
        very incomplete and only includes species that have been identified by
        available data sources for this subwatershed. These species may or may
        not be directly impacted by this barrier. The absence of species in the
        available data does not necessarily indicate the absence of species in
        the subwatershed.
      </Text>
    </Section>
  )
}

SpeciesWatershedPresence.propTypes = {
  barrierType: PropTypes.string.isRequired,
  tespp: PropTypes.number,
  statesgcnspp: PropTypes.number,
  regionalsgcnspp: PropTypes.number,
  trout: PropTypes.string,
  salmonidesu: PropTypes.string,
}

SpeciesWatershedPresence.defaultProps = {
  tespp: 0,
  statesgcnspp: 0,
  regionalsgcnspp: 0,
  trout: null,
  salmonidesu: null,
}

export default SpeciesWatershedPresence
