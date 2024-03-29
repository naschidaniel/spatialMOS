import { createRouter, createWebHistory } from "vue-router";

import Adresse from "../pages/Adresse.vue";
import Api from "../pages/Api.vue";
import Dsgvo from "../pages/Dsgvo.vue";
import Impressum from "../pages/Impressum.vue";
import Karte from "../pages/Karte.vue";
import Kontakt from "../pages/Kontakt.vue";
import Projektbeschreibung from "../pages/Projektbeschreibung.vue";
import Punktvorhersagen from "../pages/Punktvorhersagen.vue";
import Systemstatus from "../pages/Systemstatus.vue";
import Vorhersagekarten from "../pages/Vorhersagekarten.vue";
import NotFound from "../pages/NotFound.vue";

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: "/", component: Vorhersagekarten },
    { path: "/adresse", component: Adresse },
    { path: "/api", component: Api },
    { path: "/dsgvo", component: Dsgvo },
    { path: "/impressum", component: Impressum },
    { path: "/karte", component: Karte },
    { path: "/kontakt", component: Kontakt },
    { path: "/projektbeschreibung", component: Projektbeschreibung },
    { path: "/systemstatus", component: Systemstatus },
    { path: "/:pathMatch(.*)*", name: "NotFound", component: NotFound },
  ],
});

export default router;
