/* eslint-disable camelcase */
import React from 'react'
import PropTypes from 'prop-types'
import { Envelope, ExclamationTriangle } from '@emotion-icons/fa-solid'
import { Box, Flex, Spinner, Text } from 'theme-ui'
import { useQuery } from '@tanstack/react-query'

import { fetchBarrierDetails } from 'components/Data/API'
import { Tab, Tabs } from 'components/Tabs'
import {
  siteMetadata,
  barrierTypeLabelSingular,
  barrierNameWhenUnknown,
} from 'config'
import { isEmptyString } from 'util/string'

import Header from './Header'
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
    tiers = null,
  } = barrier

  const typeLabel = barrierTypeLabelSingular[barrierType]
  const [sarpid, rawName] = sarpidname.split('|')
  const name = !isEmptyString(rawName)
    ? rawName
    : barrierNameWhenUnknown[barrierType] || 'Unknown name'

  console.log(
    'show barrier details: ',
    networkType,
    barrierType,
    sarpid,
    barrier
  )

  const { isLoading, error, data } = useQuery({
    queryKey: ['getBarrierDetails', networkType, sarpid],
    queryFn: () => fetchBarrierDetails(networkType, sarpid),

    staleTime: 60 * 60 * 1000, // 60 minutes
    // staleTime: 1, // use then reload to force refresh of underlying data during dev
    refetchOnWindowFocus: false,
    refetchOnMount: false,
  })

  let content = null

  if (isLoading) {
    content = (
      <Flex
        sx={{
          alignItems: 'center',
          flexDirection: 'column',
          p: '1rem',
          mt: '2rem',
          flex: '1 1 auto',
        }}
      >
        <Flex sx={{ alignItems: 'center', gap: '0.5rem' }}>
          <Spinner size="2rem" />
          <Text>Loading details...</Text>
        </Flex>
      </Flex>
    )
  }

  // data===null is a signal for barrier data not found, skip retry
  if (error || (!isLoading && data === null)) {
    content = (
      <Flex
        sx={{
          alignItems: 'center',
          flexDirection: 'column',
          p: '1rem',
          mt: '2rem',
          flex: '1 1 auto',
        }}
      >
        <Flex sx={{ color: 'highlight', alignItems: 'center' }}>
          <ExclamationTriangle size="2em" />
          <Text sx={{ ml: '0.5rem', fontSize: '2rem' }}>Whoops!</Text>
        </Flex>
        There was an error loading these data. Please try clicking on a
        different barrier or refresh this page in your browser.
        <Text variant="help" sx={{ mt: '2rem' }}>
          If it happens again, please{' '}
          <a href="mailto:kat@southeastaquatics.net">contact us</a>.
        </Text>
      </Flex>
    )
  }

  let county = ''
  let state = ''
  let removed = false
  let yearremoved = null
  let isPriority = false
  let isSurveyed = false

  if (data) {
    console.log('barrier details:', sarpid, data)

    county = data.county
    state = data.state
    removed = data.removed
    yearremoved = data.yearremoved
    isPriority = data.ispriority
    isSurveyed = data.surveyed === 1

    let details = null
    switch (barrierType) {
      case 'dams': {
        details = (
          <DamDetails
            barrierType={barrierType}
            networkType={networkType}
            sarpid={sarpid}
            {...data}
          />
        )
        break
      }
      case 'small_barriers': {
        details = (
          <SmallBarrierDetails
            barrierType={barrierType}
            networkType={networkType}
            sarpid={sarpid}
            {...data}
          />
        )
        break
      }
      case 'road_crossings': {
        details = (
          <RoadCrossingDetails
            barrierType={barrierType}
            networkType={networkType}
            sarpid={sarpid}
            {...data}
          />
        )
        break
      }
      case 'waterfalls': {
        details = (
          <WaterfallDetails
            barrierType={barrierType}
            networkType={networkType}
            sarpid={sarpid}
            {...data}
          />
        )
        break
      }
      default: {
        // no-op
        break
      }
    }

    let scoreContent = null
    if (ranked) {
      // Transform properties to priorities: <unit>_<metric>_score
      // For now, we are using tier to save space in data transport, so convert them to percent
      const scores = {}
      const metrics = ['nc', 'wc', 'ncwc', 'pnc', 'pwc', 'pncwc']

      // state ranks are only available for dams networks (not combined)
      if (
        networkType === 'dams' &&
        data.state_ncwc_tier !== null &&
        data.state_ncwc_tier !== undefined &&
        data.state_ncwc_tier !== -1
      ) {
        scores.state = {}
        metrics.forEach((metric) => {
          const tier = data[`state_${metric}_tier`]
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

    if (ranked) {
      content = (
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
      )
    } else {
      // Only show details, not scores if cannot be ranked
      content = (
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
      )
    }
  }

  return (
    <>
      <Header
        barrierType={barrierType}
        networkType={networkType}
        sarpid={sarpid}
        name={name}
        lat={lat}
        lon={lon}
        county={county}
        state={state}
        removed={removed}
        yearremoved={yearremoved}
        isPriority={isPriority}
        isSurveyed={isSurveyed}
        onClose={onClose}
      />

      {content}

      <Box
        sx={{
          flex: '0 0 auto',
          py: '0.5rem',
          borderTop: '1px solid #DDD',
          bg: '#f6f6f2',
        }}
      >
        <Flex
          sx={{
            justifyContent: 'center',
            alignItems: 'center',
            gap: '0.25rem',
          }}
        >
          <a
            href={`mailto:Kat@southeastaquatics.net?subject=Problem with SARP Inventory for ${typeLabel}: ${sarpid} (data version: ${dataVersion})&body=I found the following problem with the SARP Inventory for this barrier:`}
          >
            <Envelope size="1rem" /> Report an error with this barrier
          </a>
        </Flex>
        <Text
          sx={{
            fontSize: 0,
            px: '1rem',
            lineHeight: 1,
            mt: '0.25rem',
            color: 'grey.7',
          }}
        >
          If this barrier should have a different value for one of the fields
          above, please let us know!
        </Text>
      </Box>
    </>
  )
}

BarrierDetails.propTypes = {
  barrier: BarrierPropType.isRequired,
  onClose: PropTypes.func.isRequired,
}

export default BarrierDetails
