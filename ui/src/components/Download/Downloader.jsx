import React, { useState, useEffect } from 'react'
import PropTypes from 'prop-types'
import { FaDownload } from 'react-icons/fa'

import { getDownloadURL } from 'components/Data'
import { OutboundLink } from 'components/Link'
import { HelpText } from 'components/Text'
import { Box, Flex } from 'components/Grid'
import { Button } from 'components/Button'
import Modal from 'components/Modal'
import { getFromStorage } from 'util/dom'
import styled, { themeGet } from 'style'

import UserInfoForm, { FIELDS } from './UserInfoForm'
import DownloadOptions from './Options'

const Content = styled(Box).attrs({ pt: '1rem' })`
  max-width: 600px;
`

const Buttons = styled(Flex).attrs({
  justifyContent: 'space-between',
  alignItems: 'center',
  mt: '1rem',
  pt: '1rem',
})`
  border-top: 1px solid ${themeGet('colors.grey.200')};
`

export const DownloadIcon = styled(FaDownload)`
  height: 1.2em;
  width: 1.2em;
  margin-right: 0.5em;
`

const DownloadButton = styled(Button).attrs({ primary: true })`
  display: flex;
  align-items: center;
`

const DownloadLink = styled.span`
  color: ${themeGet('colors.link')};
  cursor: pointer;

  &:hover {
    text-decoration: underline;
  }
`

const Downloader = ({ barrierType, config, customRank, asButton, label }) => {
  const [isOpen, setIsOpen] = useState(false)
  const [haveUserInfo, setHaveUserInfo] = useState(false)
  const [downloadOptions, setDownloadOptions] = useState({ unranked: false })

  useEffect(() => {
    // If the user previously entered their contact info, don't ask them for it again
    const formData = getFromStorage('downloadForm')
    if (formData && formData[FIELDS.email]) {
      setHaveUserInfo(true)
    }
  }, [isOpen])

  const handleShow = () => {
    setIsOpen(true)
  }

  const handleClose = () => {
    setIsOpen(false)
  }

  const handleDownloadOptionsChange = options => {
    setDownloadOptions(options)
  }

  const handleUserInfoContinue = () => {
    // Note: this might be called if there was an error submitting the user info, and we decided to let them continue anyway
    setHaveUserInfo(true)
  }

  const handleDownload = () => {
    const { layer, summaryUnits, filters, scenario } = config

    const downloadURL = getDownloadURL({
      barrierType,
      layer,
      summaryUnits,
      filters,
      includeUnranked: downloadOptions.unranked,
      sort: scenario.toUpperCase(),
      customRank,
    })

    window.open(downloadURL)
    setIsOpen(false)
  }

  const showUserInfoForm = isOpen && !haveUserInfo
  const showDownloadPopup = isOpen && haveUserInfo

  const labelText = label || `Download ${barrierType}`

  return (
    <>
      {asButton ? (
        <DownloadButton onClick={handleShow} fontSize="1.1em">
          <DownloadIcon />
          <div>{labelText}</div>
        </DownloadButton>
      ) : (
        <DownloadLink onClick={handleShow}>{labelText}</DownloadLink>
      )}

      {showUserInfoForm && (
        <Modal title="Please tell us about yourself" onClose={handleClose}>
          <UserInfoForm
            onCancel={handleClose}
            onContinue={handleUserInfoContinue}
          />
        </Modal>
      )}

      {showDownloadPopup && (
        <Modal
          title={`Download ${customRank ? 'prioritized' : ''} ${barrierType}`}
          onClose={handleClose}
        >
          <Content>
            <DownloadOptions
              barrierType={barrierType}
              options={downloadOptions}
              customRank={customRank}
              onChange={handleDownloadOptionsChange}
            />

            <HelpText fontSize="small" mt="2rem">
              By downloading these data, you agree to the{' '}
              <OutboundLink to="/terms" target="_blank">
                Terms of Use
              </OutboundLink>
              , which includes providing credit to SARP for any use of the data
              including publication, reports, presentations, or projects. Please
              see the <b>TERMS_OF_USE.txt</b> file in your download for the
              appropriate citation and more information.
            </HelpText>
          </Content>

          <Buttons>
            <Button onClick={handleClose}>Cancel</Button>
            <DownloadButton onClick={handleDownload}>
              <DownloadIcon />
              <div>Download {barrierType}</div>
            </DownloadButton>
          </Buttons>
        </Modal>
      )}
    </>
  )
}

Downloader.propTypes = {
  barrierType: PropTypes.string.isRequired,
  config: PropTypes.shape({
    layer: PropTypes.string.isRequired,
    summaryUnits: PropTypes.arrayOf(
      PropTypes.shape({ id: PropTypes.string.isRequired })
    ).isRequired,
    filters: PropTypes.object,
    scenario: PropTypes.string.isRequired,
  }).isRequired,
  customRank: PropTypes.bool,
  asButton: PropTypes.bool,
  label: PropTypes.string,
}

Downloader.defaultProps = {
  customRank: false,
  label: null,
  asButton: true,
}

export default Downloader
