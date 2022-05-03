import { ref, onMounted, unref, watchEffect } from "vue";
import { FeatureGroup, Tooltip, Marker, Map, Control } from "leaflet";
import L from "leaflet";

import { usePhotonApi } from "../store/usePhotonApi";
import { usePredictions } from "../store/usePredictions";

// fix "Uncaught TypeError: this._map is null" when zooming
/* eslint-disable @typescript-eslint/no-explicit-any */
(Tooltip.prototype as any)._updatePosition = function () {
  if (!this._map || !this._latlng) return;
  const pos = this._map.latLngToLayerPoint(this._latlng);
  this._setPosition(pos);
};
/* eslint-disable @typescript-eslint/no-explicit-any */
(Tooltip.prototype as any)._animateZoom = function (e: any) {
  if (!this._map || !this._latlng) return;
  const pos = this._map._latLngToNewLayerPoint(this._latlng, e.zoom, e.center);
  this._setPosition(pos);
};

const control = ref(undefined as unknown as Control);
const map = ref(undefined as unknown as Map);

export function useLeafletMap() {
  const { latlon, lat, lon, tooltip } = usePhotonApi();
  const { spatialImage, fetchPrediction } = usePredictions();

  onMounted(async () => {
    map.value = L.map("mapContainer", {
      attributionControl: false,
      minZoom: 6,
      maxZoom: 13,
    });
    await fetchPrediction();
    const southWest = unref(spatialImage).southWest;
    const northEast = unref(spatialImage).northEast;
    const latidude =
      lat.value || southWest[0] + (northEast[0] - southWest[0]) / 2;
    const longitude =
      lon.value || southWest[1] + (northEast[1] - southWest[1]) / 2;
    map.value.setView([latidude, longitude], 9) as Map;
    createControl();
    spatialPlot().addTo(map.value as Map);
    updateMarker();
  });

  function createControl(): void {
    const beschriftung = L.tileLayer(
      `https://maps.wien.gv.at/basemap/bmapoverlay/normal/google3857/{z}/{y}/{x}.png`,
      {
        pane: "markerPane",
      }
    );

    const gelande = L.tileLayer(
      `https://maps.wien.gv.at/basemap/bmapgelaende/grau/google3857/{z}/{y}/{x}.jpeg`,
      {
        attribution:
          "<a href='https://basemap.at/' target='_blank' rel='noreferrer'>basemap.at</a>",
      }
    );

    const osm = L.tileLayer("https://{s}.tile.osm.org/{z}/{x}/{y}.png", {
      attribution:
        "<a href='https://www.openstreetmap.org' target='_blank' rel='noreferrer'>OpenStreetMap-Mitwirkende</a>",
    });

    const baseLayers = {
      Gelände: gelande.addTo(map.value as Map),
      OpenStreetMap: osm,
    };

    const overlays = {
      Beschriftung: beschriftung,
    };

    control.value = L.control.layers(baseLayers, overlays);
    control.value.addTo(map.value as Map);
  }

  watchEffect((spatialImage) => {
    if (map.value === undefined) return;
    spatialPlot().addTo(map.value as Map);
  });

  watchEffect((latlon) => {
    if (map.value === undefined) return;
    updateMarker();
  });

  function updateMarker(): void {
    if (latlon.value === undefined) {
      return;
    }
    const _latlng = L.latLng(latlon.value);
    map.value.setView(_latlng);
    tooltip.value === ""
      ? new Marker(_latlng).addTo(map.value as Map)
      : new Marker(_latlng)
          .bindTooltip(tooltip.value)
          .openTooltip()
          .addTo(map.value as Map);
  }

  function spatialPlot(): FeatureGroup {
    const overlayImageGroup = L.featureGroup([], {
      id: "spatialmosMaps",
      pane: "overlayPane",
    });
    const overlay = unref(spatialImage).overlay;
    const southWest = unref(spatialImage).southWest;
    const northEast = unref(spatialImage).northEast;
    if (overlay === "") return overlayImageGroup;
    map.value.eachLayer(
      (layer) => layer?.options?.id === "spatialmosMaps" && layer.remove()
    );
    const _southWest = L.latLng(southWest[0], southWest[1]);
    const _northEast = L.latLng(northEast[0], northEast[1]);
    const imageBounds = L.latLngBounds(_southWest, _northEast);
    const image = L.imageOverlay(overlay, imageBounds, {
      id: "spatialmosImage",
      pane: "overlayPane",
      className: "mix-blend-mode-multiply",
      opacity: 0.85,
    });

    if (map.value.attributionControl) {
      map.value.attributionControl.remove();
    }
    image.addTo(overlayImageGroup);
    return overlayImageGroup;
  }

  return { control, map, updateMarker, spatialPlot };
}
