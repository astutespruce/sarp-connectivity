import React from 'react'
import PropTypes from 'prop-types'
import { Text } from 'theme-ui'

import {
  barrierTypeLabelSingular,
  OWNERTYPE,
  BARRIEROWNERTYPE,
  STREAM_SIZECLASS,
  STREAM_SIZECLASS_DRAINAGE_AREA,
  WATERBODY_SIZECLASS,
} from 'config'
import { Entry, Field } from 'components/Sidebar'
import { formatNumber } from 'util/format'
import { isEmptyString } from 'util/string'

const LocationInfo = ({
  barrierType,
  reachName,
  HUC12,
  HUC8Name,
  HUC12Name,
  ownertype,
  barrierownertype,
  intermittent,
  streamorder,
  streamsizeclass,
  waterbodysizeclass,
  waterbodykm2,
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
          {hasReachName ? `On ${reachName} in` : 'Within'} {HUC12Name}{' '}
          Subwatershed, {HUC8Name} Subbasin{' '}
        </Text>
        <Text sx={{ fontSize: 0, color: 'grey.8' }}>(HUC12: {HUC12})</Text>
      </Entry>
      {intermittent === 1 ? (
        <Entry>This {barrierTypeLabel} is on an intermittent reach</Entry>
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
      {ownertype !== null && ownertype > 0 ? (
        <Entry>
          <Field label="Conservation land type">{OWNERTYPE[ownertype]}</Field>
        </Entry>
      ) : null}
      {barrierownertype !== null && barrierownertype > 0 ? (
        <Entry>
          <Field label="Barrier ownership type">
            {BARRIEROWNERTYPE[barrierownertype]}
          </Field>{' '}
        </Entry>
      ) : null}
    </>
  )
}

LocationInfo.propTypes = {
  barrierType: PropTypes.string.isRequired,
  reachName: PropTypes.string,
  HUC12: PropTypes.string.isRequired,
  HUC8Name: PropTypes.string.isRequired,
  HUC12Name: PropTypes.string.isRequired,
  ownertype: PropTypes.number,
  barrierownertype: PropTypes.number,
  intermittent: PropTypes.number,
  streamorder: PropTypes.number,
  streamsizeclass: PropTypes.string,
  waterbodysizeclass: PropTypes.number,
  waterbodykm2: PropTypes.number,
}

LocationInfo.defaultProps = {
  reachName: null,
  ownertype: 0,
  barrierownertype: 0,
  intermittent: 0,
  streamorder: 0,
  streamsizeclass: null,
  waterbodysizeclass: null,
  waterbodykm2: null,
}

export default LocationInfo
