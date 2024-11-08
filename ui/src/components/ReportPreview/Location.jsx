import React from 'react'
import PropTypes from 'prop-types'
import { Box, Heading } from 'theme-ui'

import {
  barrierTypeLabelSingular,
  STREAM_SIZECLASS,
  STREAM_SIZECLASS_DRAINAGE_AREA,
  WATERBODY_SIZECLASS,
} from 'config'
import { formatNumber } from 'util/format'
import { Entry } from './elements'

const Location = ({
  barrierType,
  annualflow,
  river,
  intermittent,
  canal,
  subbasin,
  subwatershed,
  huc12,
  streamorder,
  streamsizeclass,
  waterbodyacres,
  waterbodysizeclass,
  wildscenicriver,
  sx,
}) => {
  const barrierTypeLabel = barrierTypeLabelSingular[barrierType]

  const hasRiver =
    river &&
    river !== '"' &&
    river !== 'null' &&
    river.toLowerCase() !== 'unknown' &&
    river.toLowerCase() !== 'unnamed'

  return (
    <Box sx={sx}>
      <Heading as="h3">Location within the aquatic network</Heading>

      <Entry>
        {hasRiver ? `On ${river} in` : 'Within'} {subwatershed} Subwatershed,{' '}
        {subbasin} Subbasin
        <br />
        HUC12: {huc12}
      </Entry>

      {wildscenicriver ? (
        <Entry>
          Near{' '}
          {wildscenicriver
            .split(', ')
            .map((name) => `${name} Wild & Scenic River`)
            .join(', ')}{' '}
          (within 250 meters)
        </Entry>
      ) : null}

      {intermittent === 1 ? (
        <Entry>
          This {barrierTypeLabel} is located on a reach that has intermittent or
          ephemeral flow
        </Entry>
      ) : null}

      {canal === 1 ? (
        <Entry>This {barrierTypeLabel} is located on a canal or ditch</Entry>
      ) : null}

      {streamorder > 0 ? (
        <Entry>Stream order (NHD modified Strahler): {streamorder}</Entry>
      ) : null}

      {streamsizeclass ? (
        <Entry>
          Stream size class: {STREAM_SIZECLASS[streamsizeclass]} (drainage area:{' '}
          {STREAM_SIZECLASS_DRAINAGE_AREA[streamsizeclass]})
        </Entry>
      ) : null}

      {annualflow !== null && annualflow >= 0 ? (
        <Entry>
          Stream reach annual flow rate: {formatNumber(annualflow)} CFS
        </Entry>
      ) : null}

      {barrierType === 'dams' &&
      waterbodysizeclass !== null &&
      waterbodysizeclass > 0 ? (
        <Entry>
          This {barrierTypeLabel} is associated with a{' '}
          {WATERBODY_SIZECLASS[waterbodysizeclass].split(' (')[0].toLowerCase()}{' '}
          ({formatNumber(waterbodyacres)} acres).
        </Entry>
      ) : null}
    </Box>
  )
}

Location.propTypes = {
  barrierType: PropTypes.string.isRequired,
  annualflow: PropTypes.number,
  river: PropTypes.string,
  intermittent: PropTypes.number,
  canal: PropTypes.number,
  subbasin: PropTypes.string,
  subwatershed: PropTypes.string,
  huc12: PropTypes.string,
  streamorder: PropTypes.number,
  streamsizeclass: PropTypes.string,
  waterbodyacres: PropTypes.number,
  waterbodysizeclass: PropTypes.number,
  wildscenicriver: PropTypes.string,
  sx: PropTypes.object,
}

Location.defaultProps = {
  annualflow: null,
  river: null,
  intermittent: 0,
  canal: 0,
  subbasin: null,
  subwatershed: null,
  huc12: null,
  streamorder: 0,
  streamsizeclass: null,
  waterbodyacres: -1,
  waterbodysizeclass: null,
  wildscenicriver: null,
  sx: null,
}

export default Location
