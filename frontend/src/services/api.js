import axios from 'axios';

// 创建API实例
const api = axios.create({
  baseURL: '/api',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  }
});

// 请求拦截器
api.interceptors.request.use(
  (config) => {
    // 可以在这里添加认证token等
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 响应拦截器
api.interceptors.response.use(
  (response) => {
    return response.data;
  },
  (error) => {
    if (error.response) {
      // 服务器响应错误
      return Promise.reject(error.response.data);
    } else if (error.request) {
      // 网络错误
      return Promise.reject({ error: '网络连接失败，请检查网络' });
    } else {
      // 其他错误
      return Promise.reject({ error: error.message });
    }
  }
);

export default api;