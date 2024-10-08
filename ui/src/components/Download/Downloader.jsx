import React, { useState, useEffect } from 'react'
import PropTypes from 'prop-types'
import { Download as DownloadIcon } from '@emotion-icons/fa-solid'
import { Box, Button, Flex, Text } from 'theme-ui'

import { getDownloadURL } from 'components/Data'
import { OutboundLink } from 'components/Link'
import Modal from 'components/Modal'
import { barrierTypeLabels, siteMetadata } from 'config'
import { getFromStorage } from 'util/dom'
import { trackDownload } from 'util/analytics'

import UserInfoForm, { FIELDS } from './UserInfoForm'
import DownloadOptions from './Options'

const { apiHost } = siteMetadata

const Downloader = ({
  barrierType,
  config,
  customRank,
  asButton,
  label,
  disabled,
  showOptions,
  includeUnranked,
}) => {
  const [isOpen, setIsOpen] = useState(false)
  const [haveUserInfo, setHaveUserInfo] = useState(false)
  const [downloadOptions, setDownloadOptions] = useState({
    includeUnranked,
  })

  const barrierTypeLabel = barrierTypeLabels[barrierType]

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
    const { summaryUnits, filters, scenario } = config

    let downloadURL = null

    if (summaryUnits) {
      downloadURL = getDownloadURL({
        barrierType,
        summaryUnits,
        filters,
        includeUnranked:
          barrierType !== 'road_crossings'
            ? downloadOptions.includeUnranked
            : null,
        sort: scenario ? scenario.toUpperCase() : null,
        customRank,
      })
    } else {
      downloadURL = `${apiHost}/api/v1/internal/${barrierType}/csv/national`
    }

    window.open(downloadURL)
    setIsOpen(false)

    // track to Google analytics
    if (summaryUnits) {
      const formattedIds = Object.entries(summaryUnits)
        .map(([key, values]) => `${key}: ${values.join(',')}`)
        .join(';')

      trackDownload({
        barrierType,
        unitType: 'selected area',
        details: `ids: [${formattedIds}], filters: ${
          filters ? Object.keys(filters) : 'none'
        }, scenario: ${scenario}, include unranked: ${
          downloadOptions.includeUnranked
        }`,
      })
    } else {
      trackDownload({ barrierType, unitType: 'national', details: {} })
    }
  }

  const showUserInfoForm = isOpen && !haveUserInfo
  const showDownloadPopup = isOpen && haveUserInfo

  const labelText = label || `Download ${barrierTypeLabel}`

  return (
    <>
      {asButton ? (
        <Button
          onClick={!disabled ? handleShow : null}
          variant={!disabled ? 'primary' : 'disabled'}
          sx={{ fontSize: '1.1em', flex: '1 1 auto' }}
        >
          <Flex sx={{ justifyContent: 'center' }}>
            <Box sx={{ mr: '0.5rem', flex: '0 0 auto' }}>
              <DownloadIcon size="1.2em" />
            </Box>
            <Text sx={{ flex: '0 1 auto' }}>{labelText}</Text>
          </Flex>
        </Button>
      ) : (
        <Text
          as="span"
          onClick={!disabled ? handleShow : null}
          sx={{
            flex: '1 1 auto',
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

      {showDownloadPopup ? (
        <Modal
          title={`Download ${customRank ? 'prioritized' : ''} ${
            barrierTypeLabels[barrierType]
          }`}
          onClose={handleClose}
        >
          <Box sx={{ maxWidth: '600px' }}>
            {barrierType !== 'road_crossings' ? (
              <>
                {showOptions ? (
                  <DownloadOptions
                    barrierType={barrierType}
                    options={downloadOptions}
                    customRank={customRank}
                    onChange={handleDownloadOptionsChange}
                  />
                ) : null}
                {includeUnranked && !showOptions ? (
                  <Box>
                    Note: these data include {barrierTypeLabel} that were
                    located on the aquatic network and have associated network
                    connectivity results as well as {barrierTypeLabel} that were
                    not located on the aquatic network and lack connectivity
                    results.
                    {barrierType === 'small_barriers' &&
                      '  These data only include road-related barriers that have been assessed for impacts to aquatic organisms.'}
                  </Box>
                ) : null}
              </>
            ) : null}

            <Text sx={{ mt: '2rem', fontSize: 1 }}>
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
            </Text>
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
            <Button variant="primary" onClick={handleDownload}>
              <Flex sx={{ alignItems: 'center' }}>
                <DownloadIcon size="1.2em" style={{ marginRight: '0.5rem' }} />
                <Text>Download {barrierTypeLabel}</Text>
              </Flex>
            </Button>
          </Flex>
        </Modal>
      ) : null}
    </>
  )
}

Downloader.propTypes = {
  barrierType: PropTypes.string.isRequired,
  config: PropTypes.shape({
    // <layer>: [ids...]
    summaryUnits: PropTypes.objectOf(PropTypes.array),
    filters: PropTypes.object,
    scenario: PropTypes.string,
  }),
  customRank: PropTypes.bool,
  asButton: PropTypes.bool,
  label: PropTypes.string,
  disabled: PropTypes.bool,
  showOptions: PropTypes.bool,
  includeUnranked: PropTypes.bool,
}

Downloader.defaultProps = {
  config: {}, // empty config means national data
  customRank: false,
  label: null,
  asButton: true,
  disabled: false,
  showOptions: true,
  includeUnranked: false,
}

export default Downloader
