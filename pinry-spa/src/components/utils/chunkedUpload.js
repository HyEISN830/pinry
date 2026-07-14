import axios from 'axios';

const API_PREFIX = '/api/v2/uploads/';
const DEFAULT_RETRY_DELAY = 600;
const MAX_NETWORK_RETRIES = 4;
const MAX_PROCESSING_POLLS = 300;
const fileKeys = new WeakMap();

function delay(milliseconds) {
  return new Promise(
    resolve => window.setTimeout(resolve, Math.max(0, milliseconds || 0)),
  );
}

function uploadKey(file, target) {
  let keys = fileKeys.get(file);
  if (!keys) {
    keys = {};
    fileKeys.set(file, keys);
  }
  if (!keys[target]) {
    const randomPart = Math.random().toString(36).slice(2, 12);
    keys[target] = `${target}-${Date.now().toString(36)}-${randomPart}`;
  }
  return keys[target];
}

function emitProgress(progressHandler, loaded, total, phase = 'uploading') {
  if (typeof progressHandler !== 'function') {
    return;
  }
  progressHandler({
    lengthComputable: true,
    loaded,
    total,
    phase,
  });
}

function retryDelay(error) {
  const response = error && error.response ? error.response : null;
  const data = response && response.data ? response.data : {};
  const headerValue = response && response.headers
    ? response.headers['x-retry-after-ms']
    : null;
  const milliseconds = Number(data.retry_after_ms || headerValue);
  return Number.isFinite(milliseconds) && milliseconds > 0
    ? milliseconds
    : DEFAULT_RETRY_DELAY;
}

function shouldRetryRequest(error) {
  const response = error && error.response ? error.response : null;
  return !response || response.status >= 500;
}

function uploadError(message, code) {
  const error = new Error(message);
  error.code = code;
  return error;
}

function createSession(file, target, attempt = 0) {
  return axios.post(
    API_PREFIX,
    {
      target,
      filename: file.name || 'upload',
      content_type: file.type || '',
      total_size: file.size,
      client_key: uploadKey(file, target),
    },
  ).catch(
    (error) => {
      if (!shouldRetryRequest(error) || attempt >= MAX_NETWORK_RETRIES) {
        return Promise.reject(error);
      }
      return delay(DEFAULT_RETRY_DELAY * (attempt + 1)).then(
        () => createSession(file, target, attempt + 1),
      );
    },
  );
}

function fetchSession(uploadId) {
  return axios.get(`${API_PREFIX}${uploadId}/`);
}

function putChunk(uploadId, offset, chunk) {
  return axios.put(
    `${API_PREFIX}${uploadId}/chunk/`,
    chunk,
    {
      headers: {
        'Content-Type': 'application/octet-stream',
        'X-Upload-Length': chunk.size,
        'X-Upload-Offset': offset,
      },
    },
  );
}

function completeSession(uploadId, processingPolls = 0, retryCount = 0) {
  return axios.post(`${API_PREFIX}${uploadId}/complete/`).then(
    (resp) => {
      if (resp.status !== 202) {
        return resp;
      }
      if (processingPolls >= MAX_PROCESSING_POLLS) {
        return Promise.reject(uploadError(
          'Image processing timed out. Please upload the file again.',
          'UPLOAD_PROCESSING_TIMEOUT',
        ));
      }
      return delay(Math.min(2000, 350 + processingPolls * 150)).then(
        () => completeSession(uploadId, processingPolls + 1, 0),
      );
    },
    (error) => {
      if (!shouldRetryRequest(error) || retryCount >= MAX_NETWORK_RETRIES) {
        return Promise.reject(error);
      }
      return delay(DEFAULT_RETRY_DELAY * (retryCount + 1)).then(
        () => fetchSession(uploadId),
      ).then(
        (response) => {
          if (response.data.status === 'failed') {
            return Promise.reject(uploadError(
              'Image processing failed. Please upload the file again.',
              'UPLOAD_PROCESSING_FAILED',
            ));
          }
          return completeSession(uploadId, processingPolls, retryCount + 1);
        },
      );
    },
  );
}

function recoverOffset(uploadId, error, retryCount) {
  const response = error && error.response ? error.response : null;
  if (response && response.status === 409) {
    return Promise.resolve(response.data);
  }
  if (response && response.status === 429) {
    return delay(retryDelay(error)).then(
      () => ({ retry: true }),
    );
  }
  if (!shouldRetryRequest(error) || retryCount >= MAX_NETWORK_RETRIES) {
    return Promise.reject(error);
  }
  return delay(DEFAULT_RETRY_DELAY * (retryCount + 1)).then(
    () => fetchSession(uploadId),
  ).then(resp => resp.data);
}

function sendChunks(file, session, progressHandler, retryCount = 0) {
  const offset = Number(session.received_size) || 0;
  const chunkSize = Number(session.chunk_size) || 256 * 1024;
  emitProgress(progressHandler, offset, file.size);
  if (session.status === 'failed') {
    return Promise.reject(uploadError(
      'Image upload failed. Please upload the file again.',
      'UPLOAD_FAILED',
    ));
  }
  if (session.status === 'complete') {
    emitProgress(progressHandler, file.size, file.size, 'processing');
    return completeSession(session.id);
  }
  if (session.status === 'processing') {
    emitProgress(progressHandler, file.size, file.size, 'processing');
    return completeSession(session.id);
  }
  if (offset >= file.size) {
    emitProgress(progressHandler, file.size, file.size, 'processing');
    return completeSession(session.id);
  }
  const chunk = file.slice(offset, Math.min(file.size, offset + chunkSize));
  return putChunk(session.id, offset, chunk).then(
    (resp) => {
      const nextSession = resp.data;
      emitProgress(progressHandler, nextSession.received_size, file.size);
      return delay(nextSession.next_chunk_after_ms).then(
        () => sendChunks(file, nextSession, progressHandler, 0),
      );
    },
    error => recoverOffset(session.id, error, retryCount).then(
      (recoveredSession) => {
        if (recoveredSession.retry) {
          return sendChunks(file, session, progressHandler, retryCount);
        }
        return sendChunks(
          file,
          recoveredSession,
          progressHandler,
          retryCount + 1,
        );
      },
    ),
  );
}

export default function uploadChunkedFile(file, target, progressHandler) {
  if (!file || typeof file.slice !== 'function') {
    return Promise.reject(new TypeError('A valid file is required.'));
  }
  return createSession(file, target).then(
    (resp) => {
      emitProgress(progressHandler, resp.data.received_size, file.size);
      return sendChunks(file, resp.data, progressHandler);
    },
  ).then(
    response => ({
      data: response.data.result,
      upload: response.data,
    }),
  );
}
