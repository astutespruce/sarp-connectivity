import React, { useState, useEffect } from 'react'
import PropTypes from 'prop-types'
import { FaDownload } from 'react-icons/fa'

import { OutboundLink } from 'components/Link'
import { HelpText } from 'components/Text'
import { Box, Flex } from 'components/Grid'
import { Button } from 'components/Button'
import { UserInfoForm, DownloadOptions } from 'components/Download'
import Modal from 'components/Modal'
import { getFromStorage } from 'util/dom'

import styled, { themeGet } from 'style'

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

const DownloadPopup = ({ barrierType, downloadURL }) => {
  const [isOpen, setIsOpen] = useState(false)
  const [haveUserInfo, setHaveUserInfo] = useState(false)
  const [downloadOptions, setDownloadOptions] = useState({ unranked: false })

  useEffect(() => {
    const formData = getFromStorage('downloadForm')
    console.log(formData)
    if (formData && formData.email) {
      setHaveUserInfo(true)
    }
  }, [])

  const handleShow = () => {
    setIsOpen(true)
  }

  const handleClose = () => {
    setIsOpen(false)
  }

  const handleDownloadOptionsChange = options => {
    setDownloadOptions(options)
    console.log('download options', options)
  }

  const handleUserInfoContinue = () => {
    // Note: this might be called if there was an error submitting the user info, and we decided to let them continue anyway

    // FIXME: need better prop
    setHaveUserInfo(true)
  }

  const handleDownload = () => {
    // TODO: add unranked to URL
    window.open(downloadURL)
  }

  const showUserInfoForm = isOpen && !haveUserInfo
  const showDownloadPopup = isOpen && haveUserInfo

  return (
    <>
      <DownloadButton onClick={handleShow} fontSize="1.1em">
        <DownloadIcon />
        <div>Download {barrierType}</div>
      </DownloadButton>

      {showUserInfoForm && (
        <Modal title="Please tell us about yourself" onClose={handleClose}>
          <UserInfoForm
            onCancel={handleClose}
            onContinue={handleUserInfoContinue}
          />
        </Modal>
      )}

      {showDownloadPopup && (
        <Modal title="Download prioritized barriers" onClose={handleClose}>
          <Content>
            <DownloadOptions
              barrierType={barrierType}
              options={downloadOptions}
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

DownloadPopup.propTypes = {
  barrierType: PropTypes.string.isRequired,
  downloadURL: PropTypes.string.isRequired,
}

export default DownloadPopup
