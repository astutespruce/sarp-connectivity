import React, { useCallback, useEffect, useRef } from 'react'
import PropTypes from 'prop-types'
import { Box, Flex, Text } from 'theme-ui'
import { ExclamationTriangle } from '@emotion-icons/fa-solid'

import { OutboundLink } from 'components/Link'
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

const Results = ({
  results,
  index,
  isLoading,
  error,
  selectedId,
  setSelectedId,
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
      const { id } = results[nextIndex]
      setSelectedId(id)
    },
    [results, setSelectedId]
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
      }}
    >
      {results.map(({ id, name, address }, i) => (
        <Box
          key={id}
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
            ...(id === selectedId ? highlightCSS : {}),
          }}
        >
          <Box sx={{ pointerEvents: 'none' }}>
            <Text>{name}</Text>
            {address ? <Text sx={{ color: 'grey.8' }}>{address}</Text> : null}
          </Box>
        </Box>
      ))}
    </Box>
  )
}

Results.propTypes = {
  results: PropTypes.arrayOf(
    PropTypes.shape({
      id: PropTypes.string.isRequired,
      name: PropTypes.string.isRequired,
      address: PropTypes.string,
    })
  ),
  index: PropTypes.number,
  isLoading: PropTypes.bool,
  error: PropTypes.object,
  selectedId: PropTypes.string,
  setSelectedId: PropTypes.func.isRequired,
}

Results.defaultProps = {
  index: null,
  isLoading: false,
  error: null,
  results: [],
  selectedId: null,
}

export default Results
