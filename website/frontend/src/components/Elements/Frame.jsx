import React, { Component } from 'react';

export default class Frame extends Component {

    constructor(props) {
        super(props);

        this.state =
        {
            device_scale: 1,
            device_margin: 0,
        };

        this.device_ref = React.createRef()
        this.deviceInitialMargin = 100

        this.updateWindowDimensions = this.updateWindowDimensions.bind(this);
    }

    componentDidMount() {
        this.updateWindowDimensions();
        window.addEventListener('resize', this.updateWindowDimensions);
    }

    componentWillUnmount() {
        window.removeEventListener('resize', this.updateWindowDimensions);
    }

    updateWindowDimensions() {

        var deviceMargin = 0
        var deviceScale = 1

        var deviceHeight = this.device_ref.current.clientHeight + (this.deviceInitialMargin * 2)

        if (deviceHeight > window.innerHeight) {
            deviceScale = window.innerHeight / deviceHeight
            deviceMargin = (window.innerHeight - deviceHeight) / 2
        }

        this.setState({
            device_scale: deviceScale,
            device_margin: deviceMargin
        });
    }

    render() {
        return (
            <div ref={this.device_ref} style={{ margin: this.deviceInitialMargin + "px"}}>
                <style>
                    {`
                            .marvel-device
                            {
                                transform: scale(${this.state.device_scale});
                                margin: ${this.state.device_margin}px;
                            }
                        `}
                </style>
                <div  class="marvel-device iphone8" style={{float: "left"}}>
                {/* <div  class="marvel-device iphone8"> */}
                    <div class="screen">
                        {this.props.content}
                    </div>
                </div>
            </div>
        )
    }
}