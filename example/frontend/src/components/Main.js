import React from "react";
import PropTypes from "prop-types";

import { connect } from "react-redux";

import Login from "./Login";
import Access from "./Access";
import Validate from "./Validate";
import Register from "./Register/Register";


class Main extends React.Component {
    static propTypes = {
        validated: PropTypes.bool.isRequired,
        has_devices: PropTypes.bool.isRequired,
        authenticated: PropTypes.bool.isRequired,
    };

    render() {
        if (!this.props.authenticated)
            return <Login />;

        if (this.props.validated)
            return <Access />;

        if (this.props.has_devices)
            return <Validate />;



        return <Register />
    }
}

const mapStateToProps = state => ({
    validated: state.login.validated,
    has_devices: state.validate.devices.length !== 0,
    authenticated: state.login.authenticated,
});

export default connect(mapStateToProps)(Main);
