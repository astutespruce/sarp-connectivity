/* eslint-disable camelcase */
import React from 'react'
import PropTypes from 'prop-types'
import { Envelope, FileDownload } from '@emotion-icons/fa-solid'
import { Box, Button, Flex, Heading, Paragraph, Text } from 'theme-ui'

import { Tab, Tabs } from 'components/Tabs'
import { isEmptyString } from 'util/string'
import DamDetails from './DamDetails'
import SmallBarrierDetails from './SmallBarrierDetails'
import WaterfallDetails from './WaterfallDetails'
import Scores from './Scores'
import { BarrierPropType } from './proptypes'
import { barrierTypeLabels } from '../../../config/constants'

import { siteMetadata } from '../../../gatsby-config'

const { version: dataVersion } = siteMetadata

const tierToPercent = (tier) => (100 * (19 - (tier - 1))) / 20

const BarrierDetails = ({ barrier, onClose }) => {
  const {
    barrierType,
    sarpid,
    name,
    hasnetwork,
    ranked,
    countyname,
    State,
    ncwc_tier,
  } = barrier

  const typeLabel = barrierTypeLabels[barrierType].toLowerCase()

  let details = null
  switch (barrierType) {
    case 'dams': {
      details = <DamDetails {...barrier} />
      break
    }
    case 'barriers': {
      details = <SmallBarrierDetails {...barrier} />
      break
    }
    case 'waterfalls': {
      details = <WaterfallDetails {...barrier} />
      break
    }
    default: {
      break
    }
  }

  const defaultName = `Unknown ${typeLabel} name${
    sarpid ? ` (SARPID: ${sarpid})` : ''
  }`

  let scoreContent = null
  if (ranked) {
    // Transform properties to priorities: <unit>_<metric>_score
    // For now, we are using tier to save space in data transport, so convert them to percent
    const scores = {}
    const units = ['state']
    const metrics = ['nc', 'wc', 'ncwc']

    if (barrier.se_ncwc_tier !== -1) {
      units.push('se')
    }

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
      <>
        <Paragraph variant="help" sx={{ fontSize: 2 }}>
          No connectivity scores are available for this barrier.
        </Paragraph>
        {hasnetwork ? (
          <Paragraph variant="help" sx={{ mt: '1rem' }}>
            This {typeLabel} was excluded from prioritization because it
            provides an ecological benefit by restricting the movement of
            invasive aquatic species.
          </Paragraph>
        ) : (
          <Paragraph variant="help" sx={{ mt: '1rem' }}>
            This {typeLabel} is off-network and has no functional network
            information or related ranking.
          </Paragraph>
        )}
      </>
    )
  }

  return (
    <>
      <Box
        sx={{
          pt: '0.5rem',
          pb: '1rem',
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

        {barrierType !== 'waterfalls' ? (
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
                  mt: '0.15rem',
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
