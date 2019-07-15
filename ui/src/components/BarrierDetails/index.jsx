/* eslint-disable camelcase */
import React, { useState } from 'react'
import PropTypes from 'prop-types'
import { FaEnvelope, FaTimesCircle } from 'react-icons/fa'

import { Text } from 'components/Text'
import { Flex, Box } from 'components/Grid'
import { CloseButton } from 'components/Button'
import BaseTabs, {
  Tab as BaseTab,
  TabBar,
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
  /* background: #f6f6f2; */
  /* border-bottom: 1px solid #ddd; */
  border-bottom: 4px solid ${themeGet('colors.primary.200')};
  flex: 0 0 auto;
`

// const HeaderWithTabs = styled(Box).attrs({pt: '1rem', pr: '0.5rem', pl: '1rem'})`
// background: #fff;

// `

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
  barrierType,
  mode, // TODO: only show results if there are some

  onClose,
}) => {
  const { sarpid, name, hasnetwork, countyname, State, ncwc_tier } = barrier

  // const [tab, setTab] = useState('details')

  const details =
    barrierType === 'dams' ? (
      <DamDetails {...barrier} />
    ) : (
      <SmallBarrierDetails {...barrier} />
    )

  const defaultName =
    barrierType === 'dams' ? 'Unknown name' : 'Unnamed crossing'

  // if (mode !== 'results' || !ncwc_tier) {
  //   return (
  //     <Wrapper>
  //       <Header>
  //           <Title>
  //               {!isEmptyString(name) ? name : defaultName}
  //             {!isEmptyString(countyname) && !isEmptyString(State) ? (
  //               <Subtitle>
  //                 {countyname}, {State}
  //               </Subtitle>
  //             ) : null}
  //           </Title>
  //           <CloseButton onClick={onClose} />
  //       </Header>

  //       <div id="SidebarContent" className="flex-container-column">
  //         {details}
  //       </div>

  //       {footer}
  //     </Wrapper>
  //   )
  // }

  let scoreContent = null
  if (hasnetwork) {
    // Transform properties to priorities: <unit>_<metric>_score
    // For now, we are using tier to save space in data transport, so convert them to percent
    const scores = {}
    const units = ['se', 'state']
    const metrics = ['nc', 'wc', 'ncwc']
    // TODO: "gainmiles", "landcover", "sinuosity", "sizeclasses",

    scores.custom = {}
    metrics.forEach(metric => {
      const tier = barrier[`${metric}_tier`]
      scores.custom[metric] = {
        score: tierToPercent(tier),
        tier,
      }
    })

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

    scoreContent = <Scores scores={scores} />
  } else {
    scoreContent = (
      <p className="has-text-grey">
        No connectivity information is available for this barrier.
      </p>
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
  barrierType: PropTypes.string.isRequired,
  mode: PropTypes.string.isRequired,
  barrier: BarrierPropType.isRequired,
  onClose: PropTypes.func.isRequired,
}

// const mapStateToProps = globalState => {
//   const state = globalState.get('details')

//   return {
//     mode: globalState.get('priority').get('mode'),
//     tab: state.get('tab'),
//     type: globalState.get('priority').get('type'),
//   }
// }

// export default connect(
//   mapStateToProps,
//   { setTab: setDetailsTab }
// )(BarrierDetailsSidebar)

export default BarrierDetails
