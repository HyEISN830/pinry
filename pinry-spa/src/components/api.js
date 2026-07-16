import axios from 'axios';
import storage from './utils/storage';
import uploadChunkedFile from './utils/chunkedUpload';

const API_PREFIX = '/api/v2/';

const Board = {
  create(name, private_ = false) {
    const url = `${API_PREFIX}boards/`;
    const data = { name, private: private_ };
    return new Promise(
      (resolve, reject) => {
        axios.post(url, data).then(
          (resp) => {
            if (resp.status !== 201) {
              reject(resp);
            }
            resolve(resp.data);
          },
          (error) => {
            reject(error.response);
          },
        );
      },
    );
  },
  get(boardId) {
    const url = `${API_PREFIX}boards/${boardId}/`;
    return axios.get(url);
  },
  fetchFullList(username) {
    const url = `${API_PREFIX}boards-auto-complete/?submitter__username=${username}`;
    return axios.get(url);
  },
  fetchSiteFullList() {
    const url = `${API_PREFIX}boards-auto-complete/`;
    return axios.get(url);
  },
  fetchListWhichContains(text, offset = 0, limit = 24) {
    const prefix = `${API_PREFIX}boards/?search=${text}`;
    const url = `${prefix}&offset=${offset}&limit=${limit}`;
    return axios.get(url);
  },
  saveChanges(boardId, fieldsForm) {
    const url = `${API_PREFIX}boards/${boardId}/`;
    return axios.patch(
      url,
      fieldsForm,
    );
  },
  addToBoard(boardId, pinIds) {
    const url = `${API_PREFIX}boards/${boardId}/`;
    return axios.patch(
      url,
      { pins_to_add: pinIds },
    );
  },
  removeFromBoard(boardId, pinIds) {
    const url = `${API_PREFIX}boards/${boardId}/`;
    return axios.patch(
      url,
      { pins_to_remove: pinIds },
    );
  },
  delete(boardId) {
    const url = `${API_PREFIX}boards/${boardId}/`;
    return axios.delete(url);
  },
};

const Comic = {
  create(data) {
    const url = `${API_PREFIX}comics/`;
    return axios.post(url, data);
  },
  fetchList(offset = 0, limit = 18, tagFilter = null, userFilter = null) {
    const url = `${API_PREFIX}comics/`;
    const params = {
      offset,
      limit,
      ordering: '-id',
    };
    if (tagFilter) {
      params.tags__name = tagFilter;
    }
    if (userFilter) {
      params.submitter__username = userFilter;
    }
    return axios.get(
      url,
      { params },
    );
  },
  get(comicId) {
    const url = `${API_PREFIX}comics/${comicId}/`;
    return axios.get(url);
  },
  saveChanges(comicId, data) {
    const url = `${API_PREFIX}comics/${comicId}/`;
    return axios.patch(url, data);
  },
  delete(comicId) {
    const url = `${API_PREFIX}comics/${comicId}/`;
    return axios.delete(url);
  },
  toggleLike(comicId) {
    const url = `${API_PREFIX}comics/${comicId}/like/`;
    return axios.post(url);
  },
};

const Pin = {
  create(jsonData) {
    const url = `${API_PREFIX}pins/`;
    return axios.post(
      url,
      jsonData,
    );
  },
  createFromURL(jsonData) {
    return this.create(jsonData);
  },
  createFromUploaded(jsonData) {
    return this.create(jsonData);
  },
  uploadImage(fileObject, progressHandler) {
    return uploadChunkedFile(fileObject, 'image', progressHandler);
  },
  deleteById(pinId) {
    const url = `${API_PREFIX}pins/${pinId}/`;
    return axios.delete(
      url,
    );
  },
  updateById(pinId, data) {
    const url = `${API_PREFIX}pins/${pinId}/`;
    return axios.patch(
      url,
      data,
    );
  },
  toggleLike(pinId) {
    const url = `${API_PREFIX}pins/${pinId}/like/`;
    return axios.post(url);
  },
  originalImageUrl(imageId) {
    return imageId ? `${API_PREFIX}images/${imageId}/original/` : null;
  },
  fetchOriginalImage(imageId, signal) {
    const url = this.originalImageUrl(imageId);
    const options = { credentials: 'same-origin' };
    if (signal) {
      options.signal = signal;
    }
    return fetch(url, options);
  },
};


