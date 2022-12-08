import React from 'react'
import PropTypes from 'prop-types'
import { Text } from 'theme-ui'

import { OWNERTYPE, BARRIEROWNERTYPE } from 'config'
import { Entry, Field } from 'components/Sidebar'
import { isEmptyString } from 'util/string'

const LocationInfo = ({
  reachName,
  HUC12,
  HUC8Name,
  HUC12Name,
  ownertype,
  barrierownertype,
}) => {
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
  reachName: PropTypes.string,
  HUC12: PropTypes.string.isRequired,
  HUC8Name: PropTypes.string.isRequired,
  HUC12Name: PropTypes.string.isRequired,
  ownertype: PropTypes.number,
  barrierownertype: PropTypes.number,
}

LocationInfo.defaultProps = {
  reachName: null,
  ownertype: 0,
  barrierownertype: 0,
}

export default LocationInfo
