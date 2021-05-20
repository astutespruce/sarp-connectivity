import React, { useState, useEffect } from 'react'
import PropTypes from 'prop-types'
import { Download as DownloadIcon } from '@emotion-icons/fa-solid'
import { Box, Button, Flex, Paragraph, Text } from 'theme-ui'

import { getDownloadURL } from 'components/Data'
import { OutboundLink } from 'components/Link'
import Modal from 'components/Modal'
import { getFromStorage } from 'util/dom'
import { trackDownload } from 'util/analytics'

import UserInfoForm, { FIELDS } from './UserInfoForm'
import DownloadOptions from './Options'

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

  const handleDownloadOptionsChange = (options) => {
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

    trackDownload({
      barrierType,
      unitType: layer,
      details: `ids: [${
        summaryUnits ? summaryUnits.map(({ id }) => id) : 'none'
      }], filters: ${
        filters ? Object.keys(filters) : 'none'
      }, scenario: ${scenario}, include unranked: ${downloadOptions.unranked}`,
    })
  }

  const showUserInfoForm = isOpen && !haveUserInfo
  const showDownloadPopup = isOpen && haveUserInfo

  const labelText = label || `Download ${barrierType}`

  return (
    <>
      {asButton ? (
        <Button onClick={handleShow} sx={{ fontSize: '1.1em' }}>
          <Flex>
            <DownloadIcon size="1.2em" style={{ marginRight: '0.5rem' }} />
            <Text>{labelText}</Text>
          </Flex>
        </Button>
      ) : (
        <Text
          as="span"
          onClick={handleShow}
          sx={{
            display: 'inline-block',
            color: 'link',
            cursor: 'pointer',
            '&:hover': {
              textDecoration: 'underline',
            },
          }}
        >
          {labelText}
        </Text>
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
          <Box sx={{ maxWidth: '600px' }}>
            <DownloadOptions
              barrierType={barrierType}
              options={downloadOptions}
              customRank={customRank}
              onChange={handleDownloadOptionsChange}
            />

            <Paragraph variant="help" sx={{ mt: '2rem' }}>
              By downloading these data, you agree to the{' '}
              <OutboundLink to="/terms" target="_blank">
                Terms of Use
              </OutboundLink>
              , which includes providing credit to SARP for any use of the data
              including publication, reports, presentations, or projects. Please
              see the <b>TERMS_OF_USE.txt</b> file in your download for the
              appropriate citation and more information.
              <br />
              <br />
              Coordinates are in WGS 1984.
            </Paragraph>
          </Box>

          <Flex
            sx={{
              alignItems: 'center',
              justifyContent: 'space-between',
              mt: '1rem',
              pt: '1rem',
              borderTop: '1px solid',
              borderTopColor: 'grey.2',
            }}
          >
            <Button variant="secondary" onClick={handleClose}>
              Cancel
            </Button>
            <Button onClick={handleDownload}>
              <Flex sx={{ alignItems: 'center' }}>
                <DownloadIcon size="1.2em" style={{ marginRight: '0.5rem' }} />
                <Text>Download {barrierType}</Text>
              </Flex>
            </Button>
          </Flex>
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
