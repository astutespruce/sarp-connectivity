import path from 'path'
import adapter from '@sveltejs/adapter-static'
import { enhancedImages } from '@sveltejs/enhanced-img'
import { sveltekit } from '@sveltejs/kit/vite'
import { vitePreprocess } from '@sveltejs/vite-plugin-svelte'
import tailwindcss from '@tailwindcss/vite'
import { config as dotEnvConfig } from 'dotenv'
import { defineConfig } from 'vite'

// have to configure dotenv to load correct .env file
dotEnvConfig({ path: `.env.${process.env.NODE_ENV}` })

// only proxy API in development; in production it is proxied by Caddy
const proxyAPI = !!process.env.VITE_PROXY_API

// only serve PMTiles through vite in local development; they are served
// by Caddy in production.
// NOTE: we dynamically import the plugin to ensure it is not available in production
const servePMTiles = !!process.env.VITE_TILE_DIR
let pmtilesServer = () => undefined
if (servePMTiles) {
	pmtilesServer = (
		await import(path.resolve(import.meta.dirname, './src/plugins/pmtilesServer.ts'))
	).default
}

export default defineConfig({
	build: {
		rolldownOptions: {
			output: {
				// split mapbox its own chunk; it is large
				codeSplitting: {
					groups: [{ test: /mapbox-gl/, name: 'mapbox-gl' }]
				}
			}
		}
	},

	plugins: [
		tailwindcss(),
		enhancedImages(),
		sveltekit({
			extensions: ['.svelte'],
			preprocess: [vitePreprocess()],

			adapter: adapter({
				pages: 'public',
				assets: 'public',
				fallback: '404.html',
				precompress: false,
				strict: true
			})
		}),
		// middleware to serve PMTtiles in development mode
		servePMTiles ? pmtilesServer() : undefined
	],
	server: {
		fs: {
			allow: [
				path.resolve(import.meta.dirname, './package.json'),
				path.resolve(import.meta.dirname, './data'),
				...(servePMTiles ? [path.resolve(process.env.VITE_TILE_DIR as string)] : [])
			]
		},
		proxy: proxyAPI
			? {
					// proxy API endpoint to FastAPI
					'/api': {
						target: 'http://localhost:5000',
						changeOrigin: true
					}
				}
			: undefined
	}
})
