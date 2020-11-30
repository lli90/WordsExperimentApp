// SOURCE: https://github.com/pedreviljoen/react-native-wiggle-box

import React from "react"
import { Animated, TouchableOpacity, View, StyleSheet } from "react-native"
import PropTypes from "prop-types"

class WiggleBox extends React.Component {
  constructor(props) {
    super(props)
    this.rotation = new Animated.ValueXY()

    this.interval = setInterval(() => {
      if (this.props.active) {
        this.triggerWiggle();
      }
    }, this.props.time_period);
  }

  triggerWiggle = () => {
    const { duration } = this.props
    Animated.sequence([
      Animated.timing(this.rotation, {
        toValue: -4,
        duration: duration
      }),
      Animated.timing(this.rotation, {
        toValue: 4,
        duration: duration
      }),
      Animated.timing(this.rotation, {
        toValue: -4,
        duration: duration
      }),
      Animated.timing(this.rotation, {
        toValue: 4,
        duration: duration
      }),
      Animated.timing(this.rotation, {
        toValue: 0,
        duration: duration
      })
    ]).start()
  }

  getWiggleStyle() {
    const rotation = this.rotation
    const rotate = rotation.x.interpolate({
      inputRange: [-10, 0, 10],
      outputRange: ['-10deg', '0deg', '10deg']
    })

    return {
      ...rotation.getLayout(),
      transform: [{ rotate }]
    }
  }

  renderActive = () => {
    return (
      <TouchableOpacity onPress={this.props.handlePress}>
        <View>{this.props.children}</View>
      </TouchableOpacity>
    )
  }

  renderInactive = () => {
    return <View>{this.props.children}</View>
  }

  render() {
    const { active } = this.props

    return (
      <Animated.View
        style={[styles.boxContainer, active ? this.getWiggleStyle() : null]}
      >
        {active ? this.renderActive() : this.renderInactive()}
      </Animated.View>
    )
  }
}

WiggleBox.defaultProps = {
  active: false,
  handlePress: () => {},
  duration: 100,
  type: 'wiggle'
}

WiggleBox.propTypes = {
  active: PropTypes.bool,
  handlePress: PropTypes.func,
  duration: PropTypes.number,
  type: PropTypes.string
}

const styles = StyleSheet.create({
  boxContainer: {
    display: "flex",
    justifyContent: "center",
    alignItems: "center"
  }
})

export default WiggleBox
