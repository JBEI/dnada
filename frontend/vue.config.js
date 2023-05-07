const CompressionPlugin = require('compression-webpack-plugin');
const VuetifyLoaderPlugin = require('vuetify-loader/lib/plugin');

module.exports = {
  // Fix Vuex-typescript in prod: https://github.com/istrib/vuex-typescript/issues/13#issuecomment-409869231
  configureWebpack: (config) => {
    if (process.env.NODE_ENV === 'production') {
      config.optimization.minimizer[0].options.terserOptions = Object.assign(
        {},
        config.optimization.minimizer[0].options.terserOptions,
        {
          ecma: 5,
          compress: {
            keep_fnames: true,
          },
          warnings: false,
          mangle: {
            keep_fnames: true,
          },
        },
      );
    }
  },
  productionSourceMap: false,
  chainWebpack: config => {
    config.module
      .rule('vue')
      .use('vue-loader')
      .loader('vue-loader')
      .tap(options => Object.assign(options, {
        transformAssetUrls: {
          'v-img': ['src', 'lazy-src'],
          'v-card': 'src',
          'v-card-media': 'src',
          'v-responsive': 'src',
        }
      }));
    config.module.delete('prefetch');
    config.plugin('CompressionPlugin').use(CompressionPlugin);
    config.plugin('VuetifyLoaderPlugin').use(VuetifyLoaderPlugin);
  },
}
