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
import openingPreference from './components/utils/openingPreference';
import layoutReady from './components/utils/layoutReady';
import sourceTooltip from './components/utils/sourceTooltip';
import './components/utils/motion-system.scss';
import './components/utils/grid-layout.scss';
import './components/utils/search-tag-pills.scss';
import './components/utils/home-theme-background.scss';
import './components/utils/content-card-actions.scss';
import './components/utils/user-shell.scss';
import './components/utils/collection-detail-shell.scss';
import './components/utils/loading-system.scss';
import './components/utils/create-modal-system.scss';
import './components/utils/action-modal-system.scss';
// import './registerServiceWorker';


Vue.config.productionTip = false;
Vue.use(Buefy, {
  defaultModalScroll: 'keep',
});
Vue.use(VueMasonryPlugin);
Vue.directive('layout-ready', layoutReady);
Vue.directive('source-tooltip', sourceTooltip);
Vue.use(VueI18n);
motionPreference.applySavedMotionPreference();
openingPreference.applySavedOpeningPreference();
setUpAxiosCsrfConfig();
setUpAxiosFeedback();

const supportedLocales = Object.keys(localeUtils.messages);
const requestedLocale = localStorage.getItem('localeCode') || navigator.language || 'en';
const normalizedLocale = String(requestedLocale).toLowerCase().split('-')[0];
let initialLocale = 'en';
if (supportedLocales.includes(requestedLocale)) {
  initialLocale = requestedLocale;
} else if (supportedLocales.includes(normalizedLocale)) {
  initialLocale = normalizedLocale;
}
document.documentElement.lang = initialLocale;

const i18n = new VueI18n({
  locale: initialLocale,
  fallbackLocale: 'en',
  messages: localeUtils.messages,
});

new Vue({
  router,
  i18n,
  render: h => h(App),
}).$mount('#app');
