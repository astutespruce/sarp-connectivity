import React, { useState } from 'react'
import PropTypes from 'prop-types'
import { Box, Flex, Text } from 'theme-ui'
import { CaretDown } from '@emotion-icons/fa-solid'

import Circle from './Circle'

const Legend = ({ title, subtitle, patches, circles, lines, footnote }) => {
  const [isOpen, setIsOpen] = useState(false)

  const hasElements =
    (patches && patches.length > 0) ||
    (circles && circles.length > 0) ||
    (lines && lines.length > 0)

  if (!(hasElements || footnote)) {
    return null
  }

  const toggleOpen = () => {
    setIsOpen((prevIsOpen) => !prevIsOpen)
  }

  return (
    <Box
      title={isOpen ? 'Click to hide legend' : 'Show legend'}
      onClick={toggleOpen}
      sx={{
        position: 'absolute',
        zIndex: 10000,
        right: '10px',
        bottom: '24px',
        maxWidth: '16rem',
        py: '0.5em',
        px: '0.75em',
        bg: '#FFF',
        cursor: 'pointer',
        border: '1px solid #AAA',
        borderRadius: '4px',
        boxShadow: '1px 1px 8px #333',
      }}
    >
      {isOpen ? (
        <>
          <Flex
            sx={{
              alignItems: 'center',
              mb: '0.25em',
              fontSize: 2,
              fontWeight: 'bold',
            }}
          >
            {hasElements ? (
              <Box sx={{ mr: '0.25rem' }}>
                <CaretDown size="1.5em" />
              </Box>
            ) : null}

            <Text>{title}</Text>
          </Flex>

          {subtitle ? (
            <Box
              sx={{
                fontSize: 0,
                color: 'grey.7',
                lineHeight: 1.2,
                mb: '0.5rem',
              }}
            >
              {subtitle}
            </Box>
          ) : null}

          {patches && patches.length > 0 ? (
            <div>
              {patches.map(({ id, label, entries }) => (
                <Box
                  key={id}
                  sx={{
                    '&:not(:first-of-type)': {
                      mt: '0.25rem',
                      pt: '0.25rem',
                      // borderTop: '1px solid',
                      // borderTopColor: 'grey.1',
                    },
                  }}
                >
                  {label ? (
                    <Text
                      sx={{
                        my: '0.5rem',
                        fontWeight: 'bold',
                        fontSize: 'small',
                        lineHeight: 1.2,
                      }}
                    >
                      {label}
                    </Text>
                  ) : null}
                  <div>
                    {entries.map(({ color, label: patchLabel }) => (
                      <Flex
                        key={color}
                        sx={{
                          '&:first-of-type > div': {
                            borderTopLeftRadius: '3px',
                            borderTopRightRadius: '3px',
                            borderTopWidth: '1px',
                          },
                          '&:last-of-type > div': {
                            borderBottomLeftRadius: '3px',
                            borderBottomRightRadius: '3px',
                          },
                        }}
                      >
                        <Box
                          sx={{
                            width: '20px',
                            height: '1em',
                            flex: '0 0 auto',
                            borderWidth: '0 1px 1px 1px',
                            borderStyle: 'solid',
                            borderColor: 'grey.5',
                            bg: color,
                          }}
                        />
                        <Text
                          sx={{
                            fontSize: '0.75rem',
                            ml: '0.5rem',
                            lineHeight: 1,
                            color: 'grey.7',
                          }}
                        >
                          {patchLabel}
                        </Text>
                      </Flex>
                    ))}
                  </div>
                </Box>
              ))}
            </div>
          ) : null}

          {patches && patches.length > 0 && circles && circles.length > 0 ? (
            <Box
              sx={{
                mt: '0.5rem',
                borderTop: '1px solid',
                borderTopColor: 'grey.1',
              }}
            />
          ) : null}

          {circles && circles.length > 0 ? (
            <div>
              {circles.map((point) => (
                <Flex
                  key={point.color}
                  sx={{
                    alignItems: 'flex-start',
                    py: '0.25em',
                    '&:not(:first-of-type)': {
                      borderTop: '1px solid',
                      borderTopColor: 'grey.1',
                    },
                  }}
                >
                  <Circle {...point} />
                  <Text
                    sx={{
                      fontSize: '0.75rem',
                      ml: '0.5rem',
                      lineHeight: 1,
                      color: 'grey.7',
                    }}
                  >
                    {point.label}
                  </Text>
                </Flex>
              ))}
            </div>
          ) : null}

          {((patches && patches.length > 0) ||
            (circles && circles.length > 0)) &&
          lines &&
          lines.length > 0 ? (
            <Box
              sx={{
                mt: '0.5rem',
                borderTop: '1px solid',
                borderTopColor: 'grey.1',
              }}
            />
          ) : null}

          {lines && lines.length > 0 ? (
            <div>
              {lines.map(
                ({
                  id,
                  label: lineLabel,
                  color,
                  lineWidth = '1px',
                  lineStyle = 'solid',
                }) => (
                  <Flex
                    key={id}
                    sx={{
                      alignItems: 'flex-start',
                      py: '0.25em',
                      '&:not(:first-of-type)': {
                        borderTop: '1px solid',
                        borderTopColor: 'grey.1',
                      },
                    }}
                  >
                    <Box
                      sx={{
                        flex: '0 0 auto',
                        width: '1.1rem',
                        height: '0.5rem',
                        borderBottomWidth: lineWidth,
                        borderBottomColor: color,
                        borderBottomStyle: lineStyle,
                      }}
                    />
                    <Text
                      sx={{
                        fontSize: '0.75rem',
                        ml: '0.5rem',
                        lineHeight: 1,
                        color: 'grey.7',
                      }}
                    >
                      {lineLabel}
                    </Text>
                  </Flex>
                )
              )}
            </div>
          ) : null}

          {footnote ? (
            <Text
              variant="help"
              sx={{
                mt: '0.5rem',
                pt: '0.5rem',
                lineHeight: 1.2,
                borderTop: '1px solid',
                borderTopColor: 'grey.1',
                fontSize: 0,
              }}
            >
              {footnote}
            </Text>
          ) : null}
        </>
      ) : (
        <Text
          sx={{ fontSize: 1, fontWeight: 'bold' }}
          title="click to open legend"
        >
          Legend
        </Text>
      )}
    </Box>
  )
}

Legend.propTypes = {
  title: PropTypes.string,
  subtitle: PropTypes.string,
  circles: PropTypes.arrayOf(
    PropTypes.shape({
      color: PropTypes.string.isRequired,
      label: PropTypes.string.isRequired,
      radius: PropTypes.number,
      borderWidth: PropTypes.number,
      borderColor: PropTypes.string,
    })
  ),
  patches: PropTypes.arrayOf(
    PropTypes.shape({
      id: PropTypes.string.isRequired,
      label: PropTypes.string,
      entries: PropTypes.arrayOf(
        PropTypes.shape({
          color: PropTypes.string.isRequired,
          label: PropTypes.string.isRequired,
        }).isRequired
      ),
    })
  ),
  lines: PropTypes.arrayOf(
    PropTypes.shape({
      id: PropTypes.string.isRequired,
      label: PropTypes.string.isRequired,
      color: PropTypes.string.isRequired,
      lineWidth: PropTypes.string,
      lineStyle: PropTypes.string,
    })
  ),
  footnote: PropTypes.string,
}

Legend.defaultProps = {
  title: 'Legend',
  subtitle: null,
  circles: null,
  patches: null,
  lines: null,
  footnote: null,
}

export default Legend
