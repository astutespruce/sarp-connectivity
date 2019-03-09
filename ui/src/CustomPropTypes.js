import PropTypes from "prop-types"
import ImmutablePropTypes from "react-immutable-proptypes"

// At minimum, a feature must have an id
export const FeaturePropType = ImmutablePropTypes.mapContains({
    id: PropTypes.oneOfType([PropTypes.string, PropTypes.number])
})

export const SearchFeaturePropType = ImmutablePropTypes.mapContains({
    id: PropTypes.string,
    layer: PropTypes.string,
    bbox: ImmutablePropTypes.listOf(PropTypes.number),
    maxZoom: PropTypes.number
})

export const BarrierPropType = PropTypes.shape({
    name: PropTypes.string,
    County: PropTypes.string,
    State: PropTypes.string
    // TODO: other props
})

export const ScoresPropType = PropTypes.shape({
    gainmiles: PropTypes.number,
    landcover: PropTypes.number,
    sinuosity: PropTypes.number,
    sizeclasses: PropTypes.number,
    nc: PropTypes.number,
    wc: PropTypes.number,
    ncwc: PropTypes.number
})

export const LocationPropType = PropTypes.shape({
    latitude: PropTypes.number,
    longitude: PropTypes.number,
    timestamp: PropTypes.number
})
