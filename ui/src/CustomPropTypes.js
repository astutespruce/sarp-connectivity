import PropTypes from "prop-types"
import ImmutablePropTypes from "react-immutable-proptypes"

// At minimum, a feature must have an id
export const FeaturePropType = ImmutablePropTypes.mapContains({
    id: PropTypes.oneOfType([PropTypes.string, PropTypes.number]).isRequired,
    layerId: PropTypes.string.isRequired
})

export const LabelPointPropType = PropTypes.shape({
    point: PropTypes.arrayOf(PropTypes.number.isRequired).isRequired,
    label: PropTypes.oneOfType([PropTypes.number, PropTypes.string])
})

export const BarrierPropType = PropTypes.shape({
    name: PropTypes.string,
    county: PropTypes.string.isRequired,
    state: PropTypes.string.isRequired
    // TODO: other props
})

export const PrioritiesPropType = PropTypes.shape({
    nc: PropTypes.number.isRequired,
    wc: PropTypes.number.isRequired,
    ncwc: PropTypes.number.isRequired
})

export const BarrierPrioritiesPropType = PropTypes.shape({
    se: PrioritiesPropType.isRequired,
    state: PrioritiesPropType.isRequired,
    custom: PrioritiesPropType
})

export const MetricsPropType = PropTypes.shape({
    length: PropTypes.number.isRequired,
    upstreamMiles: PropTypes.number.isRequired,
    downstreamMiles: PropTypes.number.isRequired,
    sinuosity: PropTypes.number.isRequired,
    sizeclasses: PropTypes.number.isRequired
})

export const MetricScoresPropType = PropTypes.shape({
    length: PropTypes.number,
    sinuosity: PropTypes.number,
    landcover: PropTypes.number,
    sizeclasses: PropTypes.number
})
