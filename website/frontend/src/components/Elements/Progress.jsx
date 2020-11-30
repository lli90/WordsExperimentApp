import React, { Component } from 'react';
import { ProgressBar } from 'react-bootstrap'


export default class Progress extends Component {

    render() {
        var percentage = (this.props.index / this.props.total) * 100

        return (
            <div>
             <ProgressBar now={percentage} label={`${this.props.index}/${this.props.total}`}/>
            </div>
        )
    }
}