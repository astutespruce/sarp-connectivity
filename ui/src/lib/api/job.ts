import { API_HOST } from '$lib/env'
import { captureException } from '$lib/util/log'

const pollInterval = 1000 // milliseconds; 1 second
const jobTimeout = 600000 // milliseconds; 10 minutes
const failedFetchLimit = 5

export type ProgressCallbackParams = {
	status: string
	inProgress: boolean
	progress: number
	queuePosition?: number
	elapsedTime?: number
	message?: string
}

export type ProgressCallback = (params: ProgressCallbackParams) => void

export const pollJob = async (jobId: string, onProgress: ProgressCallback | null = null) => {
	let time = 0
	let failedRequests = 0

	let response = null

	while (time < jobTimeout && failedRequests < failedFetchLimit) {
		try {
			response = await fetch(`${API_HOST}/api/v1/internal/downloads/status/${jobId}`, {
				cache: 'no-cache'
			})
		} catch {
			failedRequests += 1

			// sleep and try again
			await new Promise((r) => {
				setTimeout(r, pollInterval)
			})
			time += pollInterval
			continue
		}

		if (response.status === 500) {
			const error = await response.text()
			captureException(`server error for download job: ${error}`)
			return {
				error: 'server error'
			}
		}

		const json = await response.json()
		const {
			status = null,
			progress = null,
			queue_position: queuePosition = null,
			elapsed_time: elapsedTime = null,
			message = null,
			detail: error = null, // error message
			path = null
		} = json

		if (response.status !== 200 || status === 'failed') {
			captureException(`Download job failed: ${JSON.stringify(json)}`)
			if (error) {
				return { error }
			}

			throw Error(response.statusText)
		}

		if (status === 'success') {
			return { url: `${API_HOST}${path}` }
		}

		if (onProgress && (status === 'queued' || status === 'in_progress' || progress !== null)) {
			onProgress({
				status,
				inProgress: true,
				progress: progress || 0,
				queuePosition: queuePosition || 0,
				elapsedTime: elapsedTime || null,
				message
			})
		}

		// sleep
		await new Promise((r) => {
			setTimeout(r, pollInterval)
		})
		time += pollInterval
	}

	// if we got here, it meant that we hit a timeout error or a fetch error
	if (failedRequests) {
		captureException(`Download job encountered ${failedRequests} fetch errors`)

		return {
			error:
				'network errors were encountered while creating your download.  The server may be too busy or your network connection may be having problems.  Please try again in a few minutes.'
		}
	}

	if (time >= jobTimeout) {
		captureException('Download job timed out')
		return {
			error:
				'timeout while creating your download.  Try selecting a smaller area or number of records to download.'
		}
	}

	captureException('Download job had an unexpected error')
	return {
		error:
			'unexpected errors prevented your download job from completing successfully.  Please try again.'
	}
}
