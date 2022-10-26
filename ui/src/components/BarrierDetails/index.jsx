/* eslint-disable camelcase */
import React from 'react'
import PropTypes from 'prop-types'
import { Envelope, FileDownload } from '@emotion-icons/fa-solid'
import { Box, Button, Flex, Heading, Paragraph, Text } from 'theme-ui'

import { Tab, Tabs } from 'components/Tabs'
import {
  siteMetadata,
  barrierTypeLabelSingular,
  STATES,
  DAM_PACK_BITS,
  SB_PACK_BITS,
  WF_PACK_BITS,
  STATE_TIER_PACK_BITS,
} from 'constants'
import { isEmptyString } from 'util/string'
import { unpackBits } from 'util/data'
import { capitalize } from 'util/format'
import DamDetails from './DamDetails'
import SmallBarrierDetails from './SmallBarrierDetails'
import WaterfallDetails from './WaterfallDetails'
import Scores from './Scores'
import { BarrierPropType } from './proptypes'

const { version: dataVersion } = siteMetadata

const tierToPercent = (tier) => (100 * (19 - (tier - 1))) / 20

const BarrierDetails = ({ barrier, onClose }) => {
  const {
    barrierType,
    sarpidname,
    ranked,
    CountyName,
    State,
    packed,
    statetiers,
    ncwc_tier, // field from custom ranking
  } = barrier

  const [sarpid, name] = sarpidname.split('|')

  const isCrossing =
    barrierType === 'small_barriers' && sarpid && sarpid.startsWith('cr')

  const typeLabel = isCrossing
    ? 'road / stream crossing'
    : barrierTypeLabelSingular[barrierType]

  let details = null
  let packedInfo = null
  switch (barrierType) {
    case 'dams': {
      packedInfo = unpackBits(packed, DAM_PACK_BITS)

      details = (
        <DamDetails sarpid={sarpid} name={name} {...barrier} {...packedInfo} />
      )
      break
    }
    case 'small_barriers': {
      packedInfo = unpackBits(packed, SB_PACK_BITS)

      details = (
        <SmallBarrierDetails
          sarpid={sarpid}
          name={name}
          {...barrier}
          {...packedInfo}
        />
      )
      break
    }
    case 'waterfalls': {
      packedInfo = unpackBits(packed, WF_PACK_BITS)

      details = (
        <WaterfallDetails
          sarpid={sarpid}
          name={name}
          {...barrier}
          {...packedInfo}
        />
      )
      break
    }
    default: {
      break
    }
  }

  const { hasnetwork = 0, invasive = 0, nostructure = 0 } = packedInfo || {}

  let defaultName = `${capitalize(typeLabel)}${
    sarpid ? ` (SARPID: ${sarpid})` : ''
  }`
  if (isCrossing) {
    defaultName = 'Unknown road / stream crossing name'
  }

  let scoreContent = null
  if (ranked) {
    // Transform properties to priorities: <unit>_<metric>_score
    // For now, we are using tier to save space in data transport, so convert them to percent
    const scores = {}
    const metrics = ['nc', 'wc', 'ncwc', 'pnc', 'pwc', 'pncwc']

    // state ranks are in a bit-packed field
    const stateRanks = unpackBits(statetiers, STATE_TIER_PACK_BITS)
    scores.state = {}
    metrics.forEach((metric) => {
      const tier = stateRanks[metric]
      scores.state[metric] = {
        score: tierToPercent(tier),
        tier,
      }
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
    let reason = null

    if (hasnetwork) {
      if (invasive) {
        reason = `This ${typeLabel} was excluded from prioritization because it provides an ecological benefit by restricting the movement of invasive aquatic species.`
      } else if (nostructure) {
        reason = `This ${typeLabel} was excluded from prioritization because it is a water diversion without associated in-stream barrier.`
      } else if (isCrossing) {
        reason = `This {typeLabel} has not yet been evaluated for impacts to aquatic organisms and does not yet have functional network information or related ranking.`
      }
    }

    scoreContent = (
      <>
        <Paragraph variant="help" sx={{ fontSize: 2 }}>
          No connectivity scores are available for this {typeLabel}.
        </Paragraph>
        {reason ? (
          <Paragraph variant="help" sx={{ mt: '1rem' }}>
            {reason}
          </Paragraph>
        ) : null}
      </>
    )
  }

  return (
    <>
      <Box
        sx={{
          py: '0.5rem',
          pr: '0.5rem',
          pl: '1rem',
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
            <Heading as="h3" sx={{ m: 0, fontSize: '1.25rem' }}>
              {!isEmptyString(name) ? name : defaultName}
            </Heading>

            {!(isEmptyString(CountyName) || isEmptyString(State)) && (
              <Text>
                <i>
                  {CountyName} County, {STATES[State]}
                </i>
                <br />
              </Text>
            )}
          </Box>
          <Button variant="close" onClick={onClose}>
            &#10006;
          </Button>
        </Flex>

        {barrierType !== 'waterfalls' && !isCrossing ? (
          <Box>
            <a
              href={`/report/${barrierType}/${sarpid}`}
              target="_blank"
              rel="noreferrer"
            >
              <Flex
                sx={{
                  alignItems: 'center',
                  flex: '1 1 auto',
                  mt: '0.5rem',
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

      {barrierType === 'waterfalls' ? (
        <Box
          sx={{ flex: '1 1 auto', px: '1rem', pb: '1rem', overflowY: 'auto' }}
        >
          {details}
        </Box>
      ) : (
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
      )}

      {sarpid ? (
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
      ) : null}
    </>
  )
}

BarrierDetails.propTypes = {
  barrier: BarrierPropType.isRequired,
  onClose: PropTypes.func.isRequired,
}

export default BarrierDetails
