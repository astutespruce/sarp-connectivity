import React, { useState } from 'react'
import PropTypes from 'prop-types'

import { Button, Checkbox } from 'components/Button'
import { OutboundLink } from 'components/Link'
import { HelpText } from 'components/Text'
import { Box, Flex } from 'components/Grid'
import styled, { themeGet } from 'style'

const Wrapper = styled(Box).attrs({ pt: '1rem' })`
  max-width: 600px;
`

const Row = styled(Box)``

const Buttons = styled(Flex).attrs({
  justifyContent: 'space-between',
  alignItems: 'center',
  mt: '1rem',
  pt: '1rem',
})`
  border-top: 1px solid ${themeGet('colors.grey.200')};
`

const Options = ({ barrierType }) => {
  const [includeUnranked, setIncludeUnranked] = useState(false)

  const handleChange = checked => {
    console.log('checkbox value', checked)
    setIncludeUnranked(checked)
  }

  const handleCancel = () => {
    console.log('cancel')
  }

  const handleDownload = () => {
    console.log('Download')
  }

  return (
    <Wrapper>
      <Row>
        <Checkbox
          id="unranked"
          label={`Include unranked ${barrierType}?`}
          checked={includeUnranked}
          onChange={handleChange}
        />
        {/* <Checkbox
          name="include_unranked"
          checked={includeUnranked}
          onChange={handleChange}
        />
        <Label htmlFor="include_unranked">
          Include unranked {barrierType}?
        </Label> */}
        <HelpText mt="0.5rem" ml="2rem">
          This will include {barrierType} within your selected geographic area
          that were not prioritized in your analysis. These include any{' '}
          {barrierType} that were not located on the aquatic network or that you
          filtered out during your prioritization.
          {barrierType === 'barriers' &&
            '  These data only include road-related barriers that have been assessed for impacts to aquatic organisms.'}
        </HelpText>
      </Row>

      <HelpText fontSize="small" mt="2rem">
        By downloading these data, you agree to the{' '}
        <OutboundLink to="/terms" target="_blank">
          Terms of Use
        </OutboundLink>
        , which includes providing credit to SARP for any use of the data
        including publication, reports, presentations, or projects. Please see
        the <b>TERMS_OF_USE.txt</b> file in your download for the appropriate
        citation and more information.
      </HelpText>

      <Buttons>
        <Button onClick={handleCancel}>Cancel</Button>
        <Button primary onClick={handleDownload}>
          Download
        </Button>
      </Buttons>
    </Wrapper>
  )
}

Options.propTypes = {
  barrierType: PropTypes.string,
}

Options.defaultProps = {
  barrierType: 'dams',
}

export default Options
