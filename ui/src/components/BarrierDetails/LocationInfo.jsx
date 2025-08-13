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
  STATES,
  TNC_COLDWATER_STATUS,
  TNC_RESILIENCE,
  TU_BROOK_TROUT_PORTFOLIO,
  WILDSCENIC_RIVER_LONG_LABELS,
} from 'config'
import { OutboundLink } from 'components/Link'
import { Entry, Field } from 'components/Sidebar'
import { formatNumber } from 'util/format'
import { isEmptyString } from 'util/string'
import { BarrierPropType, BarrierDefaultProps } from './proptypes'

const LocationInfo = ({
  annualflow,
  barrierType,
  river,
  huc12,
  basin,
  subwatershed,
  congressionaldistrict,
  ownertype,
  barrierownertype,
  fercregulated,
  stateregulated,
  nrcsdam,
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
  canal,
  storagevolume,
  streamorder,
  streamsizeclass,
  waterbodysizeclass,
  waterbodyacres,
  wilderness,
  wildscenicriver,
  yearsurveyed,
  resurveyed,
  fatality,
  cold,
  resilience,
  brooktroutportfolio,
}) => {
  const barrierTypeLabel = barrierTypeLabelSingular[barrierType]
  const hasRiverName =
    !isEmptyString(river) &&
    river.toLowerCase() !== 'unknown' &&
    river.toLowerCase() !== 'unnamed'

  return (
    <>
      {yearsurveyed !== 0 ? (
        <Entry>
          <Field label="Year surveyed">
            {yearsurveyed}
            {resurveyed !== 0 ? ' (resurveyed)' : null}
          </Field>
        </Entry>
      ) : null}

      <Entry>
        <Text sx={{ fontSize: 1 }}>
          {hasRiverName ? `On ${river} in` : 'Within'} {subwatershed}{' '}
          Subwatershed, {basin} Subbasin{' '}
        </Text>
        <Text sx={{ fontSize: 0, color: 'grey.8' }}>(HUC12: {huc12})</Text>
      </Entry>

      {wildscenicriver ? (
        <>
          <Entry>
            <Text>{WILDSCENIC_RIVER_LONG_LABELS[wildscenicriver]}</Text>
          </Entry>
        </>
      ) : null}

      {wilderness ? (
        <>
          <Entry>
            <Text>Within a designated wilderness area</Text>
          </Entry>
        </>
      ) : null}

      {intermittent === 1 ? (
        <Entry>This {barrierTypeLabel} is on an intermittent reach</Entry>
      ) : null}

      {canal === 1 ? (
        <Entry>This {barrierTypeLabel} is on canal or ditch</Entry>
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
          ({formatNumber(waterbodyacres)} acres)
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
              (drainage area: {STREAM_SIZECLASS_DRAINAGE_AREA[streamsizeclass]})
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
          <Field
            label="Barrier ownership type"
            isUnknown={barrierownertype === 0}
          >
            {BARRIEROWNERTYPE[barrierownertype].toLowerCase()}
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

      {nrcsdam === 1 ? <Entry>This is a NRCS flood control dam</Entry> : null}

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
            based on data provided by{' '}
            <OutboundLink to="https://krcproject.groups.et.byu.net/browse.php">
              Fatalities at Submerged Hydraulic Jumps
            </OutboundLink>
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

      {cold ? (
        <Entry>
          <Field label="Ability of the watershed to maintain cold water habitat">
            {TNC_COLDWATER_STATUS[cold]}
          </Field>
          <Text sx={{ mt: '0.5rem', fontSize: 0, color: 'grey.7' }}>
            based on The Nature Conservancy&apos;s cold water temperature score
            where this barrier occurs (TNC; March 2024).
          </Text>
        </Entry>
      ) : null}

      {resilience ? (
        <Entry>
          <Field label="Freshwater resilience">
            {TNC_RESILIENCE[resilience]}
          </Field>
          <Text sx={{ mt: '0.5rem', fontSize: 0, color: 'grey.7' }}>
            based on the The Nature Conservancy&apos;s freshwater resilience
            category of the watershed where this barrier occurs (v0.44).
          </Text>
        </Entry>
      ) : null}

      {brooktroutportfolio ? (
        <Entry>
          <Field label="Eastern brook trout conservation portfolio">
            {TU_BROOK_TROUT_PORTFOLIO[brooktroutportfolio]}
          </Field>
          <Text sx={{ mt: '0.5rem', fontSize: 0, color: 'grey.7' }}>
            based on the{' '}
            <OutboundLink to="https://www.tu.org/science/conservation-planning-and-assessment/conservation-portfolio/">
              brook trout conservation portfolio
            </OutboundLink>{' '}
            category of the watershed where this barrier occurs, as identified
            by Trout Unlimited (7/4/2022).
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
            based on data provided by{' '}
            <OutboundLink to="https://native-land.ca/">
              Native Land Digital
            </OutboundLink>
            .
          </Text>
        </Entry>
      ) : null}

      {congressionaldistrict ? (
        <Entry>
          <Field label="Congressional district">
            {STATES[congressionaldistrict.slice(0, 2)]} Congressional District{' '}
            {congressionaldistrict.slice(2)}
            <Text
              sx={{
                display: 'inline',
                fontSize: 0,
                color: 'grey.7',
                ml: '0.5rem',
              }}
            >
              (118th congress)
            </Text>
          </Field>
        </Entry>
      ) : null}
    </>
  )
}

LocationInfo.propTypes = {
  ...BarrierPropType,
  ownertype: PropTypes.number,
  barrierownertype: PropTypes.number,
  resurveyed: PropTypes.number,
  yearsurveyed: PropTypes.number,

  // dam specific fields
  costlower: PropTypes.number,
  costmean: PropTypes.number,
  costupper: PropTypes.number,
  fatality: PropTypes.number,
  fedregulatoryagency: PropTypes.string,
  fercregulated: PropTypes.number,
  nrcsdam: PropTypes.number,
  stateregulated: PropTypes.number,
  storagevolume: PropTypes.number,
  waterbodyacres: PropTypes.number,
  waterbodysizeclass: PropTypes.number,
  waterright: PropTypes.number,
}

LocationInfo.defaultProps = {
  ...BarrierDefaultProps,
  ownertype: 0,
  barrierownertype: 0,
  resurveyed: 0,
  yearsurveyed: 0,

  // dam specific fields
  costlower: 0,
  costmean: 0,
  costupper: 0,
  fatality: 0,
  fedregulatoryagency: null,
  fercregulated: null,
  nrcsdam: null,
  stateregulated: null,
  storagevolume: null,
  waterbodyacres: null,
  waterbodysizeclass: null,
  waterright: null,
}

export default LocationInfo
