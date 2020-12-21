import React from 'react';
import { Text } from 'react-native';
import { Flip, ToastContainer } from 'react-toastify';

import SplitterLayout from 'react-splitter-layout';
import Device from '../Elements/Device';
import Frame from '../Elements/Frame';
import TrustwordSimulation from '../Elements/TrustwordSimulation'
import Progress from '../Elements/Progress';

import { URL_BASE, REQUEST_SETTINGS } from '../../global'
import VisualSimulation from '../Elements/VisualSimulation';
import Experiment from './Experiment';


export default class VisualVerification extends Experiment {

    constructor(props) {
        super(props, "visual");

        this.state.round_index = -1;
        this.state.new_message = true;

        // TODO: Make this dynamic
        this.state.total_rounds = 20;

        this.click_message_callback = this.click_message_callback.bind(this);
    }

    refresh_attack_words() {

        return fetch(URL_BASE + '/get_visual', REQUEST_SETTINGS)
            .then(response => response.text())
            .then(t => {
                if (!this.experimentFinished(t)) {
                    this.setState({
                        attackWords: t,
                        new_message: true,
                        round_index: this.state.round_index + 1
                    })
                }
            })
    }

    click_message_callback() {
        this.setState({
            new_message: false,
            controlsDisabled: false
        })

        fetch(URL_BASE + '/view_words_click', REQUEST_SETTINGS)
    }

    render() {

        const msg = "Communication with this contact will be secure and trusted by comparing the " +
            "following words with those received in the text message received from Jane."

        return (
            <div>
                <ToastContainer
                    position="top-center"
                    hideProgressBar={false}
                    autoClose={1000}
                    transition={Flip}
                    pauseOnHover={false}
                    newestOnTop
                />

                <Progress total={this.state.total_rounds} index={this.state.round_index} />

                <SplitterLayout percentage={"50%"} primaryMinSize={50} secondaryMinSize={50}>

                    <div style={{ float: "right" }}>
                        <br />
                        <Text style={{ float: "center", fontSize: "15pt" }}>Text Message</Text>

                        <Device
                            content={
                                <VisualSimulation
                                    words={this.state.attackWords}
                                    loading={this.state.loading}
                                    new_message={this.state.new_message}
                                    callback={this.click_message_callback}
                                />}
                        />
                    </div>


                    <div style={{ float: "left" }}>
                        <br />
                        <Text style={{ float: "center", fontSize: "15pt" }}>Secure Messaging Application</Text>

                        <Frame
                            content={
                                <TrustwordSimulation
                                    resultCallback={this.userResponse}
                                    words={this.state.trustWords}
                                    loading={this.state.loading}
                                    controlsDisabled={this.state.controlsDisabled || this.state.new_message}
                                    message={msg}
                                />
                            } />

                    </div>

                </SplitterLayout>
            </div>
        )
    }
}