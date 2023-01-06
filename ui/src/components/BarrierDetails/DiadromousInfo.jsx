import React from 'react'
import PropTypes from 'prop-types'

import { Entry, Field } from 'components/Sidebar'
import { formatNumber } from 'util/format'

const DiadromousInfo = ({
  barrierType,
  milestooutlet,
  totaldownstreamdams,
  totaldownstreamsmallbarriers,
  totaldownstreamwaterfalls,
}) => (
  <>
    <Entry>
      <Field label="Miles downstream to the ocean">
        {formatNumber(milestooutlet)}
      </Field>
    </Entry>
    <Entry>
      <Field label="Number of dams downstream">{totaldownstreamdams}</Field>
    </Entry>
    {barrierType === 'small_barriers' ? (
      <Entry>
        <Field label="Number of inventoried road-related barriers downstream">
          {totaldownstreamsmallbarriers}
        </Field>
      </Entry>
    ) : null}
    <Entry>
      <Field label="Number of waterfalls downstream">
        {totaldownstreamwaterfalls}
      </Field>
    </Entry>
  </>
)

DiadromousInfo.propTypes = {
  barrierType: PropTypes.string.isRequired,
  milestooutlet: PropTypes.number,
  totaldownstreamdams: PropTypes.number,
  totaldownstreamsmallbarriers: PropTypes.number,
  totaldownstreamwaterfalls: PropTypes.number,
}

DiadromousInfo.defaultProps = {
  milestooutlet: 0,
  totaldownstreamdams: 0,
  totaldownstreamsmallbarriers: 0,
  totaldownstreamwaterfalls: 0,
}

export default DiadromousInfo
