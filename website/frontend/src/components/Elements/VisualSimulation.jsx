import React, { Component } from 'react';
import { Image, StyleSheet, Text } from 'react-native';
import Loader from 'react-loader-spinner'

import Bubble from '../Elements/Bubble';
import WiggleBox from './WiggleBox';

var message_top = require("../../images/test_image.png");
var new_message_img = require("../../images/message.png")

let styles = StyleSheet.create({
    top: {
        height: "100px",
        width: "100%",
        resizeMode: 'stretch'
    },
    generalFont: {
        color: "#919191",
        fontFamily: 'Roboto',
        fontSize: "9pt"
    },
    boxContainer: {
        backgroundColor: "#ffffff",
        height: 100,
        width: 100,
        alignItems: "center",
        justifyContent: "center"
    },
    blur: {
        filter: "blur(10px)",
    }
});

const loadingAnimation = <Loader type="ThreeDots" color="#a9a9a9" height="14" width="25" />

export default class VisualSimulation extends Component {

    constructor() {
        super();

        this.onClick = this.onClick.bind(this);
    }

    onClick() {
        this.props.callback();
    }

    render() {

        var display;
        if (this.props.loading === true) {
            display = loadingAnimation;
        } else {
            display = this.props.words;
        }

        var message_elements = (
            <div>
                <Bubble text={display} />
            </div>
        )

        var new_message_element = (
            <div
                style={{
                    height: "400px",
                    display: "flex",
                    justifyContent: "center",
                    alignItems: "center",
                    
                }}
            >
                <div>
                    <Text><strong>View words</strong></Text>
                    <br/><br/>
                    <WiggleBox
                        active={true}
                        handlePress={this.onClick}
                        duration={100}
                        time_period={2000}

                    >
                        <Image
                            source={new_message_img}
                            style={styles.boxContainer}
                        />
                    </WiggleBox>
                </div>
            </div>
        )

        var main_element = this.props.new_message ? new_message_element : message_elements;
        var possibleBlurStyle = this.props.new_message? styles.blur : ""

        return (

            <div>
                <Image
                    source={message_top}
                    style={[styles.top, possibleBlurStyle]}
                />
                <Text style={[styles.generalFont, possibleBlurStyle]}>
                    iMessage<br />
                    Today at 9.40am
                </Text>
                <br />
                {main_element}
            </div>
        )
    }
}