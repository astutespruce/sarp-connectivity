import React from 'react'
import PropTypes from 'prop-types'
import { Text } from 'theme-ui'

import {
  barrierTypeLabelSingular,
  OWNERTYPE,
  BARRIEROWNERTYPE,
  FERC_REGULATED,
  STATE_REGULATED,
  WATER_RIGHT,
  STREAM_SIZECLASS,
  STREAM_SIZECLASS_DRAINAGE_AREA,
  WATERBODY_SIZECLASS,
  FISH_HABITAT_PARTNERSHIPS,
} from 'config'
import { OutboundLink } from 'components/Link'
import { Entry, Field } from 'components/Sidebar'
import { formatNumber } from 'util/format'
import { isEmptyString } from 'util/string'

const LocationInfo = ({
  annualflow,
  barrierType,
  reachName,
  huc12,
  basin,
  subwatershed,
  ownertype,
  barrierownertype,
  fercregulated,
  stateregulated,
  fedregulatoryagency,
  waterright,
  costlower,
  costmean,
  costupper,
  ejtract,
  ejtribal,
  fishhabitatpartnership,
  nativeterritories,
  intermittent,
  storagevolume,
  streamorder,
  streamsizeclass,
  waterbodysizeclass,
  waterbodykm2,
  fatality,
}) => {
  const barrierTypeLabel = barrierTypeLabelSingular[barrierType]
  const hasReachName =
    !isEmptyString(reachName) &&
    reachName.toLowerCase() !== 'unknown' &&
    reachName.toLowerCase() !== 'unnamed'

  return (
    <>
      <Entry>
        <Text sx={{ fontSize: 1 }}>
          {hasReachName ? `On ${reachName} in` : 'Within'} {subwatershed}{' '}
          Subwatershed, {basin} Subbasin{' '}
        </Text>
        <Text sx={{ fontSize: 0, color: 'grey.8' }}>(HUC12: {huc12})</Text>
      </Entry>
      {intermittent === 1 ? (
        <Entry>This {barrierTypeLabel} is on an intermittent reach</Entry>
      ) : null}
      {storagevolume !== null ? (
        <Entry>
          <Field label="Normal storage volume">
            {formatNumber(storagevolume)} acre/feet
          </Field>
        </Entry>
      ) : null}
      {waterbodysizeclass > 0 ? (
        <Entry>
          This {barrierTypeLabel} is associated with a{' '}
          {WATERBODY_SIZECLASS[waterbodysizeclass].split(' (')[0].toLowerCase()}{' '}
          (
          {waterbodykm2 > 0.1
            ? `${formatNumber(waterbodykm2, 2)} k`
            : `${formatNumber(waterbodykm2 * 1e6)} `}
          m<sup>2</sup> )
        </Entry>
      ) : null}
      {streamorder > 0 ? (
        <Entry>
          <Field label="Stream order (NHD modified Strahler)">
            {streamorder}
          </Field>
        </Entry>
      ) : null}
      {streamsizeclass ? (
        <Entry>
          <Field label="Stream size class">
            {STREAM_SIZECLASS[streamsizeclass]}
            <br />
            <Text sx={{ fontSize: 0 }}>
              (drainage area: {STREAM_SIZECLASS_DRAINAGE_AREA[streamsizeclass]}{' '}
              km
              <sup>2</sup>)
            </Text>
          </Field>
        </Entry>
      ) : null}

      {annualflow !== null && annualflow >= 0 ? (
        <Entry>
          <Field label="Stream reach annual flow rate">
            {formatNumber(annualflow)} CFS
          </Field>
        </Entry>
      ) : null}

      {ownertype !== null && ownertype > 0 ? (
        <Entry>
          <Field label="Conservation land type">{OWNERTYPE[ownertype]}</Field>
        </Entry>
      ) : null}
      {barrierownertype !== null && barrierType !== 'waterfalls' ? (
        <Entry>
          <Field label="Barrier ownership type">
            {BARRIEROWNERTYPE[barrierownertype]}
          </Field>
        </Entry>
      ) : null}

      {fercregulated !== null && fercregulated > 0 ? (
        <Entry>
          <Field
            label="Regulated by the Federal Energy Regulatory Commission"
            isUnknown={fercregulated === 0}
          >
            {FERC_REGULATED[fercregulated].toLowerCase()}
          </Field>
        </Entry>
      ) : null}

      {stateregulated !== null && stateregulated !== -1 ? (
        <Entry>
          <Field
            label="Regulated at the state level"
            isUnknown={stateregulated === 0}
          >
            {STATE_REGULATED[stateregulated].toLowerCase()}
          </Field>
        </Entry>
      ) : null}

      {fedregulatoryagency ? (
        <Entry>
          <Field label="Federal regulatory agency">{fedregulatoryagency}</Field>
        </Entry>
      ) : null}

      {waterright !== null && waterright > 0 ? (
        <Entry>
          <Field label="Has an associated water right">
            {WATER_RIGHT[waterright].toLowerCase()}
          </Field>
        </Entry>
      ) : null}

      {fatality > 0 ? (
        <Entry>
          <Field label="Number of fatalities recorded">
            {formatNumber(fatality)}
          </Field>
          <Text sx={{ fontSize: 0, color: 'grey.7' }}>
            (based on data provided by{' '}
            <OutboundLink to="https://krcproject.groups.et.byu.net/browse.php">
              Fatalities at Submerged Hydraulic Jumps
            </OutboundLink>
            )
          </Text>
        </Entry>
      ) : null}

      {costmean && costmean > 0 ? (
        <Entry>
          <Field label="Estimated cost of removal">
            ${formatNumber(costmean)} (average)
            <br /> (${formatNumber(costlower)} - ${formatNumber(costupper)})
          </Field>
          <Text sx={{ mt: '0.5rem', fontSize: 0, color: 'grey.7' }}>
            Note: costs are modeled based on dam characteristics and are a very
            rough estimate only; please use with caution. Source: Jumani et. al.
            (in prep).
          </Text>
        </Entry>
      ) : null}

      {ejtract || ejtribal ? (
        <Entry>
          <Field label="Climate and environmental justice">
            {ejtract ? 'within a disadvantaged census tract' : null}
            {ejtract && ejtribal ? ', ' : null}
            {ejtribal ? 'within a tribal community' : null}
          </Field>
        </Entry>
      ) : null}

      {fishhabitatpartnership ? (
        <Entry>
          <Text>Fish Habitat Partnerships working in this area:</Text>
          <Text sx={{ mt: '0.25rem', ml: '1rem' }}>
            {fishhabitatpartnership.split(',').map((code, i) => (
              <React.Fragment key={code}>
                {i > 0 ? ', ' : null}
                <OutboundLink to={FISH_HABITAT_PARTNERSHIPS[code].url}>
                  {FISH_HABITAT_PARTNERSHIPS[code].name}
                </OutboundLink>
              </React.Fragment>
            ))}
          </Text>
        </Entry>
      ) : null}

      {nativeterritories ? (
        <Entry>
          <Text>Within the following native territories:</Text>
          <Text sx={{ mt: '0.25rem', ml: '1rem' }}>{nativeterritories}</Text>
          <Text sx={{ fontSize: 0, color: 'grey.7', ml: '1rem' }}>
            (based on data provided by{' '}
            <OutboundLink to="https://native-land.ca/">
              Native Land Digital
            </OutboundLink>
            )
          </Text>
        </Entry>
      ) : null}
    </>
  )
}

