import path from 'path'
import send from 'send'

/** This plugin serves PMTiles from VITE_TILE_DIR in development; they are served
 * by Caddy in production
 */
const servePMTilesMiddleware = (server) => {
	server.middlewares.use(`/tiles`, (req, res, next) => {
		// hardcode root to prevent traversal
		const fileStream = send(req, req.url, {
			root: path.resolve(process.env.VITE_TILE_DIR as string)
		})

		// CORS must be set
		fileStream.on('headers', (res) => {
			res.setHeader('Access-Control-Allow-Origin', '*')
			res.setHeader('Access-Control-Allow-Headers', '*')
			res.setHeader('Access-Control-Allow-Method', '*')
			res.setHeader('Vary', 'Accept-Encoding')
		})

		fileStream.on('error', (err) => {
			if (err.status === 404) {
				// allow vite to handle 404s
				next()
			} else {
				res.statusCode = err.status || 500
				res.end(err.message)
			}
		})
		fileStream.pipe(res)
	})
}

const pmtilesServer = () => ({
	name: 'serve-pmtiles',
	configureServer(server) {
		servePMTilesMiddleware(server)
	},
	configurePreviewServer(server) {
		servePMTilesMiddleware(server)
	}
})

export default pmtilesServer
