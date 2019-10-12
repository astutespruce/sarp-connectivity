import PropTypes from 'prop-types'

export const BarrierPropType = PropTypes.shape({
  id: PropTypes.number.isRequired,
  sarpid: PropTypes.string.isRequired,
  name: PropTypes.string,
  County: PropTypes.string,
  State: PropTypes.string,
  // TODO: other props
})

export const ScorePropType = PropTypes.shape({
  score: PropTypes.number,
  tier: PropTypes.number,
})

export const ScoresPropType = PropTypes.shape({
  nc: ScorePropType,
  wc: ScorePropType,
  ncwc: ScorePropType,
})