LocationInfo.propTypes = {
  annualflow: PropTypes.number,
  barrierType: PropTypes.string.isRequired,
  reachName: PropTypes.string,
  huc12: PropTypes.string.isRequired,
  basin: PropTypes.string.isRequired,
  subwatershed: PropTypes.string.isRequired,
  ownertype: PropTypes.number,
  barrierownertype: PropTypes.number,
  fercregulated: PropTypes.number,
  stateregulated: PropTypes.number,
  fedregulatoryagency: PropTypes.string,
  waterright: PropTypes.number,
  costlower: PropTypes.number,
  costmean: PropTypes.number,
  costupper: PropTypes.number,
  ejtract: PropTypes.bool,
  ejtribal: PropTypes.bool,
  fishhabitatpartnership: PropTypes.string,
  nativeterritories: PropTypes.string,
  intermittent: PropTypes.number,
  storagevolume: PropTypes.number,
  streamorder: PropTypes.number,
  streamsizeclass: PropTypes.string,
  waterbodysizeclass: PropTypes.number,
  waterbodykm2: PropTypes.number,
  fatality: PropTypes.number,
}

LocationInfo.defaultProps = {
  annualflow: null,
  reachName: null,
  ownertype: 0,
  barrierownertype: 0,
  fercregulated: null,
  stateregulated: null,
  fedregulatoryagency: null,
  waterright: null,
  costlower: 0,
  costmean: 0,
  costupper: 0,
  ejtract: false,
  ejtribal: false,
  fishhabitatpartnership: null,
  nativeterritories: null,
  intermittent: 0,
  storagevolume: null,
  streamorder: 0,
  streamsizeclass: null,
  waterbodysizeclass: null,
  waterbodykm2: null,
  fatality: 0,
}

export default LocationInfo
