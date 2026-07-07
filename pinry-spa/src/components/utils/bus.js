import Vue from 'vue';

const eventBus = new Vue();

export default {
  bus: eventBus,
  events: {
    notify: 'notify',
    refreshPin: 'refreshPin',
    refreshBoards: 'refreshBoards',
  },
};
