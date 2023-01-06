import React, { memo } from 'react'
import PropTypes from 'prop-types'
import { Box, Flex, Text } from 'theme-ui'

import { formatNumber } from 'util/format'

const HorizontalBar = ({
  value,
  isFiltered,
  isExcluded,
  label,
  quantity,
  max,
  onClick,
}) => {
  const position = quantity / max
  const remainder = 1 - position

  const handleClick = () => {
    onClick(value)
  }

  return (
    <Box
      sx={{
        cursor: 'pointer',
        lineHeight: 1,
        mb: '0.75rem',
        transition: 'opacity 300ms',
        opacity: isExcluded ? 0.25 : 1,
        '&:hover': {
          opacity: isExcluded ? 0.5 : 1,
        },
      }}
      onClick={handleClick}
    >
      <Flex
        sx={{
          justifyContent: 'space-between',
          alignItems: 'flex-end',
          flexWrap: 'nowrap',
          fontSize: 1,
        }}
      >
        <Text
          sx={{
            flex: '0 0 auto',
            fontWeight: isFiltered ? 'bold' : 'normal',
            fontSize: 0,
          }}
        >
          {label}
        </Text>
        <Text sx={{ flex: '0 0 auto', fontSize: 0 }}>
          {formatNumber(quantity)}
        </Text>
      </Flex>

      <Flex
        sx={{
          mt: '0.25rem',
          flexWrap: 'nowrap',
          height: '0.75rem',
          borderRadius: '1rem',
          bg: 'grey.2',
          border: '1px solid',
          borderColor: 'grey.2',
          overflow: 'hidden',
        }}
      >
        <Box
          sx={{
            backgroundColor: isFiltered ? 'accent' : 'primary',
            transition: 'flex-grow 300ms',
          }}
          style={{
            flexGrow: `${position}`,
          }}
        />
        <Box
          style={{ flexGrow: `${remainder}`, transition: 'flex-grow 300ms' }}
        />
      </Flex>
    </Box>
  )
}

HorizontalBar.propTypes = {
  value: PropTypes.oneOfType([PropTypes.string, PropTypes.number]).isRequired,
  isFiltered: PropTypes.bool, // true if filter is set on this bar
  isExcluded: PropTypes.bool, // true if filters are set on others but not this one
  label: PropTypes.oneOfType([PropTypes.string, PropTypes.number]).isRequired,
  quantity: PropTypes.number.isRequired,
  max: PropTypes.number.isRequired,
  onClick: PropTypes.func.isRequired,
}

HorizontalBar.defaultProps = {
  isFiltered: false,
  isExcluded: false,
}

// TODO: optimize for changes to the callback
export default memo(HorizontalBar)
