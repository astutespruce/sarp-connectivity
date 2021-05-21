/* eslint-disable camelcase */
import React from 'react'
import PropTypes from 'prop-types'
import { Envelope } from '@emotion-icons/fa-solid'
import { Box, Button, Flex, Heading, Paragraph, Text } from 'theme-ui'

import { Tab, Tabs } from 'components/Tabs'

import { isEmptyString } from 'util/string'
import DamDetails from './DamDetails'
import SmallBarrierDetails from './SmallBarrierDetails'
import Scores from './Scores'
import { BarrierPropType } from './proptypes'

import { siteMetadata } from '../../../gatsby-config'

const { version: dataVersion } = siteMetadata

const tierToPercent = (tier) => (100 * (19 - (tier - 1))) / 20

const BarrierDetails = ({ barrier, onClose }) => {
  const {
    barrierType,
    sarpid,
    name,
    hasnetwork,
    countyname,
    State,
    ncwc_tier,
  } = barrier

  const details =
    barrierType === 'dams' ? (
      <DamDetails {...barrier} />
    ) : (
      <SmallBarrierDetails {...barrier} />
    )

  const defaultName =
    barrierType === 'dams' ? 'Unknown name' : 'Unnamed crossing'

  let scoreContent = null
  if (hasnetwork) {
    // Transform properties to priorities: <unit>_<metric>_score
    // For now, we are using tier to save space in data transport, so convert them to percent
    const scores = {}
    const units = ['se', 'state']
    const metrics = ['nc', 'wc', 'ncwc']

    units.forEach((unit) => {
      scores[unit] = {}
      metrics.forEach((metric) => {
        const tier = barrier[`${unit}_${metric}_tier`]
        scores[unit][metric] = {
          score: tierToPercent(tier),
          tier,
        }
      })
    })

    // add in custom results if available
    if (ncwc_tier) {
      scores.custom = {}
      metrics.forEach((metric) => {
        const tier = barrier[`${metric}_tier`]
        scores.custom[metric] = {
          score: tierToPercent(tier),
          tier,
        }
      })
    }

    scoreContent = <Scores scores={scores} barrierType={barrierType} />
  } else {
    scoreContent = (
      <Paragraph variant="help" sx={{ fontSize: 2 }}>
        No connectivity information is available for this barrier.
      </Paragraph>
    )
  }

  return (
    <>
      <Flex
        sx={{
          flex: '0 0 auto',
          justifyContent: 'space-between',
          py: '1rem',
          pr: '0.5rem',
          pl: '1rem',
          borderBottom: '4px solid',
          borderBottomColor: 'blue.2',
        }}
      >
        <Box sx={{ flex: '1 1 auto' }}>
          <Heading as="h3" sx={{ m: 0, fontSize: '1.25rem' }}>
            {!isEmptyString(name) ? name : defaultName}
          </Heading>
          {!(isEmptyString(countyname) || isEmptyString(State)) && (
            <Text>
              <i>
                {countyname} County, {State}
              </i>
              <br />
            </Text>
          )}
        </Box>
        <Button variant="close" onClick={onClose}>
          &#10006;
        </Button>
      </Flex>

      <Tabs
        sx={{
          flex: '1 1 auto',
          overflow: 'hidden',
        }}
      >
        <Tab id="details" label="Overview">
          {details}
        </Tab>
        <Tab id="ranks" label="Connectivity Ranks">
          {scoreContent}
        </Tab>
      </Tabs>

      <Flex
        sx={{
          flex: '0 0 auto',
          justifyContent: 'center',
          alignItems: 'center',
          py: '1rem',
          borderTop: '1px solid #DDD',
          bg: '#f6f6f2',
        }}
      >
        <a
          href={`mailto:Kat@southeastaquatics.net?subject=Problem with SARP Inventory for ${
            barrierType === 'dams' ? 'dam' : 'road-related barrier'
          }: ${sarpid} (data version: ${dataVersion})&body=I found the following problem with the SARP Inventory for this barrier:`}
        >
          <Envelope size="1rem" style={{ marginRight: '0.25rem' }} /> Report a
          problem with this barrier
        </a>
      </Flex>
    </>
  )
}

BarrierDetails.propTypes = {
  barrier: BarrierPropType.isRequired,
  onClose: PropTypes.func.isRequired,
}

export default BarrierDetails
