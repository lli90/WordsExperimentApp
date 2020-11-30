import React, { Component } from 'react';

import { BrowserRouter as Router, Route } from "react-router-dom";

import { isMobile, isEdge, isIE} from "react-device-detect";

// Global CSS imports
import './stylesheets/App.css'
import './stylesheets/devices.min.css'

import 'react-toastify/dist/ReactToastify.css';
import 'react-splitter-layout/lib/index.css';
import 'bootstrap/dist/css/bootstrap.min.css';

import VerbalVerification from './components/Experiment/VerbalVerification.jsx';
import VisualVerification from './components/Experiment/VisualVerification.jsx';
import PostExperiment from './components/InfoPages/PostExperiment.jsx'
import InvalidDevice from './components/InfoPages/InvalidDevice';
import CookiesRequired from './components/InfoPages/CookiesRequired';
import InvalidBrowser from './components/InfoPages/InvalidBrowser';


function areCookiesEnabled(){
  // Quick test if browser has cookieEnabled host property
  if (navigator.cookieEnabled) return true;
  // Create cookie
  document.cookie = "cookietest=1";
  var ret = document.cookie.indexOf("cookietest=") !== -1;
  // Delete cookie
  document.cookie = "cookietest=1; expires=Thu, 01-Jan-1970 00:00:01 GMT";
  return ret;
}


export default class App extends Component {

  render() {

    if (isEdge || isIE) {
      return <InvalidBrowser />
    }

    if (isMobile) {
      return <InvalidDevice />
    }

    if (!areCookiesEnabled()) {
      return <CookiesRequired />
    }

    return (
      <Router>
        <Route exact path="/verbal" component={VerbalVerification} />
        <Route exact path="/visual" component={VisualVerification} />
        <Route exact path="/post_experiment" component={PostExperiment} />
      </Router>
    );
  }
} 
