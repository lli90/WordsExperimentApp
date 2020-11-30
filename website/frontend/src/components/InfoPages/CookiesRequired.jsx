import React, { Component } from 'react';

export default class CookiesRequired extends Component {

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
                    This study cannot be completed with cookies deactivated.
                    <br/>
                    <br/>
                    Please enable cookies and reload the page.
              </div>
            </div>
        )
    }
}

