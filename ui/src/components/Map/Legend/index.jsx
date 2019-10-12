import React, { useState } from 'react'
import PropTypes from 'prop-types'

import { Text, HelpText } from 'components/Text'
import { Flex, Box } from 'components/Grid'
import styled, { themeGet } from 'style'

import Circle from './Circle'
import { MapControlWrapper } from '../styles'

const Wrapper = styled(MapControlWrapper)`
  z-index: 1000;
  right: 10px;
  bottom: 24px;
  max-width: 160px;
  padding: 10px;
  box-shadow: 1px 1px 8px #333;
  cursor: pointer;

  &:hover {
    background: #fff;
  }
`

const Title = styled(Text).attrs({
  as: 'h5',
  fontSize: '1rem',
})`
  line-height: 1.2;
  margin-bottom: 0.25em;
`

const Patch = styled.div`
  width: 20px;
  height: 1em;
  border-color: ${themeGet('colors.grey.500')};
  border-width: 0 1px 1px 1px;
  border-style: solid;
`

const Label = styled.div`
  font-size: 0.75rem;
  margin-left: 0.5rem;
  line-height: 1;
  color: ${themeGet('colors.grey.700')};
`

const Divider = styled(Box).attrs({ mt: '0.5rem' })`
  border-top: 1px solid ${themeGet('colors.grey.100')};
`

const CircleRow = styled(Flex).attrs({ alignItems: 'flex-start', py: '0.5em' })`
  &:not(:first-child) {
    border-top: 1px solid ${themeGet('colors.grey.100')};
  }
`

const PatchRow = styled(Flex).attrs({ alignItems: 'center' })`
  &:first-child ${Patch} {
    border-radius: 3px 3px 0 0;
    border-top-width: 1px;
  }

  &:last-child ${Patch} {
    border-radius: 0 0 3px 3px;
  }
`

const Footnote = styled(HelpText)`
  font-size: 0.75rem;
  line-height: 1.2;
  margin-top: 0.5rem;
`

const Legend = ({ title, patches, circles, footnote }) => {
  const [isOpen, setIsOpen] = useState(true)

  if (!(patches || circles || footnote)) {
    return null
  }

  const toggleOpen = () => {
    setIsOpen(prevIsOpen => !prevIsOpen)
  }

  return (
    <Wrapper onClick={toggleOpen}>
      {isOpen ? (
        <>
          <Title>{title}</Title>

          {patches && (
            <div>
              {patches.map(({ color, label }) => (
                <PatchRow key={color}>
                  <Patch style={{ backgroundColor: color }} />
                  <Label>{label}</Label>
                </PatchRow>
              ))}
            </div>
          )}

          {patches && circles && <Divider />}

          {circles && (
            <div>
              {circles.map(point => (
                <CircleRow key={point.color}>
                  <Circle {...point} />
                  <Label>{point.label}</Label>
                </CircleRow>
              ))}
            </div>
          )}

          {footnote && <Footnote>{footnote}</Footnote>}
        </>
      ) : (
        <Title title="click to open legend">Legend</Title>
      )}
    </Wrapper>
  )
}

Legend.propTypes = {
  title: PropTypes.string,
  circles: PropTypes.arrayOf(
    PropTypes.shape({
      color: PropTypes.string.isRequired,
      label: PropTypes.string.isRequired,
      radius: PropTypes.number,
      borderWidth: PropTypes.number,
      borderColor: PropTypes.string,
    })
  ),
  patches: PropTypes.arrayOf(
    PropTypes.shape({
      color: PropTypes.string.isRequired,
      label: PropTypes.string.isRequired,
    })
  ),
  footnote: PropTypes.string,
}

Legend.defaultProps = {
  title: 'Legend',
  circles: null,
  patches: null,
  footnote: null,
}

export default Legend
