import React from 'react'
import PropTypes from 'prop-types'

import { Text, HelpText } from 'components/Text'
import { Flex } from 'components/Grid'
import styled, { themeGet } from 'style'
import { MapControlWrapper } from './styles'

const Wrapper = styled(MapControlWrapper)`
  right: 10px;
  bottom: 24px;
  max-width: 160px;
  padding: 10px;
  box-shadow: 1px 1px 8px #333;

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

const Row = styled(Flex).attrs({ alignItems: 'center' })`
  &:first-child ${Patch} {
    border-radius: 3px 3px 0 0;
    border-width-top: 1px;
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

const Legend = ({ title, entries, footnote }) => (
  <Wrapper>
    <Title>{title}</Title>

    <div>
      {entries.map(({ color: backgroundColor, label }) => (
        <Row key={backgroundColor}>
          <Patch style={{ backgroundColor }} />
          <Label>{label}</Label>
        </Row>
      ))}
    </div>

    {footnote && <Footnote>{footnote}</Footnote>}
  </Wrapper>
)

Legend.propTypes = {
  title: PropTypes.string,
  entries: PropTypes.arrayOf(
    PropTypes.shape({
      color: PropTypes.string.isRequired,
      label: PropTypes.string.isRequired,
    })
  ).isRequired,
  footnote: PropTypes.string,
}

Legend.defaultProps = {
  title: 'Legend',
  footnote: null,
}

export default Legend
