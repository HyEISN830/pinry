import Buefy from 'buefy';
import Vue from 'vue';
import { VueMasonryPlugin } from 'vue-masonry';
import VueI18n from 'vue-i18n';
import localeUtils from './components/utils/i18n';
import App from './App.vue';
import router from './router';
import setUpAxiosCsrfConfig from './components/utils/csrf';
import setUpAxiosFeedback from './components/utils/apiFeedback';
import motionPreference from './components/utils/motionPreference';
import layoutReady from './components/utils/layoutReady';
import './components/utils/motion-system.scss';
import './components/utils/user-shell.scss';
// import './registerServiceWorker';


Vue.config.productionTip = false;
Vue.use(Buefy, {
  defaultModalScroll: 'keep',
});
Vue.use(VueMasonryPlugin);
Vue.directive('layout-ready', layoutReady);
Vue.use(VueI18n);
motionPreference.applySavedMotionPreference();
setUpAxiosCsrfConfig();
setUpAxiosFeedback();

const i18n = new VueI18n({
  locale: localStorage.getItem('localeCode') || navigator.language.split('-')[0],
  fallbackLocale: 'en',
  messages: localeUtils.messages,
});

new Vue({
  router,
  i18n,
  render: h => h(App),
}).$mount('#app');
