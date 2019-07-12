import PropTypes from 'prop-types'

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