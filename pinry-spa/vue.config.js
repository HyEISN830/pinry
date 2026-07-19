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
    name: 'HyEISN Gallery',
    themeColor: '#EF7CBA',
    msTileColor: '#0F1218',
    appleMobileWebAppCapable: 'yes',
    appleMobileWebAppStatusBarStyle: 'black-translucent',
    workboxPluginMode: 'GenerateSW',
    manifestOptions: {
      name: 'HyEISN Gallery',
      short_name: 'HyEISN',
      description: 'A personal visual archive for collected images, comics, and inspiration.',
      id: '/',
      start_url: '/',
      scope: '/',
      display: 'standalone',
      background_color: '#0F1218',
      theme_color: '#EF7CBA',
      categories: ['art', 'photo', 'entertainment'],
      icons: [
        {
          src: './img/icons/android-chrome-192x192.png',
          sizes: '192x192',
          type: 'image/png',
          purpose: 'any',
        },
        {
          src: './img/icons/android-chrome-512x512.png',
          sizes: '512x512',
          type: 'image/png',
          purpose: 'any',
        },
        {
          src: './img/icons/android-chrome-maskable-192x192.png',
          sizes: '192x192',
          type: 'image/png',
          purpose: 'maskable',
        },
        {
          src: './img/icons/android-chrome-maskable-512x512.png',
          sizes: '512x512',
          type: 'image/png',
          purpose: 'maskable',
        },
      ],
    },
    iconPaths: {
      favicon32: 'img/icons/favicon-32x32.png',
      favicon16: 'img/icons/favicon-16x16.png',
      appleTouchIcon: 'img/icons/apple-touch-icon-180x180.png',
      maskIcon: null,
      msTileImage: 'img/icons/msapplication-icon-144x144.png',
    },
  },
};
