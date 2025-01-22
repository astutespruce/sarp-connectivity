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

import Error from './Error'
import DownloadOptions from './Options'
import Progress from './Progress'
import Success from './Success'
import Trigger from './Trigger'
import UserInfoForm, { FIELDS } from './UserInfoForm'

const { apiHost } = siteMetadata

const Downloader = ({
  barrierType,
  config,
  customRank,
  label,
  disabled,
  showOptions,
  includeUnranked,
}) => {
  const [
    {
      isOpen,
      haveUserInfo,
      downloadOptions,
      inProgress,
      progress,
      progressMessage,
      error,
      downloadURL,
    },
    setState,
  ] = useState({
    isOpen: false,
    haveUserInfo: false,
    downloadOptions: {
      includeUnranked,
    },
    inProgress: false,
    progress: 0,
    progressMessage: null,
    error: null,
    downloadURL: null,
  })

  const barrierTypeLabel = barrierTypeLabels[barrierType]

  useEffect(() => {
    // If the user previously entered their contact info, don't ask them for it again
    const formData = getFromStorage('downloadForm')
    if (formData && formData[FIELDS.email]) {
      // setHaveUserInfo(true)
      setState((prevState) => ({
        ...prevState,
        haveUserInfo: true,
      }))
    }
  }, [isOpen])

  const handleShow = () => {
    setState((prevState) => ({
      ...prevState,
      isOpen: true,
      inProgress: false,
      progress: 0,
      progressMessage: null,
      error: null,
      downloadURL: null,
    }))
  }

  const handleClose = () => {
    setState((prevState) => ({
      ...prevState,
      isOpen: false,
      inProgress: false,
      progress: 0,
      progressMessage: null,
      error: null,
      downloadURL: null,
    }))
  }

  const handleDownloadOptionsChange = (newOptions) => {
    setState((prevState) => ({
      ...prevState,
      downloadOptions: newOptions,
    }))
  }

  const handleUserInfoContinue = () => {
    // Note: this might be called even if there was an error submitting the user
    // info, and we decided to let them continue anyway
    setState((prevState) => ({
      ...prevState,
      haveUserInfo: true,
    }))
  }

  const handleProgress = ({
    inProgress: nextInProgress = true,
    progress: nextProgress = 0,
    message: nextMessage = null,
  }) => {
    setState((prevState) => ({
      ...prevState,
      inProgress: nextInProgress,
      progress: nextProgress,
      progressMessage: nextMessage,
    }))
  }

  const handleDownload = async () => {
    const { summaryUnits, filters, scenario } = config

    let url = null

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

      // NOTE: this doesn't complete until the background job is completed
      const { url: customDownloadURL, error: requestError } =
        await getDownloadURL(
          {
            barrierType,
            summaryUnits,
            filters,
            includeUnranked:
              barrierType !== 'road_crossings'
                ? downloadOptions.includeUnranked
                : null,
            sort: scenario ? scenario.toUpperCase() : null,
            customRank,
          },
          handleProgress
        )

      if (requestError) {
        setState((prevState) => ({
          ...prevState,
          error: requestError,
          progress: 0,
          progressMessage: null,
          inProgress: false,
        }))
        return
      }

      url = customDownloadURL
    } else {
      trackDownload({ barrierType, unitType: 'national', details: {} })
      url = `${apiHost}/downloads/national/${barrierType}.zip`
    }

    console.log('download url:', url)

    setState((prevState) => ({
      ...prevState,
      downloadURL: url,
      inProgress: false,
      progress: 100,
      progressMessage: 'All done',
      error: null,
    }))

    // update window.location.href to avoid getting blocked by popup blockers
    window.location.href(url)
  }

  const showUserInfoForm = isOpen && !haveUserInfo
  const showDownloadPopup = isOpen && haveUserInfo

  const labelText = label || `Download ${barrierTypeLabel}`

  let content = null

  if (error) {
    content = <Error barrierType={barrierType} onClose={handleClose} />
  } else if (inProgress) {
    content = <Progress progress={progress} message={progressMessage} />
  } else if (downloadURL) {
    content = <Success url={downloadURL} />
  } else {
    content = (
      <>
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
                  Note: these data include {barrierTypeLabel} that were located
                  on the aquatic network and have associated network
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
      </>
    )
  }

  return (
    <>
      <Trigger
        label={labelText}
        disabled={disabled}
        onClick={!disabled ? handleShow : null}
      />

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
          <Box sx={{ minWidth: '400px', maxWidth: '600px' }}>{content}</Box>

          <Flex
            sx={{
              alignItems: 'center',
              justifyContent: downloadURL ? 'flex-end' : 'space-between',
              mt: '1rem',
              pt: '1rem',
              borderTop: '1px solid',
              borderTopColor: 'grey.2',
            }}
          >
            {downloadURL ? (
              <Button variant="primary" onClick={handleClose}>
                Close
              </Button>
            ) : (
              <>
                <Button variant="secondary" onClick={handleClose}>
                  Cancel
                </Button>
                {!(error || inProgress) ? (
                  <Button variant="primary" onClick={handleDownload}>
                    <Flex sx={{ alignItems: 'center' }}>
                      <DownloadIcon
                        size="1.2em"
                        style={{ marginRight: '0.5rem' }}
                      />
                      <Text>Download {barrierTypeLabel}</Text>
                    </Flex>
                  </Button>
                ) : null}
              </>
            )}
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
  label: PropTypes.string,
  disabled: PropTypes.bool,
  showOptions: PropTypes.bool,
  includeUnranked: PropTypes.bool,
}

Downloader.defaultProps = {
  config: {}, // empty config means national data
  customRank: false,
  label: null,
  disabled: false,
  showOptions: true,
  includeUnranked: false,
}

export default Downloader
