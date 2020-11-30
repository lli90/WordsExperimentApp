import React, { Component } from 'react';
import { Text, StyleSheet} from 'react-native';

import Box from '@material-ui/core/Box';

let styles = StyleSheet.create({
    message: {
        // fontFamily: 'Roboto',
    },
});

export default class Bubble extends Component {

    render() {
        return <div>
            <Box p={2}>
                <Box bgcolor={"#e9e8eb"}
                css={{
                    borderRadius: "2em", 
                    padding: "1em", 
                    maxWidth: "fit-content", 
                    // margin: "none",
                    textAlign: "left",
                    boxShadow: "0px 2px 10px rgba(162, 155, 254, 0.25)",
                    fontSize: "15px"
                }} >
                    {
                        <Text style={styles.message}>
                            {this.props.text}
                        </Text>
                    }
                </Box>
            </Box>
        </div>
    }
}