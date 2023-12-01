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
    {totaldownstreamdams >= 0 ? (
      <Entry>
        <Field label="Number of dams downstream">
          {formatNumber(totaldownstreamdams)}
        </Field>
      </Entry>
    ) : null}
    {barrierType === 'small_barriers' && totaldownstreamsmallbarriers >= 0 ? (
      <Entry>
        <Field label="Number of assessed road-related barriers downstream">
          {formatNumber(totaldownstreamsmallbarriers)}
        </Field>
      </Entry>
    ) : null}
    {totaldownstreamwaterfalls >= 0 ? (
      <Entry>
        <Field label="Number of waterfalls downstream">
          {formatNumber(totaldownstreamwaterfalls)}
        </Field>
      </Entry>
    ) : null}
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
