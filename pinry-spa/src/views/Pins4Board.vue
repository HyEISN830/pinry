<template>
  <div class="pins-for-board collection-detail-page">
    <PHeader></PHeader>
    <CollectionHero
      type="board"
      :title="collection.title"
      :count="collection.count"
      :owner="collection.owner"
      :is-private="collection.private"
      :can-create-pin="canCreatePin"
      :can-share="collection.id !== null"
      v-on:create-pin="createPinForBoard"
      v-on:share="shareBoard">
    </CollectionHero>
    <Pins
      :pin-filters="filters"
      v-on:pins-meta-loaded="onPinsMetaLoaded">
    </Pins>
  </div>
</template>

<script>
import API from '../components/api';
import PHeader from '../components/PHeader.vue';
import Pins from '../components/Pins.vue';
import CollectionHero from '../components/CollectionHero.vue';
import modals from '../components/modals';
import share from '../components/utils/share';

export default {
  name: 'Pins4Board',
  data() {
    return {
      filters: { boardFilter: null },
      collection: {
        id: null,
        title: '',
        count: null,
        owner: '',
        private: false,
      },
      user: {
        loggedIn: false,
        meta: {},
      },
    };
  },
  components: {
    CollectionHero,
    PHeader,
    Pins,
  },
  computed: {
    canCreatePin() {
      return (
        this.user.loggedIn
        && this.collection.owner === this.user.meta.username
      );
    },
  },
  beforeRouteUpdate(to, from, next) {
    this.filters = { boardFilter: to.params.boardId };
    this.collection = {
      id: null,
      title: '',
      count: null,
      owner: '',
      private: false,
    };
    this.fetchBoardMeta(to.params.boardId);
    next();
  },
  created() {
    this.initializeBoard();
  },
  methods: {
    initializeBoard() {
      this.filters = { boardFilter: this.$route.params.boardId };
      this.fetchUserMeta();
      this.fetchBoardMeta(this.$route.params.boardId);
    },
    fetchUserMeta() {
      API.User.fetchUserInfo().then(
        (user) => {
          if (user === null) {
            this.user.loggedIn = false;
            this.user.meta = {};
            return;
          }
          this.user.loggedIn = true;
          this.user.meta = user;
        },
      );
    },
    fetchBoardMeta(boardId) {
      API.Board.get(boardId).then(
        (resp) => {
          this.collection.id = resp.data.id;
          this.collection.title = resp.data.name;
          this.collection.count = resp.data.total_pins;
          this.collection.owner = resp.data.submitter.username;
          this.collection.private = resp.data.private;
        },
        () => {
          this.$router.push({ name: 'PageNotFound' });
        },
      );
    },
    onPinsMetaLoaded(meta) {
      this.collection.count = meta.count;
    },
    createPinForBoard() {
      if (!this.canCreatePin) {
        return;
      }
      modals.openPinEdit(
        this,
        {
          username: this.user.meta.username,
          defaultBoard: {
            id: this.collection.id,
            name: this.collection.title,
          },
        },
      );
    },
    shareBoard() {
      if (this.collection.id === null) {
        return;
      }
      share.shareRoute(
        this,
        { name: 'board', params: { boardId: this.collection.id } },
      );
    },
  },
};
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped lang="scss">
</style>
