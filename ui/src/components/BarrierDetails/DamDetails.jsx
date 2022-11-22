import React from 'react'
import PropTypes from 'prop-types'
import { Box, Text, Paragraph } from 'theme-ui'

import { Entry, Field, Section } from 'components/Sidebar'
import { OutboundLink } from 'components/Link'
import { formatNumber } from 'util/format'
import { isEmptyString } from 'util/string'

import {
  siteMetadata,
  CONDITION,
  CONSTRUCTION,
  PASSAGEFACILITY,
  PURPOSE,
  RECON,
  OWNERTYPE,
  BARRIEROWNERTYPE,
  WATERBODY_SIZECLASS,
} from 'config'

import NetworkInfo from './NetworkInfo'

const { version: dataVersion } = siteMetadata

const DamDetails = ({
  barrierType,
  sarpid,
  lat,
  lon,
  hasnetwork,
  excluded,
  onloop,
  height,
  nidid,
  source,
  link,
  estimated,
  yearcompleted,
  construction,
  diversion,
  purpose,
  condition,
  lowheaddam,
  passagefacility,
  river,
  waterbodykm2,
  waterbodysizeclass,
  intermittent,
  HUC8,
  HUC12,
  HUC8Name,
  HUC12Name,
  tespp,
  statesgcnspp,
  regionalsgcnspp,
  trout,
  recon,
  ownertype,
  barrierownertype,
  // metrics
  totalupstreammiles,
  perennialupstreammiles,
  alteredupstreammiles,
  unalteredupstreammiles,
  freedownstreammiles,
  freeperennialdownstreammiles,
  freealtereddownstreammiles,
  freeunaltereddownstreammiles,
  landcover,
  sizeclasses,
}) => (
  <Box
    sx={{
      mt: '-1rem',
      mx: '-1rem',
      fontSize: 1,
    }}
  >
    <Section title="Location">
      <Entry>
        {estimated === 1 ? 'Estimated dam' : 'Dam'} at {formatNumber(lat, 5)}
        &deg; N / {formatNumber(lon, 5)}
        &deg; E
        {estimated === 1 ? (
          <Paragraph variant="help" sx={{ fontSize: 0, mt: '0.5em' }}>
            Dam is estimated from other data sources and may be incorrect;
            please{' '}
            <a
              href={`mailto:Kat@southeastaquatics.net?subject=Problem with Estimated Dam ${sarpid} (data version: ${dataVersion})`}
            >
              let us know
            </a>
          </Paragraph>
        ) : null}
      </Entry>

      {river && river !== '"' && river !== 'null' && river !== 'Unknown' ? (
        <Entry>
          <Field>River or stream:</Field> {river}
        </Entry>
      ) : null}

      {waterbodysizeclass !== null && waterbodysizeclass > 0 ? (
        <Entry>
          <Field>Size of associated pond or lake:</Field>{' '}
          {waterbodykm2 > 0.1
            ? `${formatNumber(waterbodykm2, 2)} k`
            : `${formatNumber(waterbodykm2 * 1e6)} `}
          m<sup>2</sup> (
          {WATERBODY_SIZECLASS[waterbodysizeclass].split(' (')[0].toLowerCase()}
          )
        </Entry>
      ) : null}

      {intermittent === 1 ? (
        <Entry>
          Located on a reach that has intermittent or ephemeral flow
        </Entry>
      ) : null}

      {HUC12Name ? (
        <Entry>
          {HUC12Name} Subwatershed{' '}
          <Paragraph variant="help" sx={{ fontSize: 0 }}>
            HUC12: {HUC12}
          </Paragraph>
        </Entry>
      ) : null}

      {HUC8Name ? (
        <Entry>
          {HUC8Name} Subbasin{' '}
          <Paragraph variant="help" sx={{ fontSize: 0 }}>
            HUC8: {HUC8}
          </Paragraph>
        </Entry>
      ) : null}

      {ownertype !== null && ownertype > 0 ? (
        <Entry>
          <Field>Conservation land type:</Field> {OWNERTYPE[ownertype]}
        </Entry>
      ) : null}

      {barrierownertype !== null && barrierownertype > 0 ? (
        <Entry>
          <Field>Barrier ownership type:</Field>{' '}
          {BARRIEROWNERTYPE[barrierownertype]}
        </Entry>
      ) : null}
    </Section>

    <Section title="Construction information">
      {yearcompleted > 0 ? (
        <Entry>
          <Field>Constructed completed:</Field> {yearcompleted}
        </Entry>
      ) : null}
      {height > 0 ? (
        <Entry>
          <Field>Height:</Field> {height} feet
        </Entry>
      ) : null}
      {construction !== null &&
      construction >= 0 &&
      CONSTRUCTION[construction] ? (
        <Entry>
          <Field>Construction material:</Field>{' '}
          {CONSTRUCTION[construction].toLowerCase()}
        </Entry>
      ) : null}
      {lowheaddam !== null && lowheaddam >= 1 ? (
        <Entry>This is {lowheaddam === 2 ? 'likely' : ''} a lowhead dam</Entry>
      ) : null}
      {diversion === 1 ? (
        <Entry>
          <Field>Diversion:</Field> this is a water diversion
        </Entry>
      ) : null}
      {purpose !== null && purpose >= 0 && PURPOSE[purpose] ? (
        <Entry>
          <Field>Purpose:</Field> {PURPOSE[purpose].toLowerCase()}
        </Entry>
      ) : null}
      {condition !== null && condition >= 0 && CONDITION[condition] ? (
        <Entry>
          <Field>Structural condition:</Field>{' '}
          {CONDITION[condition].toLowerCase()}
        </Entry>
      ) : null}

      {passagefacility !== null &&
      passagefacility >= 0 &&
      PASSAGEFACILITY[passagefacility] ? (
        <Entry>
          <Field>Passage facility type:</Field>{' '}
          {PASSAGEFACILITY[passagefacility].toLowerCase()}
        </Entry>
      ) : null}
    </Section>

    <Section title="Functional network information">
      {hasnetwork ? (
        <NetworkInfo
          barrierType={barrierType}
          totalupstreammiles={totalupstreammiles}
          perennialupstreammiles={perennialupstreammiles}
          alteredupstreammiles={alteredupstreammiles}
          unalteredupstreammiles={unalteredupstreammiles}
          freedownstreammiles={freedownstreammiles}
          freeperennialdownstreammiles={freeperennialdownstreammiles}
          freealtereddownstreammiles={freealtereddownstreammiles}
          freeunaltereddownstreammiles={freeunaltereddownstreammiles}
          sizeclasses={sizeclasses}
          landcover={landcover}
        />
      ) : null}
      {excluded && !hasnetwork ? (
        <Entry>
          This dam was excluded from the connectivity analysis based on field
          reconnaissance or manual review of aerial imagery.
        </Entry>
      ) : null}
      {onloop && !hasnetwork ? (
        <Entry>
          <Text>
            This dam was excluded from the connectivity analysis based on its
            position within the aquatic network.
          </Text>
          <Paragraph variant="help" sx={{ mt: '1rem', fontSize: 0 }}>
            This dam was snapped to a secondary channel within the aquatic
            network according to the way that primary versus secondary channels
            are identified within the NHD High Resolution Plus dataset. This dam
            may need to be repositioned to occur on the primary channel in order
            to be included within the connectivity analysis. Please{' '}
            <b>contact us</b> to report an issue with this barrier.
          </Paragraph>
        </Entry>
      ) : null}
      {!hasnetwork && !(excluded || onloop) ? (
        <Entry>
          <Text>
            This dam is off-network and has no functional network information.
          </Text>
          <Paragraph variant="help" sx={{ mt: '1rem', fontSize: 0 }}>
            Not all dams could be correctly snapped to the aquatic network for
            analysis. Please <b>contact us</b> to report an error or for
            assistance interpreting these results.
          </Paragraph>
        </Entry>
      ) : null}
    </Section>

    <Section title="Species information">
      {tespp + regionalsgcnspp > 0 || trout ? (
        <>
          <Text sx={{ my: '0.5rem', mr: '0.5rem' }}>
            Data sources in the subwatershed containing this dam have recorded:
          </Text>
          <Box as="ul">
            <li>
              <b>{tespp}</b> federally-listed threatened and endangered aquatic
              species
            </li>
            <li>
              <b>{statesgcnspp}</b> state-listed aquatic Species of Greatest
              Conservation Need (SGCN), which include state-listed threatened
              and endangered species
            </li>
            <li>
              <b>{regionalsgcnspp}</b> regionally-listed aquatic Species of
              Greatest Conservation Need
            </li>
            <li>{trout ? 'One or more trout species' : 'No trout species'}</li>
          </Box>
        </>
      ) : (
        <Text sx={{ my: '0.5rem', mr: '0.5rem', color: 'grey.8' }}>
          Data sources in the subwatershed containing this dam have not recorded
          any federally-listed threatened and endangered aquatic species,
          state-listed aquatic Species of Greatest Conservation Need,
          regionally-listed aquatic Species of Greatest Conservation Need, or
          trout species.
        </Text>
      )}

      <Paragraph variant="help" sx={{ mt: '1rem', fontSize: 0 }}>
        Note: species information is very incomplete. These species may or may
        not be directly impacted by this dam.{' '}
        <a href="/sgcn" target="_blank">
          Read more.
        </a>
      </Paragraph>
    </Section>

    <Section title="Feasibility & conservation benefit">
      {recon !== null && recon >= 0 ? (
        <Entry>{RECON[recon]}</Entry>
      ) : (
        <Entry>No feasibility information is available for this dam.</Entry>
      )}
    </Section>

    <Section title="Other information">
      <Entry>
        <Field>SARP ID:</Field> {sarpid}
      </Entry>
      {!isEmptyString(nidid) ? (
        <Entry>
          <Field>National inventory of dams ID:</Field>{' '}
          <OutboundLink to="http://nid.usace.army.mil/cm_apex/f?p=838:12">
            {nidid}
          </OutboundLink>
        </Entry>
      ) : null}

      {!isEmptyString(source) ? (
        <Entry>
          <Field>Source:</Field> {source}
        </Entry>
      ) : null}

      {!isEmptyString(link) ? (
        <Entry>
          <OutboundLink to={link}>
            Click here for more information about this barrier
          </OutboundLink>
        </Entry>
      ) : null}

      {source && source.startsWith('WDFW') ? (
        <Entry>
          Information about this barrier is maintained by the Washington State
          Department of Fish and Wildlife, Fish Passage Division. For more
          information about specific structures, please visit the{' '}
          <OutboundLink to="https://geodataservices.wdfw.wa.gov/hp/fishpassage/index.html">
            fish passage web map
          </OutboundLink>
          .
        </Entry>
      ) : null}
    </Section>
  </Box>
)

