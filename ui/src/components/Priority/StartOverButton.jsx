import React, { useState, memo } from 'react'
import { navigate } from 'gatsby'
import { FaTrash } from 'react-icons/fa'

import { WarningButton } from 'components/Button'
import Confirm from 'components/Confirm'
import styled from 'style'

const TrashIcon = styled(FaTrash)`
  width: 1em;
  height: 1em;
`

const Button = styled(WarningButton)`
  margin-right: 1rem;
  font-size: 1.1em;
`

const StartOverButton = () => {
  const [confirmIsActive, setConfirmIsActive] = useState(false)

  const handleConfirm = () => {
    setConfirmIsActive(false)
    navigate('/priority')
  }

  const handleClick = () => {
    setConfirmIsActive(true)
  }

  return (
    <>
      {confirmIsActive && (
        <Confirm
          title="Start Over?"
          onConfirm={handleConfirm}
          onClose={() => setConfirmIsActive(false)}
        >
          You will lose all your work. Are you sure?
        </Confirm>
      )}

      <Button title="Start Over" onClick={handleClick}>
        <TrashIcon />
      </Button>
    </>
  )
}

export default memo(StartOverButton)
