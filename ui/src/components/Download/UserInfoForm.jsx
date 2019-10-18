import React, { useState, useRef } from 'react'
import PropTypes from 'prop-types'
import useForm from 'react-hook-form'
import fetchJSONP from 'fetch-jsonp'
import { FaSync, FaExclamationTriangle, FaCheckCircle } from 'react-icons/fa'
import { Image } from 'rebass'

import { Button } from 'components/Button'
import { Text } from 'components/Text'
import { Box, Flex } from 'components/Grid'
import styled, { themeGet, keyframes, css } from 'style'
import { saveToStorage, encodeParams } from 'util/dom'
import SARPLogoImage from 'images/sarp_logo.png'
import { siteMetadata } from '../../../gatsby-config'

const {
  mailchimpConfig: { userID, formID, formURL },
} = siteMetadata

if (!(formURL && userID && formID)) {
  console.error('Mail chimp form env vars need to be provided in .env file')
}

// Since Mailchimp uses custom field names that vary between forms, use the following
// to map those to logical entities
const FIELDS = {
  email: 'MERGE0',
  firstName: 'MERGE1',
  lastName: 'MERGE2',
  organization: 'MERGE3',
  use: 'MERGE4',
}

const Wrapper = styled(Box).attrs({ pt: '1rem' })``

const SARPLogo = styled(Image).attrs({ src: SARPLogoImage })`
  height: 4rem;
  display: block;
`

const Message = styled(Text)`
  width: 33%;
  padding-right: 1rem;
`

const List = styled.ul`
  margin-top: 0.5rem;
`

const Form = styled.form`
  width: 960px;
  margin: 0;
`

const FormContainer = styled(Box).attrs({})`
  width: 66%;
  padding-left: 1rem;
`

const FormColumns = styled(Flex)``

const FormColumn = styled(Box).attrs({})`
  width: 50%;

  &:not(:first-child) {
    margin-left: 2rem;
  }
`

const Row = styled(Box)`
  &:not(:first-child) {
    margin-top: 1rem;
  }
`

const Label = styled(Text).attrs({ fontSize: '1.25rem' })``

const Input = styled.input`
  width: 100%;
  border: 1px solid ${themeGet('colors.grey.500')};
  border-radius: 0.25rem;
  outline: none;
  padding: 0.25rem 0.5rem;

  &:focus {
    border-color: ${themeGet('colors.primary.500')};
  }

  ${({ invalid }) =>
    invalid &&
    css`
      border-left-width: 0.5rem !important;
      border-color: ${themeGet('colors.highlight.500')} !important;
    `}
`

const TextArea = styled.textarea`
  width: 100%;
  border: 1px solid ${themeGet('colors.grey.500')};
  border-radius: 0.25rem;
  outline: none;
  padding: 0.25rem 0.5rem;

  &:focus {
    border-color: ${themeGet('colors.primary.500')};
  }

  ${({ invalid }) =>
    invalid &&
    css`
      border-left-width: 0.5rem !important;
      border-color: ${themeGet('colors.highlight.500')} !important;
    `}
`

const RowLabel = styled(Flex).attrs({
  justifyContent: 'space-between',
  alignItems: 'flex-end',
})``

const Error = styled(Text).attrs({ fontSize: '0.8rem' })`
  color: ${themeGet('colors.highlight.500')};
`

const Buttons = styled(Flex).attrs({
  justifyContent: 'space-between',
  alignItems: 'center',
  mt: '1rem',
  pt: '1rem',
})`
  border-top: 1px solid ${themeGet('colors.grey.200')};
`

const rotate = keyframes`
  from {
    transform: rotate(0deg);
  }

  to {
    transform: rotate(360deg);
  }
`

const MessageBox = styled(Flex).attrs({
  p: '1rem',
  alignItems: 'center',
  justifyContent: 'center',
  height: '100%',
})`
  font-size: 1.5rem;
  width: 600px;
`

const Spinner = styled(FaSync)`
  height: 5rem;
  width: 5rem;
  animation: ${rotate} 2s linear infinite;
  color: ${themeGet('colors.primary.500')};
  margin-right: 1em;
`

const ErrorIcon = styled(FaExclamationTriangle)`
  height: 2em;
  width: 2em;
  margin-right: 0.5em;
  color: ${themeGet('colors.highlight.500')};
  display: inline-block;
`

const ErrorMessage = styled(MessageBox)`
  color: ${themeGet('colors.highlight.500')};
`

const SuccessIcon = styled(FaCheckCircle)`
  height: 2em;
  width: 2em;
  margin-right: 0.5em;
  color: ${themeGet('colors.primary.500')};
`

