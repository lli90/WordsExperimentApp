import React, { Component } from 'react';
import { View, Image, StyleSheet, Text } from 'react-native';

import Loader from 'react-loader-spinner'
import ResponseButton from './ResponseButton';


var trustword_top = require("../../images/trustwords_top.jpg");
var trustword_filler = require("../../images/trustwords_filler.jpg");

const loadingAnimation = <Loader type="ThreeDots" color="#00BFFF" height="14" width="20" />

let styles = StyleSheet.create({
  top: {
    height: "75px",
    resizeMode: 'stretch'
  },
  filler: {
    height: "25vh",
    resizeMode: "stretch"
  },
  mainText: {
    textAlign: "left",
    width: '95%',
    margin: '15px',
    fontSize: '14px',
  }
});

export default class TrustwordSimulation extends Component {

  constructor(props) {
    super(props);

    this.onAcceptClick = this.onAcceptClick.bind(this)
    this.onDeclineClick = this.onDeclineClick.bind(this)
  }


  onAcceptClick() {
    this.props.resultCallback(true);
  }

  onDeclineClick() {
    this.props.resultCallback(false);
  }

  render() {

    // Adds a dialog box checking if refresh is the desired action
    window.onbeforeunload = function () { return "X"; }

    var display;
    if (this.props.loading === true) {
      display = loadingAnimation;
    } else {
      display = this.props.words;
    }

    return (
      <View style={{ backgroundColor: "white" }}>
        <Image
          source={trustword_top}
          style={styles.top}
        />
        <Text style={styles.mainText}>
          <strong>Partner:</strong>
          <br/>
          jane@hotmail.co.uk
          <br/><br/>
          <strong>Myself:</strong>
          <br/>
          alex@hotmail.co.uk
          <br/><br/>
          <strong style={{fontSize: "13px"}}>
            {this.props.message} 
          </strong> 
        </Text>
        <Text style={{ backgroundColor: "white", color: "black", margin: "10px" }}>
          {display}
        </Text>

        <div style={{display: 'flex', justifyContent: 'center', padding: "10px", gridGap: "40px"}}>
          <ResponseButton
            responseType={false}
            disabled={this.props.controlsDisabled}
            onClick={this.onDeclineClick}
          />
          <ResponseButton
            responseType={true}
            disabled={this.props.controlsDisabled}
            onClick={this.onAcceptClick}
          />
        </div>

        <Image
          source={trustword_filler}
          style={styles.filler}
        />

       
      </View>
    );
  }
}
