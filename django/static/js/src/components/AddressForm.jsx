import React, { Component } from "react";
import ReactDOM from "react-dom";


export default class AddressForm extends React.Component {
  constructor() {
    super();

    this.state = {
      value: ""
    };

    this.handleChange = this.handleChange.bind(this);
  }

  handleChange(event) {
    const { value } = event.target;
    this.setState(() => {
      return {
        value
      };
    });
  }

  render() {
    return (
      <form>
        <input
          className="form-control"
          type="text"
          value={this.state.value}
          onChange={this.handleChange}
        />
        <button type="submit" className="btn btn-primary">Submit</button>
      </form>
    );
  }
}

const wrapper = document.getElementById("address_form_container");
wrapper ? ReactDOM.render(<AddressForm />, wrapper) : false;