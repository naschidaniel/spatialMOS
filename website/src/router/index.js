import { createRouter, createWebHashHistory } from "vue-router"

import Adresse from "../pages/Adresse.vue";
import Api from "../pages/Api.vue";
import Dsgvo from "../pages/Dsgvo.vue";
import Impressum from "../pages/Impressum.vue";
import Kontakt from "../pages/Kontakt.vue";
import Projektbeschreibung from "../pages/Projektbeschreibung.vue";
import Punktvorhersagen from "../pages/Punktvorhersagen.vue";
import Systemstatus from "../pages/Systemstatus.vue";
import Vorhersagekarten from "../pages/Vorhersagekarten.vue";

const router = createRouter({
  history: createWebHashHistory(),
  routes: [
    { path: '/', component: Vorhersagekarten },
    { path: '/adresse', component: Adresse },
    { path: '/api', component: Api },
    { path: '/dsgvo', component: Dsgvo },
    { path: '/impressum', component: Impressum },
    { path: '/kontakt', component: Kontakt },
    { path: '/projektbeschreibung', component: Projektbeschreibung },
    { path: '/punktvorhersagen', component: Punktvorhersagen },
    { path: '/systemstatus', component: Systemstatus },
  ],
})

export default router;
