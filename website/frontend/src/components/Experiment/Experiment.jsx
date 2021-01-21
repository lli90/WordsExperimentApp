import { Component } from 'react';
import { toast } from 'react-toastify';
import { URL_BASE, REQUEST_SETTINGS } from '../../global'


export default class Experiment extends Component {

    constructor(props, trialType) {
        super(props);
        this.state = {
            trustWords: "",
            attackWords: "",
            audio_url: [],
            loading: true,
            controlsDisabled: true
        }

        this.onAccept = this.onAccept.bind(this);
        this.onDecline = this.onDecline.bind(this);

        this.onDeclineRequest = this.onDeclineRequest.bind(this);
        this.onAcceptRequest = this.onAcceptRequest.bind(this);

        this.userResponse = this.userResponse.bind(this);
        this.toggleState = this.toggleState.bind(this);

        // Tells the backend what type of trial should be
        // passed with the new_experiment request
        this.trialType = trialType;

        this.setupExperiment();
    }

    /**
     * TODO
     */
    toggleState() {
        this.setState({
            loading: !this.state.loading,
            controlsDisabled: !this.state.controlsDisabled,
        })
    }

    /**
     * TODO
     */
    onAccept() {
        toast.success("CONFIRM")
        this.toggleState();
        this.onAcceptRequest()
            .then((r) => r.text())
            .then((r) => this.afterResponse())
    }

    
    /**
     * TODO
     */
    onDecline() {
        toast.error("REJECT")
        this.toggleState();
        this.onDeclineRequest()
            .then((r) => r.text())
            .then((r) => this.afterResponse())
    }

    /**
     * TODO
     */
    onAcceptRequest() {
        return fetch(URL_BASE + '/submit_result?result=True', REQUEST_SETTINGS)
    }

    /**
     * TODO
     */
    onDeclineRequest() {
        return fetch(URL_BASE + '/submit_result?result=False', REQUEST_SETTINGS)
    }

    /**
     * TODO
     */
    afterResponse() {
        if (!this.state.experimentHasFinished) {
            this.refresh_attack_words()
            this.refresh_words()
            this.toggleState()
        }
    }

    /**
     * TODO
     */
    setupExperiment() {
        fetch(URL_BASE + `/new_experiment?type=${this.trialType}`, REQUEST_SETTINGS)
            .then((r) => r.text())
            .then(() => this.refresh_attack_words())
            .then(() => this.refresh_words())
            .then(() => this.toggleState())
    }

    /**
     * TODO
     * @param {*} response_text 
     */
    experimentFinished(response_text) {
        if (response_text === "DONE") {

            this.props.history.push("/post_experiment")

            this.setState({
                controlsDisabled: true,
            })

            return true
        }

        return false
    }

    /**
     * Obtains the set of words that will never contain an attack
     */
    refresh_words() {

        return fetch(URL_BASE + '/get_words', REQUEST_SETTINGS)
            .then(response => response.text())
            .then(t => {
                if (!this.experimentFinished(t)) {
                    this.setState({
                        trustWords: t,
                    })
                }
            })
    }

    /**
     * Obtains the set of words that may contain an attack set
     */
    refresh_attack_words() {
        throw Error("Not implemented!")
    }

    /**
     * TODO
     * @param {*} responseType 
     */
    userResponse(responseType) {
        if (responseType === true) {
            this.onAccept();
        } else {
            this.onDecline();
        }
    }
}