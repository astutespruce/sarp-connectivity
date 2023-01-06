import React, { useState, useRef } from 'react'
import PropTypes from 'prop-types'
import { useForm } from 'react-hook-form'
import fetchJSONP from 'fetch-jsonp'
import { ExclamationTriangle, CheckCircle } from '@emotion-icons/fa-solid'
import {
  Box,
  Flex,
  Grid,
  Container,
  Button,
  Image,
  Text,
  Paragraph,
  Spinner,
  Label,
  Input,
  Textarea,
} from 'theme-ui'

import { siteMetadata } from 'config'
import { saveToStorage, encodeParams } from 'util/dom'
import SARPLogoImage from 'images/sarp_logo.png'

const {
  mailchimpConfig: { userID, formID, formURL },
} = siteMetadata

if (!(formURL && userID && formID)) {
  console.error('Mail chimp form env vars need to be provided in .env file')
}

// Since Mailchimp uses custom field names that vary between forms, use the following
// to map those to logical entities

// for test form:
// export const FIELDS = {
//   email: 'MERGE0',
//   firstName: 'MERGE1',
//   lastName: 'MERGE2',
//   organization: 'MERGE3',
//   use: 'MERGE4',
// }

// for SARP form
export const FIELDS = {
  email: 'EMAIL',
  firstName: 'FNAME',
  lastName: 'LNAME',
  organization: 'MMERGE5',
  use: 'MMERGE6',
}

