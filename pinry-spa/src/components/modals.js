import PinCreateModal from './pin_edit/PinCreateModal.vue';
import LoginForm from './LoginForm.vue';
import SignUpForm from './SignUpForm.vue';
import BoardEdit from './BoardEdit.vue';
import Add2Board from './pin_edit/Add2Board.vue';
import ComicCreateModal from './comic/ComicCreateModal.vue';

function runCreatedCallback(vm, callback, item) {
  if (typeof callback !== 'function') {
    return;
  }
  vm.$nextTick(() => callback(item));
}

function openPinEdit(vm, props = null, onCreated = null) {
  vm.$buefy.modal.open(
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
  vm.$buefy.modal.open(
    {
      parent: vm,
      component: Add2Board,
      props: { pin, username },
      hasModalCard: true,
    },
  );
}

function openBoardCreate(vm, onCreated = null) {
  vm.$buefy.modal.open(
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
  vm.$buefy.modal.open(
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
  vm.$buefy.modal.open(
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
  vm.$buefy.modal.open({
    parent: vm,
    component: LoginForm,
    hasModalCard: true,
    events: {
      'login.succeed': onSucceed,
    },
  });
}

function openSignUp(vm, onSignUpSucceed) {
  vm.$buefy.modal.open({
    parent: vm,
    component: SignUpForm,
    hasModalCard: true,
    events: {
      'signup.succeed': onSignUpSucceed,
    },
  });
}

export default {
  openBoardCreate,
  openComicCreate,
  openBoardEdit,
  openAdd2Board,
  openPinEdit,
  openLogin,
  openSignUp,
};
