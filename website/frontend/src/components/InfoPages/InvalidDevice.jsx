import React, { Component } from 'react';

export default class InvalidDevice extends Component {

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
                    <br />
                    You are using an invalid device!
                    <br />
                    <br />
                    Please only use a computer or tablet.
                </div>
            </div>
        )
    }
}

