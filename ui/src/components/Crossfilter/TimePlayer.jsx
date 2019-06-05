import React, { useState, useContext, memo } from 'react'
import PropTypes from 'prop-types'
import { FaPlayCircle, FaPauseCircle, FaRegTimesCircle } from 'react-icons/fa'
import { Set } from 'immutable'

import { Box, Flex, Columns, Column } from 'components/Grid'
import { useInterval } from 'util/time'
import styled, { themeGet } from 'style'

import { Context } from './Context'
import { SET_FILTER } from './Crossfilter'

const SPEED_INCREMENT = 250

const Wrapper = styled(Columns).attrs({
  alignItems: 'center',
  px: '1rem',
  py: '0.5rem',
})`
  background: ${themeGet('colors.grey.200')};
`

const RightColumn = styled(Column)`
  display: flex;
  justify-content: flex-end;
  align-items: center;
`

const buttonSize = '1.5em'

const PlayButton = styled(FaPlayCircle)`
  height: ${buttonSize};
  width: ${buttonSize};
  cursor: pointer;
`

const PauseButton = styled(FaPauseCircle)`
  height: ${buttonSize};
  width: ${buttonSize};
  cursor: pointer;
`

const StopButton = styled(FaRegTimesCircle)`
  height: ${buttonSize};
  width: ${buttonSize};
  cursor: pointer;
`

const TimestepLabel = styled(Box).attrs({ mx: '0.5em' })`
  font-size: 0.8rem;
  color: ${themeGet('colors.grey.600')};
`

const SpeedLabel = styled.div`
  font-size: 0.8rem;
  color: ${themeGet('colors.grey.600')};
`

const SpeedSlider = styled.input.attrs({
  type: 'range',
  min: SPEED_INCREMENT,
  max: SPEED_INCREMENT * 10,
  step: SPEED_INCREMENT,
})`
  width: 60px;
  margin: 0 0.25em;
`

const TimePlayer = ({ timesteps, timestepLabels }) => {
  const [speed, setSpeed] = useState(1000) // in seconds
  const [isPlaying, setIsPlaying] = useState(false)
  const [idx, setIdx] = useState(0)
  const { state, dispatch } = useContext(Context)

  const hasFilter = state.get('filters').get('timestep', Set()).size > 0

  useInterval(
    () => {
      setIdx(prevIdx => {
        const nextIdx = prevIdx < timesteps.length - 1 ? prevIdx + 1 : 0
        setTimestepFilter(timesteps[nextIdx])
        return nextIdx
      })
    },
    isPlaying ? speed : null
  )

  // set timestep to null where filter should be reset
  const setTimestepFilter = t => {
    const filterValue = t === null ? Set() : Set([t])

    dispatch({
      type: SET_FILTER,
      payload: {
        field: 'timestep',
        filterValue,
      },
    })
  }

  const play = () => {
    setIsPlaying(true)
    setTimestepFilter(timesteps[idx])
  }

  const pause = () => {
    setIsPlaying(false)
  }

  const stop = () => {
    setIsPlaying(false)
    setTimestepFilter(null)
  }

  const handleSpeedChange = ({ target: { value } }) => {
    setSpeed(SPEED_INCREMENT * 11 - value)
  }

  return (
    <Wrapper>
      <Column>
        <Flex alignItems="center">
          <div>Play time series:&nbsp;</div>
          {isPlaying ? (
            <PauseButton onClick={pause} />
          ) : (
            <>
              <PlayButton onClick={play} />
              {hasFilter && <StopButton onClick={stop} />}
            </>
          )}
          {isPlaying ? (
            <TimestepLabel>{timestepLabels[idx]}</TimestepLabel>
          ) : null}
        </Flex>
      </Column>
      <RightColumn>
        <SpeedLabel>slower</SpeedLabel>
        <SpeedSlider
          value={SPEED_INCREMENT * 11 - speed}
          onChange={handleSpeedChange}
        />
        <SpeedLabel>faster</SpeedLabel>
      </RightColumn>
    </Wrapper>
  )
}

TimePlayer.propTypes = {
  timesteps: PropTypes.arrayOf(PropTypes.number).isRequired,
  timestepLabels: PropTypes.arrayOf(PropTypes.string).isRequired,
}

// only render once at mount
export default memo(TimePlayer, () => true)
