import React, { Component } from 'react';

export default class ResponseButton extends Component {

    render() {

        var backgroundColour = '';
        var buttonText = '';

        if (this.props.responseType) {
            backgroundColour = '#5cdd5c';
            buttonText = "CONFIRM";
        }
        else {
            backgroundColour = '#ff5c5c';
            buttonText = "REJECT";
        }

        return (
            <button
                disabled={this.props.disabled}
                style={{ 'margin': '10px', "backgroundColor": backgroundColour, width: "90px"}}
                onClick={() => this.props.onClick()}>
                {buttonText}
            </button>
        )
    }
}