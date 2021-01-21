import React, { Component } from 'react'
import { Text } from 'react-native';
import { Phone } from '@material-ui/icons';


import { URL_BASE, REQUEST_SETTINGS} from '../../global'
import LoadingOverlay from 'react-loading-overlay';
import Sound from 'react-sound'

import WiggleBox from './WiggleBox';

var LOADING_TEXT = "Loading audio"
var PLAYING_TEXT = "Playing audio"

var FIRST_PRESS_AUDIO_TEXT = "Listen to words"
var REPEAT_AUDIO_TEXT = "Repeat words"

export default class AudioButton extends Component {

    constructor(props) {
        super(props)

        this.state = {
            loading: false,
            playing: false,
            loadingText: LOADING_TEXT,
            id: this.randomNumber()
        }

        this.handleSongLoaded = this.handleSongLoaded.bind(this);
        this.handleSongFinishedPlaying = this.handleSongFinishedPlaying.bind(this);
        this._play_audio = this._play_audio.bind(this);
    }

    randomNumber() {
        return Math.random()
    }

    _play_audio() {

        this.setState({
            loading: true,
            playing: true,
            disabled: true,
            loadingText: LOADING_TEXT,
        })

        this.props.buttonClickCallback();
    }

    handleSongLoaded(sound) {
        console.log("LOADED!")

        this.setState({
            loading: false,
            loadingText: PLAYING_TEXT
        })

        fetch(URL_BASE + '/audio_playing', REQUEST_SETTINGS)
        .then(() => {})

        this.props.finishedLoadingCallback()
    }

    handleSongFinishedPlaying() {
        this.setState({
            playing: false,
            loading: false,
            id: this.randomNumber(),
            disabled: false,
        })

        this.props.finishedPlayingCallback()
    }

    render() {

        var buttonTextColor = "#5cdd5c"

        return (

            
                <LoadingOverlay
                    active={this.state.loading || this.state.playing}
                    text={this.state.loadingText}
                >

                
                {
                    !this.state.playing 
                    ?
                    <Text style={{color: "#ffffff", fontSize: "12pt"}}>
                        <strong> {this.props.wiggle ? FIRST_PRESS_AUDIO_TEXT : REPEAT_AUDIO_TEXT} </strong>
                    </Text> 
                    : 
                    <div/>
                }

                <br/><br/>
                <WiggleBox
                    active={!this.state.playing && this.props.wiggle}
                    duration={100}
                    time_period={1000}
                >
                    <div style={{width: "1000px"}}>
                    <button
                        style={{
                            align: "center",
                            width: "80px",
                            height: "80px",
                            color: "#ffffff",
                            backgroundColor: buttonTextColor,
                            borderRadius: "50%"
                        }}
                        disabled={this.props.disabled || this.state.disabled}
                        onClick={() => this._play_audio()}
                    >
                        <Phone size={250} />
                    </button>

                    {this.state.playing &&
                        <Sound
                            url={`${URL_BASE}/get_audio?id=${this.state.id}`}
                            playStatus={Sound.status.PLAYING}
                            onLoad={(loaded) => this.handleSongLoaded(loaded)}
                            onFinishedPlaying={() => this.handleSongFinishedPlaying()}
                        />
                    }
                    </div>
            </WiggleBox>
        </LoadingOverlay>

        )
    }
}

