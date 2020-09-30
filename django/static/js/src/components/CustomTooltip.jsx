import React from "react";
import PropTypes from "prop-types";

export default class CustomTooltip extends React.Component {
  constructor(props) {
    super(props);
  }

  static get propTypes() {
    return {
      active: PropTypes.bool,
      payload: PropTypes.array,
    };
  }

  render() {
    const { active, payload } = this.props;
    if (active) {
      if (payload.length === 0) return <div>No CustomTooltip available</div>;
      
        const apiData = payload[0].payload;
        return (
          <div className="custom-tooltip">
            <p className="label">{apiData.tooltip_label}</p>
            <p>{`Mean: ${apiData.spatialmos_mean} ${apiData.unit}`}</p>
            <p>{`Spread: ${apiData.spatialmos_spread} ${apiData.unit}`}</p>
          </div>
        );
      
    } return <div>No CustomTooltip available</div>;
  }
}