const DownloadForm = ({ onCancel, onContinue }) => {
  const [{ isPending, isError, isSuccess }, setState] = useState({
    isPending: false,
    isError: false,
    isSuccess: false,
  })

  const { register, handleSubmit, errors } = useForm({
    mode: 'onBlur',
  })

  const formRef = useRef()

  const onSubmit = data => {
    console.log('on submit data', data)

    setState({
      isPending: true,
      isError: false,
      isSuccess: false,
    })

    // Mailchimp doesn't have CORS support, so we have to use JSONP to submit form data.
    // yuck!
    fetchJSONP(
      `https://astutespruce.us20.list-manage.com/subscribe/post-json?${encodeParams(
        {
          u: userID,
          id: formID,
          ...data,
        }
      )}`,
      {
        jsonpCallback: 'c',
      }
    )
      .then(response => {
        return response.json()
      })
      .then(({ result, msg }) => {
        console.log('json', result, msg)
        if (result === 'error') {
          if (msg.search('already subscribed') !== -1) {
            // this is an error ot Mailchimp, but not a problem for us
            saveToStorage('downloadForm', data)
            setState({ isPending: false, isError: false, isSuccess: true })

            onContinue()
          } else {
            setState({ isPending: false, isError: true })
            // TODO: report error to sentry
          }
        } else {
          // assume it was successful
          saveToStorage('downloadForm', data)
          setState({ isPending: false, isError: false, isSuccess: true })
          // TODO:

          onContinue()
        }
      })
      .catch(error => {
        console.error(error)
        setState({ isPending: false, isError: true })

        // TODO: report error to sentry
      })
  }

  const handleCancel = () => {
    onCancel()
  }

  const handleContinue = () => {
    onContinue()
  }

  if (isError) {
    return (
      <Wrapper>
        <ErrorMessage>
          <ErrorIcon />
          <Box>Whoops! Something went wrong saving your information.</Box>
        </ErrorMessage>

        <Buttons>
          <Button onClick={handleCancel}>Cancel</Button>

          <Button primary onClick={handleContinue}>
            Continue to download anyway
          </Button>
        </Buttons>
      </Wrapper>
    )
  }
  if (isPending) {
    return (
      <Wrapper>
        <MessageBox>
          <Spinner />
        </MessageBox>
      </Wrapper>
    )
  }

  if (isSuccess) {
    return (
      <MessageBox>
        <SuccessIcon />
        <Text>Thank you!</Text>
      </MessageBox>
    )
  }

  return (
    <Wrapper>
      <Form ref={formRef} onSubmit={handleSubmit(onSubmit)}>
        <Flex>
          <Message>
            We use this information to:
            <List>
              <li>get in touch with you if we discover errors in the data</li>
              <li>
                provide statistics about how this tool is being used to our
                funders
              </li>
              <li>
                better understand how this tool is being used so that we can
                prioritize improvements
              </li>
            </List>
            <Flex justifyContent="center">
              <SARPLogo />
            </Flex>
          </Message>

          <FormContainer>
            <FormColumns>
              <FormColumn>
                <Row>
                  <RowLabel>
                    <Label htmlFor={FIELDS.email}>Email address:</Label>
                    {errors[FIELDS.email] && <Error>required</Error>}
                  </RowLabel>
                  <Input
                    name={FIELDS.email}
                    ref={register({
                      required: true,
                      pattern: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
                    })}
                    invalid={!!errors[FIELDS.email]}
                  />
                </Row>

                <Row>
                  <RowLabel>
                    <Label htmlFor={FIELDS.firstName}>First name:</Label>
                    {errors[FIELDS.firstName] && <Error>required</Error>}
                  </RowLabel>

                  <Input
                    name={FIELDS.firstName}
                    ref={register({ required: true })}
                    invalid={!!errors[FIELDS.firstName]}
                  />
                </Row>

                <Row>
                  <RowLabel>
                    <Label htmlFor={FIELDS.lastName}>Last name:</Label>
                    {errors[FIELDS.lastName] && <Error>required</Error>}
                  </RowLabel>

                  <Input
                    name={FIELDS.lastName}
                    ref={register({ required: true })}
                    invalid={!!errors[FIELDS.lastName]}
                  />
                </Row>
              </FormColumn>

              <FormColumn>
                <Row>
                  <RowLabel>
                    <Label htmlFor={FIELDS.use}>
                      How will you use the data?
                    </Label>
                    {errors[FIELDS.use] && <Error>required</Error>}
                  </RowLabel>
                  <TextArea
                    name={FIELDS.use}
                    rows={8}
                    ref={register({ required: true })}
                    invalid={!!errors[FIELDS.use]}
                  />
                </Row>
              </FormColumn>
            </FormColumns>

            <Row>
              <RowLabel>
                <Label htmlFor={FIELDS.organization}>Organization:</Label>
                {errors[FIELDS.organization] && <Error>required</Error>}
              </RowLabel>
              <Input
                name={FIELDS.organization}
                ref={register({ required: true })}
                invalid={!!errors[FIELDS.organization]}
              />
            </Row>
          </FormContainer>
        </Flex>

        <Buttons>
          <Button type="button" onClick={handleCancel}>
            Cancel
          </Button>

          <Button type="submit" primary>
            Continue to download
          </Button>
        </Buttons>
      </Form>
    </Wrapper>
  )
}

DownloadForm.propTypes = {
  onCancel: PropTypes.func.isRequired,
  onContinue: PropTypes.func.isRequired,
}

export default DownloadForm
