import React from 'react';
import { Text } from 'react-native';
import { Flip, ToastContainer } from 'react-toastify';

import SplitterLayout from 'react-splitter-layout';
import Device from '../Elements/Device';
import Frame from '../Elements/Frame';
import Progress from '../Elements/Progress';


import AudioButton from '../Elements/AudioButton'
import TrustwordSimulation from '../Elements/TrustwordSimulation'

import Experiment from './Experiment';

import phone_background from "../../images/foggy_forrest.jpg";

export default class VerbalVerification extends Experiment {

    constructor(props) {
        super(props, "verbal");

        this.state.round_index = -1;
        this.state.new_message = true;

        // TODO: Make this dynamic
        this.state.total_rounds = 20;
        
        this.audio_button_click = this.audio_button_click.bind(this);
    }

    refresh_attack_words() {
        this.setState({
            buttonToBeClicked: true,
            round_index: this.state.round_index + 1
        })
    }

    audio_button_click() {
        this.setState({
            buttonToBeClicked: false
        })
    }

    render() {

        const msg = "Communication with this contact will be secure and trusted by comparing the " +
            "following words with those read over the phone by Jane."

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

                <Progress total={this.state.total_rounds} index={this.state.round_index}/>

                <SplitterLayout percentage={"50%"} primaryMinSize={50} secondaryMinSize={50}>


                <div style={{ float: "right" }}>
                        <br />
                        <Text style={{ float: "center", fontSize: "15pt"}}>Phone Call</Text>

                        <Device content={

                            <div>
                                <div style={{
                                    background: "#273c75",
                                    backgroundImage: `url(${phone_background})`,
                                    filter: "blur(10px)",
                                    position: "absolute",
                                    top: 0,
                                    left: 0,
                                    right: 0,
                                    bottom: 0,
                                    zIndex: -1,
                                }}>
                                    {/* <Image src={{phone_background}}/> */}
                                </div>
                                <br/>
                                <br/>
                                <br/>
                                <Text style={{fontSize: "40px", color: "#e2e2e2"}}>
                                    Jane
                                </Text>
                                <br/>
                                <Text style={{color: "#e2e2e2"}}>Mobile</Text>

                                <div style={{
                                    display: 'flex',
                                    justifyContent: 'center',
                                    alignItems: 'center',
                                    height: '800px'
                                    // width: '100%'
                                }}>
                                    <AudioButton
                                        loading={this.state.loading}
                                        toggleButtonCallback={this.audio_button_click}
                                        wiggle={this.state.buttonToBeClicked}
                                    />
                                </div>
                            </div>

                            } />

                    </div>

                    <div style={{ float: "left" }}>
                        <br />
                        <Text style={{ float: "center", fontSize: "15pt"}}>Secure Messaging Application</Text>

                        <Frame content={
                            <TrustwordSimulation
                                resultCallback={this.userResponse}
                                words={this.state.trustWords}
                                loading={this.state.loading}
                                controlsDisabled={this.state.controlsDisabled || this.state.buttonToBeClicked}
                                message={msg}
                            />
                        } />
                    </div>

                </SplitterLayout>
            </div>
        )
    }
}