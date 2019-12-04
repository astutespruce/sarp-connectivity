import React, { memo, useState, useEffect, useRef } from 'react'
import PropTypes from 'prop-types'
import {
  FaCaretRight,
  FaCaretDown,
  FaLayerGroup,
  FaTimesCircle,
} from 'react-icons/fa'

import { Flex, Box } from 'components/Grid'
import { Checkbox } from 'components/Button'
import { useEffectSkipFirst } from 'util/hooks'
import styled, { themeGet } from 'style'
import { MapControlWrapper } from './styles'

const Wrapper = styled(MapControlWrapper)`
  top: 150px;
  right: 10px;
  line-height: 1;
  background-color: ${({ isOpen }) => (isOpen ? '#eee' : '#fff')};
  border: none;
  padding: 7px;
  z-index: 10000;
`

const Icon = styled(FaLayerGroup)`
  width: 1em;
  height: 1em;
  margin-top: 1px;
  cursor: pointer;
`

const Header = styled.span`
  margin: 0 0.5em;
  font-weight: bold;
  font-size: 0.9em;
  display: inline-block;
  vertical-align: top;
  margin-top: 4px;
  cursor: pointer;
`

const CloseIcon = styled(FaTimesCircle)`
  width: 1em;
  height: 1em;
  color: ${themeGet('colors.grey.500')};
  cursor: pointer;

  &:hover {
    color: ${themeGet('colors.grey.900')};
  }
`

const Content = styled(Box).attrs({ py: '1rem', px: '0.5rem' })`
  width: 16rem;
`

const Row = styled(Flex).attrs({ alignItems: 'flex-start' })`
  &:not(:first-child) {
    margin-top: 1rem;
  }

  & label {
    font-size: small !important;
    font-weight: normal !important;
  }
`

const DropDownLayerChooser = ({ label, options, onChange }) => {
  const [isOpen, setIsOpen] = useState(false)
  const [checkboxState, setCheckboxState] = useState(() => {
    return options.reduce(
      (prev, { id }) => Object.assign(prev, { [id]: false }),
      {}
    )
  })

  const toggle = () => {
    setIsOpen(prevIsOpen => !prevIsOpen)
  }

  const toggleCheckbox = id => checked => {
    setCheckboxState(prevState => ({
      ...prevState,
      [id]: !prevState[id],
    }))
  }

  useEffectSkipFirst(() => {
    onChange(checkboxState)
  }, [checkboxState])

  return (
    <Wrapper isOpen={isOpen}>
      {isOpen ? (
        <>
          <Flex justifyContent="space-between" alignItems="center">
            <div>
              <Icon onClick={toggle} />
              <Header onClick={toggle}>Show / hide map layers</Header>
            </div>
            <CloseIcon onClick={toggle} />
          </Flex>
          <Content>
            {options.map(({ id, label: checkboxLabel }) => (
              <Row key={id}>
                <Checkbox
                  id={id}
                  checked={checkboxState[id]}
                  label={checkboxLabel}
                  onChange={toggleCheckbox(id)}
                />
              </Row>
            ))}
          </Content>
        </>
      ) : (
        <Icon onClick={toggle} title="Show / hide map layers" />
      )}
    </Wrapper>
  )
}

DropDownLayerChooser.propTypes = {
  label: PropTypes.string.isRequired,
  options: PropTypes.arrayOf(
    PropTypes.shape({
      id: PropTypes.string.isRequired,
      label: PropTypes.string.isRequired,
    })
  ).isRequired,
  onChange: PropTypes.func.isRequired,
}

export default memo(DropDownLayerChooser, () => true)

// const Wrapper = styled(Box)`
//   position: absolute;
//   z-index: 1000;
//   top: 0;
//   left: 10px;
// `

// const Toggle = styled(Flex).attrs({ px: '1rem', py: '0.75rem' })`
//   position: relative;
//   z-index: 2;
//   cursor: pointer;
//   background: #fff;
//   border-radius: 0 0 0.25rem 0.25rem;
//   box-shadow: 1px 1px 8px #333;
// `

// const Icon = styled(FaLayerGroup)`
//   height: 2em;
//   width: 2em;
// `

// const ExpandoOpen = styled(FaCaretDown)`
//   width: 1rem;
//   height: 1rem;
//   flex: 0 0 auto;
// `

// const ExpandoClosed = styled(FaCaretRight)`
//   width: 1rem;
//   height: 1rem;
//   flex: 0 0 auto;
// `

// const Label = styled.div`
//   font-size: smaller;
// `

// const Panel = styled(Box).attrs({
//   px: '1rem',
//   py: '1rem',
//   mx: '0.5rem',
// })`
//   position: absolute;
//   left: 0;
//   z-index: 1;
//   background: #fff;
//   border-radius: 0 0 0.25rem 0.25rem;
//   box-shadow: 1px 1px 8px #333;
//   width: 18rem;
// `

// const Row = styled(Flex).attrs({ alignItems: 'flex-start' })`
//   &:not(:first-child) {
//     margin-top: 1rem;
//   }

//   & label {
//     font-size: small !important;
//     font-weight: normal !important;
//   }
// `

// /**
//  * useEffect hook that skips first call during initial rendering of component.
//  * Adapted from: https://stackoverflow.com/a/54895884
//  * @param {function} fn
//  * @param {Array} deps - dependencies for useEffect
//  */
// const useEffectSkipFirst = (f, deps) => {
//   const isFirst = useRef(true)

//   useEffect(() => {
//     if (isFirst.current) {
//       isFirst.current = false
//       return
//     }

//     f()
//   }, deps)
// }

// const DropDownLayerChooser = ({ label, options, onChange }) => {
//   const [isOpen, setIsOpen] = useState(false)
//   const [checkboxState, setCheckboxState] = useState(() => {
//     return options.reduce(
//       (prev, { id }) => Object.assign(prev, { [id]: false }),
//       {}
//     )
//   })

//   console.log('render dropdown layer chooser')

//   const toggle = () => {
//     setIsOpen(prevIsOpen => !prevIsOpen)
//   }

//   const toggleCheckbox = id => checked => {
//     setCheckboxState(prevState => ({
//       ...prevState,
//       [id]: !prevState[id],
//     }))
//   }

//   useEffectSkipFirst(() => {
//     onChange(checkboxState)
//   }, [checkboxState])

//   return (
//     <Wrapper>
//       <Toggle onClick={toggle}>
//         <Icon />
//         {/* {isOpen ? <ExpandoOpen /> : <ExpandoClosed />}
//         <Label>{label}</Label> */}
//       </Toggle>

//       {isOpen && (
//         <Panel>
//           <Label>{label}</Label>
//           <div>
//             {options.map(({ id, label: checkboxLabel }) => (
//               <Row key={id}>
//                 <Checkbox
//                   id={id}
//                   checked={checkboxState[id]}
//                   label={checkboxLabel}
//                   onChange={toggleCheckbox(id)}
//                 />
//               </Row>
//             ))}
//           </div>
//         </Panel>
//       )}
//     </Wrapper>
//   )
// }

// DropDownLayerChooser.propTypes = {
//   label: PropTypes.string.isRequired,
//   options: PropTypes.arrayOf(
//     PropTypes.shape({
//       id: PropTypes.string.isRequired,
//       label: PropTypes.string.isRequired,
//     })
//   ).isRequired,
//   onChange: PropTypes.func.isRequired,
// }

// export default memo(DropDownLayerChooser, () => true)
