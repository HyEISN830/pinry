// A list click and the detail component can mount during the same request.
// Share only that in-flight request; persistent de-duplication belongs to the
// API so account changes in one browser session still use the likes identity.
const pending = Object.create(null);

function mark(kind, id, request) {
  if (!id || typeof request !== 'function') {
    return Promise.resolve(null);
  }
  const key = `${kind}.${id}`;
  if (pending[key]) {
    return pending[key];
  }
  const task = Promise.resolve().then(request);
  pending[key] = task.then(
    (value) => {
      delete pending[key];
      return value;
    },
    (error) => {
      delete pending[key];
      throw error;
    },
  );
  return pending[key];
}

export default {
  markComic(id, request) { return mark('comic', id, request); },
  markPin(id, request) { return mark('pin', id, request); },
};