function fetchPins(offset, tagFilter, userFilter, boardFilter) {
  const url = `${API_PREFIX}pins/`;
  const queryArgs = {
    format: 'json',
    ordering: '-id',
    limit: 18,
    offset,
  };
  if (tagFilter) queryArgs.tags__name = tagFilter;
  if (userFilter) queryArgs.submitter__username = userFilter;
  if (boardFilter) queryArgs.pins__id = boardFilter;
  return axios.get(
    url,
    { params: queryArgs },
  );
}

function fetchPin(pinId) {
  const url = `${API_PREFIX}pins/${pinId}`;
  return new Promise(
    (resolve, reject) => {
      const p = axios.get(
        url,
      );
      p.then(
        (resp) => {
          const response = {
            data: { results: [resp.data], next: null },
          };
          resolve(response);
        },
        (error) => {
          reject(error);
        },
      );
    },
  );
}

function fetchBoardForUser(username, offset = 0, limit = 24) {
  const prefix = `${API_PREFIX}boards/?submitter__username=${username}`;
  const url = `${prefix}&offset=${offset}&limit=${limit}`;
  return axios.get(url);
}

const User = {
  storageKey: 'pinry.user',
  logIn(username, password) {
    const url = `${API_PREFIX}profile/login/`;
    return new Promise(
      (resolve, reject) => {
        const p = axios.post(
          url,
          {
            username,
            password,
          },
        );
        p.then(
          (resp) => {
            if (resp.status !== 200) {
              reject(resp);
            }
            resolve(resp.data);
          },
          (error) => {
            console.log('Failed to log in due to unexpected error:', error);
            reject(error.response);
          },
        );
      },
    );
  },
  logOut() {
    const self = this;
    return new Promise(
      (resolve) => {
        axios.get('/api-auth/logout/').then(
          () => {
            storage.set(self.storageKey, null, 1);
            resolve();
          },
        );
      },
    );
  },
  uploadAvatar(fileObject, progressHandler) {
    return uploadChunkedFile(fileObject, 'avatar', progressHandler).then(
      (resp) => {
        storage.set(this.storageKey, resp.data, 60 * 5 * 1000);
        return resp;
      },
    );
  },
  fetchUserInfoByName(username) {
    /* returns null if user not logged in */
    const url = `${API_PREFIX}profile/public-users/?username=${username}`;
    return new Promise(
      (resolve) => {
        axios.get(url).then(
          (resp) => {
            const users = resp.data;
            if (users.length === 0) {
              return resolve(null);
            }
            return resolve(users[0]);
          },
        );
      },
    );
  },
  fetchUserInfo(force = false) {
    /* returns null if user not logged in */
    const self = this;
    if (!force) {
      const userInfo = storage.get(self.storageKey);
      if (userInfo !== null) {
        return new Promise(
          resolve => resolve(userInfo),
        );
      }
    }
    const url = `${API_PREFIX}profile/users/`;
    return new Promise(
      (resolve) => {
        axios.get(url).then(
          (resp) => {
            const users = resp.data;
            if (users.length === 0) {
              return resolve(null);
            }
            const value = users[0];
            storage.set(self.storageKey, value, 60 * 5 * 1000);
            return resolve(users[0]);
          },
        );
      },
    );
  },
};

const Tag = {
  fetchList() {
    const url = `${API_PREFIX}tags-auto-complete/`;
    return axios.get(url);
  },
};

const Search = {
  aggregate(query, type = 'all', offsets = {}, limit = 8) {
    const url = `${API_PREFIX}search/`;
    return axios.get(
      url,
      {
        params: {
          q: query,
          type,
          limit,
          pin_offset: offsets.pins || 0,
          board_offset: offsets.boards || 0,
          comic_offset: offsets.comics || 0,
          tag_offset: offsets.tags || 0,
        },
      },
    );
  },
};

export default {
  Search,
  Tag,
  Pin,
  Board,
  Comic,
  fetchPin,
  fetchPins,
  fetchBoardForUser,
  User,
};
