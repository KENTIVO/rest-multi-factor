import React from 'react';
import PropTypes from "prop-types";

import { connect } from "react-redux";

import { logout } from "../actions/login";
import { request_access } from "../actions/access";


class Access extends React.Component {
    static propTypes = {
        content: PropTypes.string.isRequired,
        validated: PropTypes.bool.isRequired,
        authenticated: PropTypes.bool.isRequired,

        logout: PropTypes.func.isRequired,
        request_access: PropTypes.func.isRequired,
    };

    componentDidMount() {
        this.permissionCheck();
        this.props.request_access()
    }

    componentDidUpdate() {
        this.permissionCheck();
    }

    permissionCheck() {
        if (!this.props.authenticated)
            this.props.history.push("/login/");

        else if (!this.props.validated)
            this.props.history.push("/validate/");
    }

    render() {
        return (
            <div>
                <p>{this.props.content}</p>
                <input type="submit" value="logout" onClick={this.props.logout} />
            </div>
        );
    }
}

const mapStateToProps = state => ({
    content: state.access.content,
    validated: state.login.validated,
    authenticated: state.login.authenticated,
});

export default connect(mapStateToProps, {request_access, logout})(Access);
