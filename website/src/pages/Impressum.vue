<template>
  <div class="container-lg">
    <h1>Impressum</h1>
    <p>
      Informationspflicht laut §5 E-Commerce Gesetz, §14 Unternehmensgesetzbuch,
      §63 Gewerbeordnung und Offenlegungspflicht laut §25 Mediengesetz.
    </p>

    <p>
      <strong>Daniel Naschberger</strong><br />
      Peter-Mayr-Straße 29<br />
      6020 Innsbruck<br />
      Österreich
    </p>
    <p>
      <strong>Unternehmensgegenstand:</strong> Dienstleistungen in der
      automatischen Datenverarbeitung und Informationstechnik<br />
      <strong>UID-Nummer:</strong> ATU61978818<br />
      <strong>Firmenbuchnummer:</strong> 22011541<br />
      <strong>Firmenbuchgericht:</strong> Innsbruck<br />
      <strong>Firmensitz:</strong> 6020 Innsbruck<br />
      <br />
      <strong>Tel.:</strong>
      <a target="_blank" href="tel:004369910030004">+43 699 10030004</a><br />
      <strong>E-Mail:</strong>
      <a target="_blank" href="mailto:daniel@naschi.at">daniel@naschi.at</a
      ><br />
      <br />
      <strong>Mitglied bei:</strong> WKO<br />
      <strong>Berufsrecht:</strong> Gewerbeordnung:
      <a target="_blank" href="https://www.ris.bka.gv.at">www.ris.bka.gv.at</a
      ><br />
      <br />
      <strong>Aufsichtsbehörde/Gewerbebehörde:</strong> Bezirkshauptmannschaft
      innsbruck<br />
      <strong>Berufsbezeichnung:</strong> IT-Dienstleistungen<br />
      <strong>Verleihungsstaat:</strong> Österreich<br />
    </p>

    <h2>EU-Streitschlichtung</h2>
    <p>
      Gemäß Verordnung über Online-Streitbeilegung in Verbraucherangelegenheiten
      (ODR-Verordnung) möchten wir Sie über die Online-Streitbeilegungsplattform
      (OS-Plattform) informieren.<br />
      Verbraucher haben die Möglichkeit, Beschwerden an die Online
      Streitbeilegungsplattform der Europäischen Kommission unter
      <a target="_blank" href="https://ec.europa.eu/odr?tid=121389948"
        >https://ec.europa.eu/odr?tid=121389948</a
      >
      zu richten. Die dafür notwendigen Kontaktdaten finden Sie oberhalb in
      unserem Impressum.
    </p>
    <p>
      Wir möchten Sie jedoch darauf hinweisen, dass wir nicht bereit oder
      verpflichtet sind, an Streitbeilegungsverfahren vor einer
      Verbraucherschlichtungsstelle teilzunehmen.
    </p>

    <h2>Haftung für Inhalte dieser Webseite</h2>
    <p>
      Wir entwickeln die Inhalte dieser Webseite ständig weiter und bemühen uns
      korrekte und aktuelle Informationen bereitzustellen. Leider können wir
      keine Haftung für die Korrektheit aller Inhalte auf dieser Webseite
      übernehmen, speziell für jene die seitens Dritter bereitgestellt wurden.
    </p>
    <p>
      Sollten Ihnen problematische oder rechtswidrige Inhalte auffallen, bitten
      wir Sie uns umgehend zu kontaktieren, Sie finden die Kontaktdaten im
      Impressum.
    </p>

    <h2>Haftung für Links auf dieser Webseite</h2>

    <p>
      Unsere Webseite enthält Links zu anderen Webseiten für deren Inhalt wir
      nicht verantwortlich sind. Haftung für verlinkte Websites besteht laut §
      17 ECG für uns nicht, da wir keine Kenntnis rechtswidriger Tätigkeiten
      hatten und haben, uns solche Rechtswidrigkeiten auch bisher nicht
      aufgefallen sind und wir Links sofort entfernen würden, wenn uns
      Rechtswidrigkeiten bekannt werden.
    </p>
    <p>
      Wenn Ihnen rechtswidrige Links auf unserer Website auffallen, bitten wir
      Sie uns zu kontaktieren, Sie finden die Kontaktdaten im Impressum.
    </p>

    <h2>Urheberrechtshinweis</h2>
    <p>
      Alle Inhalte dieser Webseite (Bilder, Fotos, Texte, Videos) unterliegen
      dem Urheberrecht. Falls notwendig, werden wir die unerlaubte Nutzung von
      Teilen der Inhalte unserer Seite rechtlich verfolgen.
    </p>

    <p></p>
    <p>
      Sollten Sie auf dieser Webseite Inhalte finden, die das Urheberrecht
      verletzen, bitten wir Sie uns zu kontaktieren.
    </p>
    <h2>Bildernachweis</h2>
    <p>
      Die Bilder, Fotos und Grafiken auf dieser Webseite sind urheberrechtlich
      mit der Lizenz
      <a
        href="https://creativecommons.org/licenses/by-nc-sa/3.0/"
        target="_blank"
        >CC BY-NC-SA 3.0</a
      >
      geschützt.
    </p>
    <h2>Verwendete Softwarepakete und Lizenzinformation</h2>
    <ul>
      <li v-for="dependency in dependencies" :key="dependency.version">
        <span style="font-weight: bold">{{ dependency.name }} </span> –
        <span style="font-style: italic">{{ dependency.version }}</span> –
        {{ dependency.license }} License
      </li>
    </ul>
  </div>
</template>

<script setup lang="ts">
import { Dependency } from "../model/dependency";

const dependencies: Dependency[] = JSON.parse(
  import.meta.env.VITE_APP_DEPENDENCIES
);
</script>
