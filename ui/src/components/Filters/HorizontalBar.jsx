import React, { memo } from 'react'
import PropTypes from 'prop-types'
import { Box, Flex, Text } from 'theme-ui'

import { formatNumber } from 'util/format'

// const Wrapper = styled.div`
//   cursor: pointer;
//   line-height: 1;
//   margin-bottom: 1rem;

//   transition: opacity 300ms;
//   opacity: ${({ isExcluded }) => (isExcluded ? 0.25 : 1)};

//   &:hover {
//     opacity: ${({ isExcluded }) => (isExcluded ? 0.5 : 1)};
//   }
// `

// const Labels = styled(Columns).attrs({
//   justifyContent: 'space-between',
//   alignItems: 'flex-end',
// })`
//   color: ${({ active }) =>
//     active ? themeGet('colors.accent.500') : themeGet('colors.grey.700')};

//   margin-bottom: 0.25em;
// `

// const Label = styled(Column)`
//   font-size: 0.9rem;
// `

// const Count = styled(Column)`
//   font-size: 0.8rem;
//   flex: 0 0 auto;
// `

// const IndicatorWrapper = styled(Flex).attrs({
//   flexWrap: 'nowrap',
// })`
//   height: 0.5rem;
//   border-radius: 0.25rem;
//   background-color: ${themeGet('colors.grey.200')};
//   overflow: hidden;
// `

// const Indicator = styled.div`
//   background-color: ${themeGet('colors.primary.500')};
//   flex-grow: ${({ width }) => width};
//   transition: flex-grow 300ms;
// `

// const FilteredIndicator = styled(Indicator)`
//   background-color: ${themeGet('colors.accent.500')};
// `

// const Filler = styled.div`
//   transition: flex-grow 300ms;
// `

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

  // return (
  //   <Wrapper onClick={handleClick} isExcluded={isExcluded}>
  //     <Labels active={isFiltered}>
  //       <Label>{label}</Label>
  //       <Count>{formatNumber(quantity)}</Count>
  //     </Labels>
  //     <IndicatorWrapper>
  //       {position > 0 && (
  //         <>
  //           {isFiltered ? (
  //             <FilteredIndicator style={{ flexGrow: position }} />
  //           ) : (
  //             <Indicator style={{ flexGrow: position }} />
  //           )}
  //         </>
  //       )}

  //       {remainder > 0 && <Filler style={{ flexGrow: remainder }} />}
  //     </IndicatorWrapper>
  //   </Wrapper>
  // )

  return (
    <Box
      sx={{
        cursor: 'pointer',
        lineHeight: 1,
        mb: '1rem',
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
          sx={{ flex: '0 0 auto', fontWeight: isFiltered ? 'bold' : 'normal' }}
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
