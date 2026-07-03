const path = require('path');

module.exports = {
  publicPath: '/static/spa/',
  outputDir: path.resolve(__dirname, '../pinry/static/spa'),
  indexPath: path.resolve(__dirname, '../pinry/templates/index.html'),

  devServer: {
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000/',
        changeOrigin: true,
        ws: true,
      },
      '/media': {
        target: 'http://127.0.0.1:8000/',
        changeOrigin: true,
      },
      '/static/js/': {
        target: 'http://127.0.0.1:8000/',
        changeOrigin: true,
      },
    },
  },

  pwa: {
    name: 'Pinry Mobile',
    appleMobileWebAppCapable: 'yes',
    appleMobileWebAppStatusBarStyle: 'black',
    workboxPluginMode: 'GenerateSW',
    iconPaths: {
      favicon32: 'favicon.png',
      favicon16: 'favicon.png',
      appleTouchIcon: 'favicon.png',
      msTileImage: 'favicon.png',
    },
  },
};
