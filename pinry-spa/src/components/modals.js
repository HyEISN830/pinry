import PinCreateModal from './pin_edit/PinCreateModal.vue';
import LoginForm from './LoginForm.vue';
import BoardEdit from './BoardEdit.vue';
import Add2Board from './pin_edit/Add2Board.vue';
import ComicCreateModal from './comic/ComicCreateModal.vue';
import ActionConfirmModal from './ActionConfirmModal.vue';
import scroll from './utils/scroll';

function runCreatedCallback(vm, callback, item) {
  if (typeof callback !== 'function') {
    return;
  }
  vm.$nextTick(() => callback(item));
}

function openPreservingScroll(vm, options) {
  const routeAtOpen = vm.$route ? vm.$route.fullPath : null;
  const restoreScroll = scroll.preserveModalScrollPosition(
    () => !routeAtOpen || !vm.$route || vm.$route.fullPath === routeAtOpen,
  );
  const modal = vm.$buefy.modal.open(Object.assign(
    { scroll: 'keep' },
    options,
  ));
  modal.$once('close', restoreScroll);
  return modal;
}

function openPinEdit(vm, props = null, onCreated = null) {
  return openPreservingScroll(
    vm,
    {
      parent: vm,
      component: PinCreateModal,
      props,
      hasModalCard: true,
      canCancel: ['escape', 'outside'],
      customClass: 'pinry-create-modal pinry-create-pin-modal',
      events: {
        pinCreated(pin) {
          runCreatedCallback(vm, onCreated, pin);
        },
      },
    },
  );
}

function openAdd2Board(vm, pin, username) {
  return openPreservingScroll(
    vm,
    {
      parent: vm,
      component: Add2Board,
      props: { pin, username },
      hasModalCard: true,
      canCancel: ['escape', 'outside'],
      customClass: 'pinry-create-modal pinry-action-modal pinry-add-board-modal',
    },
  );
}

function openActionConfirm(vm, props, onConfirm) {
  return openPreservingScroll(
    vm,
    {
      parent: vm,
      component: ActionConfirmModal,
      props,
      hasModalCard: true,
      canCancel: ['escape', 'outside'],
      customClass: 'pinry-create-modal pinry-action-modal pinry-confirm-modal',
      events: {
        confirm: onConfirm,
      },
    },
  );
}

function openBoardCreate(vm, onCreated = null) {
  return openPreservingScroll(
    vm,
    {
      parent: vm,
      component: BoardEdit,
      hasModalCard: true,
      canCancel: ['escape', 'outside'],
      customClass: 'pinry-create-modal pinry-create-board-modal',
      events: {
        boardCreated(board) {
          runCreatedCallback(vm, onCreated, board);
        },
      },
    },
  );
}

function openComicCreate(vm, username, onCreated = null) {
  return openPreservingScroll(
    vm,
    {
      parent: vm,
      component: ComicCreateModal,
      props: { username },
      hasModalCard: true,
      canCancel: ['escape', 'outside'],
      customClass: 'pinry-create-modal pinry-create-comic-modal',
      events: {
        comicCreated(comic) {
          runCreatedCallback(vm, onCreated, comic);
        },
      },
    },
  );
}

function openBoardEdit(vm, board, onSaved) {
  return openPreservingScroll(
    vm,
    {
      parent: vm,
      component: BoardEdit,
      props: {
        board,
        isEdit: true,
      },
      events: {
        boardSaved: onSaved,
      },
      hasModalCard: true,
      canCancel: ['escape', 'outside'],
      customClass: 'pinry-create-modal pinry-create-board-modal',
    },
  );
}

function openLogin(vm, onSucceed) {
  return openPreservingScroll(
    vm,
    {
      parent: vm,
      component: LoginForm,
      hasModalCard: true,
      canCancel: ['escape', 'outside'],
      customClass: 'pinry-create-modal pinry-auth-modal',
      events: {
        'login.succeed': onSucceed,
      },
    },
  );
}

export default {
  openBoardCreate,
  openComicCreate,
  openBoardEdit,
  openAdd2Board,
  openActionConfirm,
  openPinEdit,
  openLogin,
};
