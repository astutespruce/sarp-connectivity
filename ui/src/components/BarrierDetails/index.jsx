/* eslint-disable camelcase */
import React from 'react'
import PropTypes from 'prop-types'
import { Envelope, FileDownload } from '@emotion-icons/fa-solid'
import { Box, Button, Flex, Heading, Text } from 'theme-ui'

import { Tab, Tabs } from 'components/Tabs'
import {
  siteMetadata,
  barrierTypeLabelSingular,
  barrierNameWhenUnknown,
  STATES,
  DAM_PACK_BITS,
  SB_PACK_BITS,
  RC_PACK_BITS,
  WF_PACK_BITS,
  TIER_PACK_BITS,
} from 'config'
import { isEmptyString } from 'util/string'
import { unpackBits } from 'util/data'
import { formatNumber } from 'util/format'
import DamDetails from './DamDetails'
import RoadCrossingDetails from './RoadCrossingDetails'
import SmallBarrierDetails from './SmallBarrierDetails'
import WaterfallDetails from './WaterfallDetails'
import Scores from './Scores'
import { BarrierPropType } from './proptypes'

const { version: dataVersion } = siteMetadata

const tierToPercent = (tier) => (100 * (19 - (tier - 1))) / 20

const BarrierDetails = ({ barrier, onClose }) => {
  const {
    lat,
    lon,
    barrierType,
    networkType,
    sarpidname = '|', // should never be empty, but breaks badly if it is
    ranked,
    CountyName,
    State,
    packed,
    statetiers = null,
    tiers = null,
  } = barrier

  const typeLabel = barrierTypeLabelSingular[barrierType]

  const [sarpid, rawName] = sarpidname.split('|')

  const name = !isEmptyString(rawName)
    ? rawName
    : barrierNameWhenUnknown[barrierType] || 'Unknown name'

  let details = null
  let packedInfo = null
  switch (barrierType) {
    case 'dams': {
      packedInfo = unpackBits(packed, DAM_PACK_BITS)

      details = <DamDetails sarpid={sarpid} {...barrier} {...packedInfo} />
      break
    }
    case 'small_barriers': {
      packedInfo = unpackBits(packed, SB_PACK_BITS)

      details = (
        <SmallBarrierDetails sarpid={sarpid} {...barrier} {...packedInfo} />
      )
      break
    }
    case 'road_crossings': {
      packedInfo = unpackBits(packed, RC_PACK_BITS)
      // parse EJTract, EJTribal back to DisadvantagedCommunity
      const disadvantagedcommunityParts = []
      if (packedInfo.ejtract) {
        disadvantagedcommunityParts.push('tract')
      }
      if (packedInfo.ejtribal) {
        disadvantagedcommunityParts.push('tribal')
      }
      const disadvantagedcommunity = disadvantagedcommunityParts.join(',')

      details = (
        <RoadCrossingDetails
          sarpid={sarpid}
          {...barrier}
          {...packedInfo}
          disadvantagedcommunity={disadvantagedcommunity}
        />
      )
      break
    }
    case 'waterfalls': {
      packedInfo = unpackBits(packed, WF_PACK_BITS)

      details = (
        <WaterfallDetails sarpid={sarpid} {...barrier} {...packedInfo} />
      )
      break
    }
    default: {
      // no-op
      break
    }
  }

  console.log('barrier details:', barrier, 'packed info:', packedInfo)

  let scoreContent = null
  if (ranked) {
    // Transform properties to priorities: <unit>_<metric>_score
    // For now, we are using tier to save space in data transport, so convert them to percent
    const scores = {}
    const metrics = ['nc', 'wc', 'ncwc', 'pnc', 'pwc', 'pncwc']

    if (statetiers !== null) {
      // state ranks are in a bit-packed field, only available for dams
      const stateRanks = unpackBits(statetiers, TIER_PACK_BITS)
      scores.state = {}
      metrics.forEach((metric) => {
        const tier = stateRanks[metric]
        scores.state[metric] = {
          score: tierToPercent(tier),
          tier,
        }
      })
    }

    // add in custom results if available
    if (tiers) {
      scores.custom = {}
      metrics.forEach((metric) => {
        const tier = tiers[metric]
        scores.custom[metric] = {
          score: tierToPercent(tier),
          tier,
        }
      })
    }

    scoreContent = <Scores scores={scores} networkType={networkType} />
  }

  return (
    <>
      <Box
        sx={{
          py: '0.5rem',
          px: '0.5rem',
          borderBottom: '4px solid',
          borderBottomColor: 'blue.2',
        }}
      >
        <Flex
          sx={{
            flex: '0 0 auto',
            justifyContent: 'space-between',
          }}
        >
          <Box sx={{ flex: '1 1 auto' }}>
            <Heading as="h3" sx={{ m: '0 0 0.5rem 0', fontSize: '1.25rem' }}>
              {name}
            </Heading>
          </Box>
          <Button variant="close" onClick={onClose}>
            &#10006;
          </Button>
        </Flex>

        <Flex sx={{ color: 'grey.8', fontSize: 1, lineHeight: 1.1 }}>
          {!isEmptyString(State) ? (
            <Text sx={{ flex: '1 1 auto', mr: '1rem' }}>
              {CountyName} County, {STATES[State]}
            </Text>
          ) : null}

          <Text sx={{ flex: '0 0 auto', textAlign: 'right' }}>
            {formatNumber(lat, 3)}
            &deg; N, {formatNumber(lon, 3)}
            &deg; E
          </Text>
        </Flex>

        {/* Only show report for dams / small barriers */}
        {barrierType === 'dams' || barrierType === 'small_barriers' ? (
          <Box sx={{ lineHeight: 1, mt: '1.5rem' }}>
            <a
              href={`/report/${
                networkType === 'dams' || networkType === barrierType
                  ? barrierType
                  : 'combined_barriers'
              }/${sarpid}`}
              target="_blank"
              rel="noreferrer"
              style={{ display: 'inline-block' }}
            >
              <Flex
                sx={{
                  alignItems: 'baseline',
                }}
              >
                <Box sx={{ flex: '0 0 auto', color: 'link', mr: '0.25rem' }}>
                  <FileDownload size="1em" />
                </Box>
                <Text>Create PDF report</Text>
              </Flex>
            </a>
          </Box>
        ) : null}
      </Box>

      {ranked ? (
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
      ) : (
        // Only show details, not scores if cannot be ranked
        <Box
          sx={{
            flex: '1 1 auto',
            px: '0.5rem',
            pb: '1rem',
            overflowY: 'auto',
            overflowX: 'hidden',
          }}
        >
          {details}
        </Box>
      )}

      <Flex
        sx={{
          flex: '0 0 auto',
          justifyContent: 'center',
          alignItems: 'center',
          py: '0.5rem',
          borderTop: '1px solid #DDD',
          bg: '#f6f6f2',
        }}
      >
        <a
          href={`mailto:Kat@southeastaquatics.net?subject=Problem with SARP Inventory for ${typeLabel}: ${sarpid} (data version: ${dataVersion})&body=I found the following problem with the SARP Inventory for this barrier:`}
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
