<template>
  <div class="pins-for-board">
    <PHeader></PHeader>
    <CollectionHero
      type="board"
      :title="collection.title"
      :count="collection.count"
      :owner="collection.owner"
      :is-private="collection.private">
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

export default {
  name: 'Pins4Board',
  data() {
    return {
      filters: { boardFilter: null },
      collection: {
        title: '',
        count: null,
        owner: '',
        private: false,
      },
    };
  },
  components: {
    CollectionHero,
    PHeader,
    Pins,
  },
  beforeRouteUpdate(to, from, next) {
    this.filters = { boardFilter: to.params.boardId };
    this.collection = {
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
      this.fetchBoardMeta(this.$route.params.boardId);
    },
    fetchBoardMeta(boardId) {
      API.Board.get(boardId).then(
        (resp) => {
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
  },
};
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped lang="scss">
</style>
