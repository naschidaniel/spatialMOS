<template>
  <div class="container-lg my-3">
    <h1>Projektbeschreibung</h1>
    <h2>Allgemeine Projektbeschreibung</h2>
    <p>
      Auf Basis von vergangenen Stationsmesswerten und vergangenen Vorhersagen
      können zukünftige Vorhersagen von einem Wettermodell korrigiert werden.
      Diese Korrekturen basieren auf statistischen Methoden und werden geläufig
      als Model-Output-Statistik (MOS) bezeichnet. Bei diesem Projekt
      (spatialMOS) werden die Vorhersagen des globalen Wetter Modells GEFS mit
      eine Auflösung von 0,5 x 0,5 Grad für die Region Nord- und Südtirol
      verbessert. Es wird für die gesamte Region ein gültiges statistisches
      Modell erstellt. Es werden im Modell die Höhe über MSL, der Tag im Jahr
      und die geographische Position berücksichtigt. Als Geländemodell für Tirol
      werden die SRTM Daten verwendet (Mehr Informationen können über die
      Webseite https://gadm.org bezogen werden). Die Auflösung der mit
      spatialMOS erstellten Vorhersagen entspricht einem Grid von 90 x 90 m. Es
      können mithilfe von spatialMOS Temperatur- und relative Luftfeuchte- und
      für 2 m über der Topographie erstellt werden.
    </p>

    <p>
      Eine detaillierte Beschreibung der statistischen Methode kann in der
      Master Thesis
      <a
        href="https://diglib.uibk.ac.at/ulbtirolhs/content/titleinfo/2508296"
        target="_blank"
        >Flächenhafte Vorhersagen von Temperatur und relativer Luftfeuchte im
        Flachland</a
      >
      als auch im Paper
      <a
        href="https://econpapers.repec.org/paper/innwpaper/2016-08.htm"
        target="_blank"
        >Spatial Ensemble Post-Processing with Standardized Anomalies</a
      >
      nachgelesen werden.
    </p>
    <h2>Features</h2>
    <ul>
      <li>Alle Anwendungen werden mit Docker Containern betrieben</li>
      <li>Datamanagment mit Python</li>
      <li>Statistische Modellbildung mit R</li>
      <li>UI-Framwork mit VUE.JS</li>
      <li>Free https Suppport dank lets encrypt</li>
    </ul>
    <h2>Sourcecode</h2>
    <p>
      Der Sourcecode befindet sich auf Github im Repository und ist unter der
      "GNU General Public License v3.0" Lizenz frei verfügbar.
    </p>
  </div>
</template>
