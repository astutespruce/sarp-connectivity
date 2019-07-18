import React from 'react'
import PropTypes from 'prop-types'
import { FaDownload } from 'react-icons/fa'

import { OutboundLink } from 'components/Link'
import { PrimaryButton } from 'components/Button'
import styled from 'style'

const Button = styled(PrimaryButton)`
  font-size: 1.1em;
`

const Link = styled(OutboundLink)`
  color: #fff;
  display: flex;
  align-items: center;
`

export const DownloadIcon = styled(FaDownload)`
  height: 1.2em;
  width: 1.2em;
  margin-right: 0.5em;
`

const DownloadButton = ({ label, downloadURL, onClick }) => (
  <Button onClick={onClick}>
    <Link to={downloadURL}>
      <DownloadIcon />
      <div>{label}</div>
    </Link>
  </Button>
)

DownloadButton.propTypes = {
  label: PropTypes.string.isRequired,
  downloadURL: PropTypes.string.isRequired,
  onClick: PropTypes.func.isRequired,
}

export default DownloadButton
