/* eslint-disable camelcase */
import React, { useState } from 'react'
import PropTypes from 'prop-types'
import {FaEnvelope, FaTimesCircle} from 'react-icons/fa'

import {Text} from 'components/Text'
import {Flex, Box} from 'components/Grid'
import {Tab, TabContainer} from 'components/Tabs'
import { isEmptyString } from 'util/string'
import styled from 'style'
import DamDetails from './DamDetails'
import SmallBarrierDetails from './SmallBarrierDetails'
import Scores from './Scores'
import { BarrierPropType } from './proptypes'

const Wrapper = styled(Flex).attrs({flexDirection: 'column'})``


const Header = styled(Flex).attrs({justifyContent: 'center', py: '1rem', pr: '0.5rem', pl: '1rem'})`
    background: #f6f6f2;
    border-bottom: 1px solid #ddd;
`

// const HeaderWithTabs = styled(Box).attrs({pt: '1rem', pr: '0.5rem', pl: '1rem'})`
// background: #fff;

// `

const Title = styled(Text).attrs({fontSize: '1.5rem'})`
flex-grow: 1;

`

const Subtitle = styled(Text).attrs({fontSize: '1rem'})``




const Footer = styled(Flex).attrs({justifyContent: 'center', alignItems: 'center', py: '1rem'})`
    flex-grow: 0;
    border-top: 1px solid #ddd;
    background: #f6f6f2;
`

const CloseButton = styled(FaTimesCircle)`
height: 2em;
width: 2em;
flex: 0 0 auto;
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
  mode,  // TODO: only show results if there are some

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

  const footer = (
    <Footer>
        <a
          href={`mailto:Kat@southeastaquatics.net?subject=Problem with SARP Inventory for ${
            barrierType === 'dams' ? 'dam' : 'road-related barrier'
          }: ${sarpid}&body=I found the following problem with the SARP Inventory for this barrier:`}
        >
          <MailIcon /> Report a problem with this barrier
        </a>
    </Footer>
  )

  const defaultName =
    barrierType === 'dams' ? 'Unknown name' : 'Unnamed crossing'

  if (mode !== 'results' || !ncwc_tier) {
    return (
      <Wrapper>
        <Header>
            <Title>
                {!isEmptyString(name) ? name : defaultName}
              {!isEmptyString(countyname) && !isEmptyString(State) ? (
                <Subtitle>
                  {countyname}, {State}
                </Subtitle>
              ) : null}
            </Title>
            <CloseButton onClick={onClose} />
        </Header>

        <div id="SidebarContent" className="flex-container-column">
          {details}
        </div>

        {footer}
      </Wrapper>
    )
  }

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

//   const handleDetailsClick = () => setTab('details')
//   const handlePrioritiesClick = () => setTab('priorities')

  return (
    <Wrapper>
      <Header>
        <div className="flex-container flex-justify-center flex-align-start">
          <div className="flex-grow">
            <h5 className="title is-5">
              {!isEmptyString(name) ? name : defaultName}
            </h5>
            <h5 className="subtitle is-6">
              {countyname}, {State}
            </h5>
          </div>
          <CloseButton onClick={onClose}/>
        </div>
        {/* <div className="tabs">
          <ul>
            <li className={tab === 'details' ? 'is-active' : null}>
              <a onClick={handleDetailsClick}>Overview</a>
            </li>
            <li className={tab === 'priorities' ? 'is-active' : null}>
              <a onClick={handlePrioritiesClick}>Connectivity Ranks</a>
            </li>
          </ul>
        </div> */}
      </Header>

      <TabContainer>
          <Tab id="details" label="Overview">
              {details}
          </Tab>
          <Tab id="ranks" label="Connectivity Ranks">
              {scoreContent}
          </Tab>
      </TabContainer>

      {/* <div id="SidebarContent" className="flex-container-column">
        {tab === 'details' ? details : scoreContent}
      </div> */}

      {footer}
    </Wrapper>
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
