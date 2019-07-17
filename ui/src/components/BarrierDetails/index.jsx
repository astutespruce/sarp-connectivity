/* eslint-disable camelcase */
import React from 'react'
import PropTypes from 'prop-types'
import { FaEnvelope } from 'react-icons/fa'

import {useBarrierType} from 'components/Data'
import { Text, HelpText } from 'components/Text'
import { Flex, Box } from 'components/Grid'
import { CloseButton } from 'components/Button'
import BaseTabs, {
  Tab as BaseTab,
  ActiveButton,
  InactiveButton,
} from 'components/Tabs'
import { isEmptyString } from 'util/string'
import styled, { themeGet } from 'style'
import DamDetails from './DamDetails'
import SmallBarrierDetails from './SmallBarrierDetails'
import Scores from './Scores'
import { BarrierPropType } from './proptypes'

// const Wrapper = styled(Flex).attrs({flexDirection: 'column'})``

const Header = styled(Flex).attrs({
  justifyContent: 'space-between',
  py: '1rem',
  pr: '0.5rem',
  pl: '1rem',
})`
  border-bottom: 4px solid ${themeGet('colors.primary.200')};
  flex: 0 0 auto;
`

const TitleWrapper = styled(Box)`
  flex: 1 1 auto;
  margin-right: 1em;
`

const Title = styled(Text).attrs({ as: 'h3', fontSize: '1.25rem', m: 0 })``

const Subtitle = styled(Text).attrs({ fontSize: '1rem' })``

const Tabs = styled(BaseTabs)`
  flex: 1 1 auto;
  height: 100%;

  ${ActiveButton} {
      border: none;
      padding: 0.5rem 0;
    }
    ${InactiveButton} {
      background: ${themeGet('colors.primary.100')};
      border: none;
      padding: 0.5rem 0;
    }
`

const Tab = styled(BaseTab)`
  overflow-y: auto;
  padding: 1rem;
`

const Footer = styled(Flex).attrs({
  justifyContent: 'center',
  alignItems: 'center',
  py: '1rem',
})`
  flex: 0 0 auto;
  border-top: 1px solid #ddd;
  background: #f6f6f2;
`

const MailIcon = styled(FaEnvelope)`
  height: 1em;
  width: 1em;
  margin-right: 0.25em;
`

const tierToPercent = tier => (100 * (19 - (tier - 1))) / 20

const BarrierDetails = ({
  barrier,
  onClose,
}) => {
  const { sarpid, name, hasnetwork, countyname, State, ncwc_tier } = barrier

const barrierType = useBarrierType()

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

    units.forEach(unit => {
      scores[unit] = {}
      metrics.forEach(metric => {
        const tier = barrier[`${unit}_${metric}_tier`]
        scores[unit][metric] = {
          score: tierToPercent(tier),
          tier,
        }
      })
    })

    console.log('score data', scores)


    // add in custom results if available
    if (ncwc_tier) {
    scores.custom = {}
    metrics.forEach(metric => {
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
      <HelpText>
        No connectivity information is available for this barrier.
      </HelpText>
    )
  }

  return (
    <>
      <Header>
        <TitleWrapper>
          <Title>{!isEmptyString(name) ? name : defaultName}</Title>
          <Subtitle>
            {countyname}, {State}
          </Subtitle>
        </TitleWrapper>
        <CloseButton onClick={onClose} />
      </Header>

      <Tabs>
        <Tab id="details" label="Overview">
          {details}
        </Tab>
        <Tab id="ranks" label="Connectivity Ranks">
          {scoreContent}
        </Tab>
      </Tabs>

      <Footer>
        <a
          href={`mailto:Kat@southeastaquatics.net?subject=Problem with SARP Inventory for ${
            barrierType === 'dams' ? 'dam' : 'road-related barrier'
          }: ${sarpid}&body=I found the following problem with the SARP Inventory for this barrier:`}
        >
          <MailIcon /> Report a problem with this barrier
        </a>
      </Footer>
    </>
  )
}

BarrierDetails.propTypes = {
  barrier: BarrierPropType.isRequired,
  onClose: PropTypes.func.isRequired,
}

export default BarrierDetails
