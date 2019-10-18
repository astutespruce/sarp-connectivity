import React from 'react'
import PropTypes from 'prop-types'
import { FaDownload } from 'react-icons/fa'

import { OutboundLink } from 'components/Link'
import { PrimaryButton } from 'components/Button'
import styled from 'style'

const Button = styled(PrimaryButton)`
  font-size: 1.1em;
  display: flex;
  align-items: center;
`

const Link = styled(OutboundLink)`
  color: #fff;
`

export const DownloadIcon = styled(FaDownload)`
  height: 1.2em;
  width: 1.2em;
  margin-right: 0.5em;
`

const DownloadButton = ({ label, downloadURL, onClick }) => (
  <Link to={downloadURL}>
    <Button onClick={onClick}>
      <DownloadIcon />
      <div>{label}</div>
    </Button>
  </Link>
)

DownloadButton.propTypes = {
  label: PropTypes.string.isRequired,
  downloadURL: PropTypes.string.isRequired,
  onClick: PropTypes.func.isRequired,
}

export default DownloadButton
