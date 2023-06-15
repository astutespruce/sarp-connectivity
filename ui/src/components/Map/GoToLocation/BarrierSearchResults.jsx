import React, { useCallback, useEffect, useRef } from 'react'
import PropTypes from 'prop-types'
import { Box, Flex, Text } from 'theme-ui'
import { ExclamationTriangle } from '@emotion-icons/fa-solid'

import {
  STATES,
  barrierNameWhenUnknown,
  barrierTypeLabelSingular,
} from 'config'
import { OutboundLink } from 'components/Link'
import { formatNumber } from 'util/format'
import LoadingIcon from './LoadingIcon'
import { siteMetadata } from '../../../../gatsby-config'

const { contactEmail } = siteMetadata

const highlightCSS = {
  fontWeight: 'bold',
  bg: 'grey.0',
  '&:hover': {
    bg: 'grey.0',
  },
}

const BarrierSearchResults = ({
  results,
  remaining,
  index,
  isLoading,
  error,
  selectedId,
  setLocation,
}) => {
  const listNode = useRef(null)

  useEffect(() => {
    // make sure that all nodes are created first
    if (
      listNode.current &&
      listNode.current.children &&
      listNode.current.children.length > index &&
      listNode.current.children[index]
    ) {
      listNode.current.children[index].focus()
    }
  }, [index])

  const handleSelectId = useCallback(
    (nextIndex) => {
      setLocation(results[nextIndex])
    },
    [results, setLocation]
  )

  const handleClick = useCallback(
    ({
      target: {
        dataset: { index: nextIndex },
      },
    }) => {
      if (nextIndex !== undefined) {
        handleSelectId(nextIndex)
      }
    },
    [handleSelectId]
  )

  const handleKeyDown = useCallback(
    ({
      key,
      target: {
        dataset: { index: nextIndex },
      },
    }) => {
      if (key === 'Enter' && nextIndex !== undefined) {
        handleSelectId(nextIndex)
      }
    },
    [handleSelectId]
  )

  if (error) {
    return (
      <Box
        sx={{
          color: 'grey.8',
          px: '1rem',
          py: '2rem',
          ml: '-1.5rem',
        }}
      >
        <Text>
          <Flex sx={{ alignItems: 'center' }}>
            <ExclamationTriangle
              size="1.5rem"
              style={{ margin: '0 0.5rem 0 0' }}
            />
            <Text>Error loading search results.</Text>
          </Flex>

          <Text sx={{ mt: '1rem' }}>
            Please try a different search term. If the error continues, please{' '}
            <OutboundLink to={`mailto:${contactEmail}`}>
              let us know
            </OutboundLink>
            .
          </Text>
        </Text>
      </Box>
    )
  }

  if (isLoading) {
    return (
      <Flex
        sx={{
          alignItems: 'center',
          justifyContent: 'center',
          color: 'grey.8',
          px: '1rem',
          py: '2rem',
          ml: '-1.5rem',
        }}
      >
        <LoadingIcon
          sx={{
            width: '2rem',
            height: '2rem',
            margin: '0 0.5rem 0 0',
            color: 'grey.5',
          }}
        />
        <Text>Loading...</Text>
      </Flex>
    )
  }

  if (!(results && results.length > 0)) {
    return (
      <Flex
        sx={{
          alignItems: 'center',
          justifyContent: 'center',
          color: 'grey.8',
          px: '1rem',
          py: '2rem',
          ml: '-1.5rem',
        }}
      >
        No results found
      </Flex>
    )
  }

  return (
    <Box
      ref={listNode}
      className="search-results"
      sx={{
        mt: '0.5rem',
        ml: '-1.5rem',
        maxHeight: 'calc(80vh - 6rem)',
        overflowY: 'auto',
      }}
    >
      {results.map(({ sarpid, name, state, river, stream, barriertype }, i) => (
        <Box
          key={sarpid}
          data-index={i}
          tabIndex={0}
          onKeyDown={handleKeyDown}
          onClick={handleClick}
          sx={{
            cursor: 'pointer',
            '&:not(:first-of-type)': {
              borderTop: '1px solid',
              borderTopColor: 'grey.1',
            },

            py: '0.25rem',
            px: '0.5rem',
            '&:hover': {
              bg: 'grey.0',
            },
            ...(sarpid === selectedId ? highlightCSS : {}),
          }}
        >
          <Box sx={{ pointerEvents: 'none' }}>
            <Text>
              {name || barrierNameWhenUnknown[barriertype] || 'Unknown name'} (
              {sarpid})
            </Text>
            <Text sx={{ color: 'grey.8' }}>
              barrier type: {barrierTypeLabelSingular[barriertype]}
              <br />
              {river ? `located on ${river}, ` : null}
              {stream && !river ? `located on ${stream}, ` : null}
              {STATES[state]}
            </Text>
          </Box>
        </Box>
      ))}
      {remaining && remaining > 0 ? (
        <Flex
          sx={{
            justifyContent: 'center',
            fontSize: 0,
            color: 'grey.8',
            pt: '0.5rem',
            borderTop: '1px solid',
            borderTopColor: 'grey.1',
          }}
        >
          ... and {remaining >= 1000 ? 'at least ' : null}
          {formatNumber(remaining)} more ...
        </Flex>
      ) : null}
    </Box>
  )
}

BarrierSearchResults.propTypes = {
  results: PropTypes.arrayOf(
    PropTypes.shape({
      sarpid: PropTypes.string.isRequired,
      name: PropTypes.string.isRequired,
      state: PropTypes.string.isRequired,
      river: PropTypes.string,
      Stream: PropTypes.string,
    })
  ),
  remaining: PropTypes.number,
  index: PropTypes.number,
  isLoading: PropTypes.bool,
  error: PropTypes.object,
  selectedId: PropTypes.string,
  setLocation: PropTypes.func.isRequired,
}

BarrierSearchResults.defaultProps = {
  results: [],
  remaining: 0,
  index: null,
  isLoading: false,
  error: null,
  selectedId: null,
}

export default BarrierSearchResults
