import axios from 'axios';
import storage from './storage';
import { notifyError } from './toast';

const USER_STORAGE_KEY = 'pinry.user';
const AUTH_EXPIRED_MESSAGE = '登录过期，请重新登录';
const NETWORK_ERROR_MESSAGE = '网络请求失败，请稍后重试';
const SERVER_ERROR_MESSAGE = '请求失败，请稍后重试';

function isApiRequest(config) {
  const url = config && config.url ? config.url : '';
  return url.indexOf('/api/') === 0
    || url.indexOf('/api-auth/') === 0;
}

function isAuthExpiredError(error) {
  if (!error.response) {
    return false;
  }
  const { status, data } = error.response;
  if (status === 401) {
    return true;
  }
  if (status !== 403) {
    return false;
  }
  if (typeof data === 'string') {
    return data.toLowerCase().indexOf('csrf') >= 0;
  }
  const detail = data && data.detail ? data.detail.toString().toLowerCase() : '';
  return detail.indexOf('authentication') >= 0
    || detail.indexOf('credentials') >= 0;
}

function setUpAxiosFeedback() {
  axios.interceptors.response.use(
    response => response,
    (error) => {
      if (isApiRequest(error.config) && isAuthExpiredError(error)) {
        storage.set(USER_STORAGE_KEY, null, 1);
        notifyError(AUTH_EXPIRED_MESSAGE);
      } else if (isApiRequest(error.config) && !error.response) {
        notifyError(NETWORK_ERROR_MESSAGE);
      } else if (
        isApiRequest(error.config)
        && error.response
        && error.response.status >= 500
      ) {
        notifyError(SERVER_ERROR_MESSAGE);
      }
      return Promise.reject(error);
    },
  );
}

export default setUpAxiosFeedback;
