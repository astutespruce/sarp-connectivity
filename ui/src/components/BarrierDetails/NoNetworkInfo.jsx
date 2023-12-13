import React from 'react'
import PropTypes from 'prop-types'
import { Paragraph, Text } from 'theme-ui'

import { barrierTypeLabels, barrierTypeLabelSingular } from 'config'
import { Entry } from 'components/Sidebar'

const NoNetworkInfo = ({
  barrierType,
  networkType,
  snapped,
  excluded,
  in_network_type,
  onloop,
  diversion,
}) => {
  const typeLabel = barrierTypeLabelSingular[barrierType]

  if (barrierType === 'road_crossings') {
    return (
      <Entry>
        This road-related barrier has not yet been assessed as a potential
        barrier for aquatic organisms, and has not been analyzed for aquatic
        network connectivity.
      </Entry>
    )
  }

  if (!snapped) {
    return (
      <Entry>
        This {typeLabel} is off-network and has no functional network
        information.
        <Paragraph variant="help" sx={{ mt: '1rem', fontSize: 0 }}>
          Not all {barrierTypeLabels[barrierType]} could be correctly snapped to
          the aquatic network for analysis. Please <b>contact us</b> to report
          an error or for assistance interpreting these results.
        </Paragraph>
      </Entry>
    )
  }

  if (excluded) {
    return (
      <Entry>
        This {typeLabel} was excluded from the connectivity analysis based on
        field reconnaissance, manual review of aerial imagery, or other
        information about this {typeLabel}.
      </Entry>
    )
  }

  if (onloop) {
    return (
      <Entry>
        <Text>
          This {typeLabel} was excluded from the connectivity analysis based on
          its position within the aquatic network.
        </Text>
        <Paragraph variant="help" sx={{ mt: '1rem', fontSize: 0 }}>
          This {typeLabel} was snapped to a secondary channel within the aquatic
          network according to the way that primary versus secondary channels
          are identified within the NHD High Resolution Plus dataset. This dam
          may need to be repositioned to occur on the primary channel in order
          to be included within the connectivity analysis. Please{' '}
          <b>contact us</b> to report an issue with this barrier.
        </Paragraph>
      </Entry>
    )
  }

  if (!in_network_type) {
    return (
      <Entry>
        <Text>
          This {typeLabel} is not included in this network scenario based on its
          passability
          {networkType === 'largefish_barriers'
            ? ' for large-bodied fish '
            : null}
          {networkType === 'smallfish_barriers'
            ? ' for small-bodied fish '
            : null}
          and has no functional network information.
        </Text>
      </Entry>
    )
  }

  return <Entry>No network information is available.</Entry>
}

NoNetworkInfo.propTypes = {
  barrierType: PropTypes.string.isRequired,
  networkType: PropTypes.string.isRequired,
  excluded: PropTypes.bool,
  in_network_type: PropTypes.bool,
  onloop: PropTypes.bool,
  snapped: PropTypes.bool,
  diversion: PropTypes.number,
}

NoNetworkInfo.defaultProps = {
  excluded: false,
  in_network_type: false,
  onloop: false,
  snapped: false,
  diversion: 0,
}

export default NoNetworkInfo
