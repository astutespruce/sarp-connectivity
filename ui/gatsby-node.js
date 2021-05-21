const path = require('path-browserify')

exports.onCreateWebpackConfig = ({ actions, stage, loaders, plugins }) => {
  const config = {
    resolve: {
      alias: {
        path: require.resolve('path-browserify'),
      },
      fallback: {
        fs: false,
        // process: false,
      },

      // Enable absolute imports with `/src` as root.
      modules: [path.resolve(__dirname, 'src'), 'node_modules'],
    },
    plugins: [plugins.provide({ process: 'process/browser' })],
  }

  // when building HTML, window is not defined, so mapbox-gl causes the build to blow up
  if (stage === 'build-html') {
    config.module = {
      rules: [
        {
          test: /mapbox-gl/,
          use: loaders.null(),
        },
      ],
    }
  }

  actions.setWebpackConfig(config)
}
