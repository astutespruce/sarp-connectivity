import React, { useState } from 'react'
import useForm from 'react-hook-form'
import fetchJSONP from 'fetch-jsonp'
import { FaSync, FaExclamationTriangle } from 'react-icons/fa'
import { Image } from 'rebass'

import { Text } from 'components/Text'
import { Box, Flex } from 'components/Grid'
import styled, { themeGet, keyframes } from 'style'
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

const Wrapper = styled(Box)`
  width: 960px;
`

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

const FormContainer = styled(Box).attrs({})`
  width: 66%;
  padding-left: 1rem;
`

const Form = styled.form`
  margin: 0;
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
`

const Buttons = styled(Flex).attrs({
  mt: '1rem',
  pt: '1rem',
  justifyContent: 'space-between',
  alignItems: 'center',
})``

const rotate = keyframes`
  from {
    transform: rotate(0deg);
  }

  to {
    transform: rotate(360deg);
  }
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
  display: inline;
`

const ErrorMessage = styled(Box).attrs({ p: '1rem' })`
  color: ${themeGet('colors.highlight.500')};
  font-size: 2rem;
`

const encode = data => {
  return Object.keys(data)
    .map(key => `${encodeURIComponent(key)}=${encodeURIComponent(data[key])}`)
    .join('&')
}

const DownloadForm = () => {
  const [{ isPending, isError }, setState] = useState({
    isPending: false,
    isError: false,
  })
  const { register, handleSubmit, watch, errors } = useForm()
  const onSubmit = data => {
    console.log('on submit data', data)

    setState({
      isPending: true,
      isError: false,
    })

    // Mailchimp doesn't have CORS support, so we have to use JSONP to submit form data.
    // yuck!
    fetchJSONP(
      `https://astutespruce.us20.list-manage.com/subscribe/post-json?${encode({
        u: userID,
        id: formID,
        ...data,
      })}`,
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
          setState({ isPending: false, isError: true })
          // TODO: report error to sentry
        } else {
          setState({ isPending: false, isError: false })

          // TODO:
        }
      })
      .catch(error => {
        console.error(error)
        setState({ isPending: false, isError: true })

        // TODO: report error to sentry
      })
  }

  let content = null
  if (isError) {
    content = (
      <>
        <ErrorMessage>
          <ErrorIcon />
          Whoops! That didn&apos;t work out quite right.
          <br />
          We are sorry for this problem.
          <br />
        </ErrorMessage>
        TODO: download link
      </>
    )
  } else if (isPending) {
    content = (
      <Flex alignItems="center" justifyContent="center" height="100%">
        <Spinner />
      </Flex>
    )
  } else {
    content = (
      <Form onSubmit={handleSubmit(onSubmit)}>
        <FormColumns>
          <FormColumn>
            <Row>
              <Label htmlFor={FIELDS.email}>Email address:</Label>
              <Input name={FIELDS.email} ref={register} />
            </Row>

            <Row>
              <Label htmlFor={FIELDS.firstName}>First name:</Label>
              <Input name={FIELDS.firstName} ref={register} />
            </Row>

            <Row>
              <Label htmlFor={FIELDS.lastName}>Last name:</Label>
              <Input name={FIELDS.lastName} ref={register} />
            </Row>
          </FormColumn>

          <FormColumn>
            <Row>
              <Label htmlFor={FIELDS.use}>How will you use the data?</Label>
              <TextArea name={FIELDS.use} rows={8} ref={register} />
            </Row>
          </FormColumn>
        </FormColumns>

        <Row>
          <Label htmlFor={FIELDS.organization}>Organization:</Label>
          <Input name={FIELDS.organization} ref={register} />
        </Row>

        <Buttons>
          <button type="button">Cancel</button>
          <button type="submit">Submit</button>
        </Buttons>
      </Form>
    )
  }

  return (
    <Wrapper>
      <Flex>
        <Message>
          <SARPLogo />
          <br />
          We use this information to:
          <List>
            <li>get in touch with you if we discover errors in the data</li>
            <li>
              provide statistics about how this tool is being used to report to
              our funders, who make this tool possible
            </li>
            <li>
              better understand how this tool is being used so that we can
              prioritize improvements
            </li>
          </List>
        </Message>
        <FormContainer>{content}</FormContainer>
      </Flex>
    </Wrapper>
  )
}

export default DownloadForm
