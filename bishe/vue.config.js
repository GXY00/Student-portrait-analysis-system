module.exports = {
  devServer: {
    port: 8080,
    proxy: {
      '/api': {
        target: 'http://localhost:5000', // 代理到 Flask
        changeOrigin: true,
        pathRewrite: {
          '^/api': '/api' // 保持路径不变
        }
      }
    }
  },
  lintOnSave: false
}
