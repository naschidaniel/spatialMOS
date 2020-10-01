import React from "react";
import PropTypes from "prop-types";

export default function CustomTooltip(props) {
  const {active, payload} = props
  if (!active) return <div>No CustomTooltip available</div>;
  
  const apiData = payload[0].payload;

  if (payload.length === 0) return <div>No CustomTooltip available</div>;
  return (
    <div className="custom-tooltip">
      <p className="label">{apiData.tooltip_label}</p>
      <p>{`Max: ${apiData.spatialmos_max} ${apiData.unit}`}</p>
      <p>{`Mean: ${apiData.spatialmos_mean} ${apiData.unit}`}</p>
      <p>{`Min: ${apiData.spatialmos_min} ${apiData.unit}`}</p>
    </div>
        );

}

CustomTooltip.propTypes = {
    active: PropTypes.bool.isRequired,
    payload: PropTypes.arrayOf(PropTypes.number).isRequired,
  };
