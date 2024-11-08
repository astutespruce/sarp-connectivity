import React from 'react'
import PropTypes from 'prop-types'
import { Text } from '@react-pdf/renderer'

import {
  barrierTypeLabelSingular,
  STREAM_SIZECLASS,
  STREAM_SIZECLASS_DRAINAGE_AREA,
  WATERBODY_SIZECLASS,
} from 'config'
import { formatNumber } from 'util/format'

import { Entry, Entries, Section } from './elements'

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
  ...props
}) => {
  const barrierTypeLabel = barrierTypeLabelSingular[barrierType]

  const hasRiver =
    river &&
    river !== '"' &&
    river !== 'null' &&
    river.toLowerCase() !== 'unknown' &&
    river.toLowerCase() !== 'unnamed'

  return (
    <Section
      title="Location within the aquatic network"
      {...props}
      wrap={false}
    >
      <Entries>
        <Entry>
          <Text>
            {hasRiver ? `On ${river} in` : 'Within'} {subwatershed}{' '}
            Subwatershed, {subbasin} Subbasin
          </Text>
          <Text>HUC12: {huc12}</Text>
        </Entry>

        {wildscenicriver ? (
          <Entry>
            <Text>
              Near{' '}
              {wildscenicriver
                .split(', ')
                .map((name) => `${name} Wild & Scenic River`)
                .join(', ')}{' '}
              (within 250 meters)
            </Text>
          </Entry>
        ) : null}

        {intermittent === 1 ? (
          <Entry>
            <Text>
              This {barrierTypeLabel} is located on a reach that has
              intermittent or ephemeral flow
            </Text>
          </Entry>
        ) : null}

        {canal === 1 ? (
          <Entry>
            <Text>This {barrierTypeLabel} is located on a canal or ditch</Text>
          </Entry>
        ) : null}

        {barrierType === 'dams' &&
        waterbodysizeclass !== null &&
        waterbodysizeclass > 0 ? (
          <Entry>
            <Text>
              This {barrierTypeLabel} is associated with a{' '}
              {WATERBODY_SIZECLASS[waterbodysizeclass]
                .split(' (')[0]
                .toLowerCase()}{' '}
              {formatNumber(waterbodyacres)} acres.
            </Text>
          </Entry>
        ) : null}

        {streamorder > 0 ? (
          <Entry>
            <Text>Stream order (NHD modified Strahler): {streamorder}</Text>
          </Entry>
        ) : null}

        {streamsizeclass ? (
          <Entry>
            <Text>
              Stream size class: {STREAM_SIZECLASS[streamsizeclass]} (drainage
              area: {STREAM_SIZECLASS_DRAINAGE_AREA[streamsizeclass]})
            </Text>
          </Entry>
        ) : null}

        {annualflow !== null && annualflow >= 0 ? (
          <Entry>
            <Text>
              Stream reach annual flow rate: {formatNumber(annualflow)} CFS
            </Text>
          </Entry>
        ) : null}
      </Entries>
    </Section>
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
}

export default Location
