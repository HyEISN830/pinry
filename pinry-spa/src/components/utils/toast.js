import bus from './bus';

function notify(message, type = 'is-danger') {
  bus.bus.$emit(
    bus.events.notify,
    {
      message,
      type,
    },
  );
}

function notifySuccess(message) {
  notify(message, 'is-success');
}

function notifyError(message) {
  notify(message, 'is-danger');
}

export {
  notify,
  notifyError,
  notifySuccess,
};
