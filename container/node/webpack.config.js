const path = require("path");
const devMode = process.env.NODE_ENV !== 'production';

module.exports = {
  entry: {
    main: '/www/site/static/js/index.js'
  },
  output: {
    filename: '[name].js',
    chunkFilename: "[name].js",
    publicPath: "/static/",
    path: path.resolve(__dirname, 'static')
  },
  resolve: {
    modules: [
        path.resolve(__dirname, "site/static/js"),
        'node_modules'
    ],
    extensions: ['*', '.js', '.json']
  },
  module: {
    rules: [
      {
        test: /\.(js|jsx)$/,
        exclude: /node_modules/,
        use: {
          loader: "babel-loader"
        }
      }
    ]
  },
  devServer: {
    public: "http://0.0.0.0:8080",
    proxy: {
      '**': {
        target: 'http://nginx:80',
        changeOrigin: false
      }
    },
    host: "0.0.0.0",
    port: 8080,
    hot: true,
    https: false,
    headers: { "Access-Control-Allow-Origin": ["*"] }
    }
};