DamDetails.propTypes = {
  barrierType: PropTypes.string.isRequired,
  sarpid: PropTypes.string.isRequired,
  lat: PropTypes.number.isRequired,
  lon: PropTypes.number.isRequired,
  hasnetwork: PropTypes.number.isRequired,
  excluded: PropTypes.number,
  onloop: PropTypes.number,
  river: PropTypes.string,
  intermittent: PropTypes.number,
  HUC8: PropTypes.string,
  HUC12: PropTypes.string,
  HUC8Name: PropTypes.string,
  HUC12Name: PropTypes.string,
  height: PropTypes.number,
  yearcompleted: PropTypes.number,
  nidid: PropTypes.string,
  source: PropTypes.string,
  link: PropTypes.string,
  estimated: PropTypes.number,
  construction: PropTypes.number,
  purpose: PropTypes.number,
  condition: PropTypes.number,
  passagefacility: PropTypes.number,
  tespp: PropTypes.number,
  statesgcnspp: PropTypes.number,
  regionalsgcnspp: PropTypes.number,
  trout: PropTypes.number,
  recon: PropTypes.number,
  ownertype: PropTypes.number,
  barrierownertype: PropTypes.number,
  totalupstreammiles: PropTypes.number,
  perennialupstreammiles: PropTypes.number,
  alteredupstreammiles: PropTypes.number,
  unalteredupstreammiles: PropTypes.number,
  freedownstreammiles: PropTypes.number,
  freeperennialdownstreammiles: PropTypes.number,
  freealtereddownstreammiles: PropTypes.number,
  freeunaltereddownstreammiles: PropTypes.number,
  landcover: PropTypes.number,
  sizeclasses: PropTypes.number,
  diversion: PropTypes.number,
  lowheaddam: PropTypes.number,
  waterbodykm2: PropTypes.number,
  waterbodysizeclass: PropTypes.number,
}

DamDetails.defaultProps = {
  HUC8: null,
  HUC12: null,
  HUC8Name: null,
  HUC12Name: null,
  excluded: false,
  onloop: false,
  river: null,
  intermittent: -1,
  nidid: null,
  source: null,
  link: null,
  estimated: 0,
  height: 0,
  yearcompleted: 0,
  construction: null,
  purpose: null,
  condition: null,
  passagefacility: null,
  tespp: 0,
  statesgcnspp: 0,
  regionalsgcnspp: 0,
  trout: 0,
  recon: null,
  ownertype: null,
  barrierownertype: null,
  totalupstreammiles: 0,
  perennialupstreammiles: 0,
  alteredupstreammiles: 0,
  unalteredupstreammiles: 0,
  freedownstreammiles: 0,
  freeperennialdownstreammiles: 0,
  freealtereddownstreammiles: 0,
  freeunaltereddownstreammiles: 0,
  landcover: null,
  sizeclasses: null,
  diversion: 0,
  lowheaddam: null,
  waterbodykm2: -1,
  waterbodysizeclass: null,
}

export default DamDetails
