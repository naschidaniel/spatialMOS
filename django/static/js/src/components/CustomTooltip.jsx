import React from "react";
import PropTypes from "prop-types";
import formatNumber from "../util/formatNumber";

export default function CustomTooltip(props) {
  const {active, payload} = props
  if (!active) return <div>No CustomTooltip available</div>;
  
  const apiData = payload[0].payload;
  return (
    <div className="custom-tooltip">
      <p className="label">{apiData.tooltip_label}</p>
      <p>{`Max: ${formatNumber(apiData.spatialmos_max, 2)} ${apiData.unit}`}</p>
      <p>{`Mean: ${formatNumber(apiData.spatialmos_mean, 2)} ${apiData.unit}`}</p>
      <p>{`Min: ${formatNumber(apiData.spatialmos_min, 2)} ${apiData.unit}`}</p>
    </div>
        );

}

CustomTooltip.propTypes = {
    active: PropTypes.bool,
    payload: PropTypes.arrayOf(PropTypes.object),
  };

CustomTooltip.defaultProps = {
  active: false,
  payload: [],
};