const DownloadForm = ({ onCancel, onContinue }) => {
  const [{ isPending, isError, isSuccess }, setState] = useState({
    isPending: false,
    isError: false,
    isSuccess: false,
  })

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm({
    mode: 'onBlur',
  })

  const formRef = useRef()

  const onSubmit = (data) => {
    console.log('on submit data', data)

    setState({
      isPending: true,
      isError: false,
      isSuccess: false,
    })

    // Mailchimp doesn't have CORS support, so we have to use JSONP to submit form data.
    // yuck!

    // Note: we have to add -json to the end of the regular form URL, make sure it is formatted correctly in .env.*
    fetchJSONP(
      `${formURL}-json?${encodeParams({
        u: userID,
        id: formID,
        ...data,
      })}`,
      {
        jsonpCallback: 'c',
      }
    )
      .then((response) => response.json())
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
      .catch((error) => {
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
      <Box sx={{ pt: '1rem' }}>
        <Flex sx={{ color: 'highlight', alignItems: 'center' }}>
          <Box sx={{ mr: '0.5rem', flex: '0 0 auto' }}>
            <ExclamationTriangle size="2em" />
          </Box>
          <Box sx={{ flex: '1 1 auto' }}>
            Whoops! Something went wrong saving your information.
          </Box>
        </Flex>

        <Flex
          sx={{
            justifyContent: 'space-between',
            alignItems: 'center',
            mt: '1rem',
            pt: '1rem',
            borderTop: '1px solid',
            borderTopColor: 'grey.2',
          }}
        >
          <Button variant="secondary" onClick={handleCancel}>
            Cancel
          </Button>

          <Button onClick={handleContinue}>Continue to download anyway</Button>
        </Flex>
      </Box>
    )
  }
  if (isPending || isSuccess) {
    return (
      <Flex
        sx={{
          p: '1rem',
          alignItems: 'center',
          justifyContent: 'center',
          height: '100%',
          fontSize: '1.5rem',
          width: '600px',
        }}
      >
        {isPending ? (
          <Spinner size="5rem" sx={{ color: 'primary', mr: '1em' }} />
        ) : (
          <>
            <Box sx={{ color: 'primary', mr: '0.5em' }}>
              <CheckCircle size="2em" />
            </Box>
            <Text>Thank you!</Text>
          </>
        )}
      </Flex>
    )
  }

  return (
    <Box sx={{ pt: '1rem' }}>
      <Container
        as="form"
        ref={formRef}
        onSubmit={handleSubmit(onSubmit)}
        sx={{
          m: 0,
          label: {
            flex: '1 1 auto',
          },
          'label + span': {
            flex: '0 0 auto',
          },
        }}
      >
        <Grid columns="1fr 2fr" gap={4}>
          <Box>
            <Paragraph>We use this information to:</Paragraph>
            <Box as="ul" sx={{ mt: '0.5rem' }}>
              <li>get in touch with you if we discover errors in the data</li>
              <li>
                provide statistics about how this tool is being used to our
                funders
              </li>
              <li>
                better understand how this tool is being used so that we can
                prioritize improvements
              </li>
            </Box>
            <Flex sx={{ justifyContent: 'center', mt: '1rem' }}>
              <Image
                src={SARPLogoImage}
                sx={{ height: '4rem', display: 'block' }}
              />
            </Flex>
          </Box>

          <Box>
            <Grid columns={2} gap={5}>
              <Box
                sx={{
                  '&>div + div': {
                    mt: '1rem',
                  },
                }}
              >
                <Box>
                  <Flex
                    sx={{
                      justifyContent: 'space-between',
                      alignItems: 'flex-end',
                    }}
                  >
                    <Label htmlFor={FIELDS.email}>Email address:</Label>
                    {errors[FIELDS.email] && (
                      <Text variant="error">required</Text>
                    )}
                  </Flex>
                  <Input
                    name={FIELDS.email}
                    {...register(FIELDS.email, {
                      required: true,
                      pattern: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
                    })}
                    variant={
                      errors[FIELDS.email] ? 'input-invalid' : 'input-default'
                    }
                  />
                </Box>

                <Box>
                  <Flex
                    sx={{
                      justifyContent: 'space-between',
                      alignItems: 'flex-end',
                    }}
                  >
                    <Label htmlFor={FIELDS.firstName}>First name:</Label>
                    {errors[FIELDS.firstName] && (
                      <Text variant="error">required</Text>
                    )}
                  </Flex>

                  <Input
                    name={FIELDS.firstName}
                    {...register(FIELDS.firstName, { required: true })}
                    variant={
                      errors[FIELDS.firstName]
                        ? 'input-invalid'
                        : 'input-default'
                    }
                  />
                </Box>

                <Box>
                  <Flex
                    sx={{
                      justifyContent: 'space-between',
                      alignItems: 'flex-end',
                    }}
                  >
                    <Label htmlFor={FIELDS.lastName}>Last name:</Label>
                    {errors[FIELDS.lastName] && (
                      <Text variant="error">required</Text>
                    )}
                  </Flex>

                  <Input
                    name={FIELDS.lastName}
                    {...register(FIELDS.lastName, { required: true })}
                    variant={
                      errors[FIELDS.lastName]
                        ? 'input-invalid'
                        : 'input-default'
                    }
                  />
                </Box>
              </Box>

              <Box>
                <Box>
                  <Flex
                    sx={{
                      justifyContent: 'space-between',
                      alignItems: 'flex-end',
                    }}
                  >
                    <Label htmlFor={FIELDS.use}>
                      How will you use the data?
                    </Label>
                    {errors[FIELDS.use] && (
                      <Text variant="error">required</Text>
                    )}
                  </Flex>
                  <Textarea
                    name={FIELDS.use}
                    rows={8}
                    {...register(FIELDS.use, { required: true })}
                    variant={
                      errors[FIELDS.use] ? 'input-invalid' : 'input-default'
                    }
                  />
                </Box>
              </Box>
            </Grid>

            <Box sx={{ mt: '2rem' }}>
              <Flex
                sx={{ justifyContent: 'space-between', alignItems: 'flex-end' }}
              >
                <Label htmlFor={FIELDS.organization}>Organization:</Label>
                {errors[FIELDS.organization] && (
                  <Text variant="error">required</Text>
                )}
              </Flex>
              <Input
                name={FIELDS.organization}
                {...register(FIELDS.organization, { required: true })}
                variant={
                  errors[FIELDS.organization]
                    ? 'input-invalid'
                    : 'input-default'
                }
              />
            </Box>
          </Box>
        </Grid>

        <Flex
          sx={{
            justifyContent: 'space-between',
            alignItems: 'center',
            mt: '1rem',
            pt: '1rem',
            borderTop: '1px solid',
            borderTopColor: 'grey.2',
          }}
        >
          <Button type="button" variant="secondary" onClick={handleCancel}>
            Cancel
          </Button>

          <Button type="submit">Continue to download</Button>
        </Flex>
      </Container>
    </Box>
  )
}

DownloadForm.propTypes = {
  onCancel: PropTypes.func.isRequired,
  onContinue: PropTypes.func.isRequired,
}

export default DownloadForm
