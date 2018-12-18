import PropTypes from "prop-types"
import ImmutablePropTypes from "react-immutable-proptypes"

// At minimum, a feature must have an id
export const FeaturePropType = ImmutablePropTypes.mapContains({
    id: PropTypes.oneOfType([PropTypes.string, PropTypes.number]).isRequired,
    layerId: PropTypes.string.isRequired
})

export const BarrierPropType = PropTypes.shape({
    Name: PropTypes.string,
    County: PropTypes.string.isRequired,
    State: PropTypes.string.isRequired
    // TODO: other props
})

export const ScoresPropType = PropTypes.shape({
    GainMiles: PropTypes.number,
    Landcover: PropTypes.number,
    Sinuosity: PropTypes.number,
    SizeClasses: PropTypes.number,
    NC: PropTypes.number,
    WC: PropTypes.number,
    NCWC: PropTypes.number
})
