import React, { Component } from 'react';

export default class InvalidBrowser extends Component {

    render() {
        return (
            <div 
              style={{
                display: "flex",
                justifyContent: "center",
                alignItems: "center",
                height: "100vh",
                color: "#ffffff",
                backgroundColor: "#000000"
              }}
            >
                <div>
                    The study is not supported on Internet Explorer or Microsoft Edge.
                    <br/>
                    <br/>
                    Please switch to Firefox or Chrome to complete this HIT
                </div>
            </div>
        )
    }
}

