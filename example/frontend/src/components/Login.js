import React from "react";
import PropTypes from "prop-types";

import { connect } from "react-redux"

import { login } from "../actions/login";

class Login extends React.Component {
    static propTypes = {
        login: PropTypes.func.isRequired,
        authenticated: PropTypes.bool.isRequired,
    };

    constructor(props) {
        super(props);

        this.state = {
            username: "",
            password: "",
        }
    }

    componentDidUpdate() {
        if (this.props.authenticated)
            this.props.history.push("/validate/");
    }

    onChange(e) {
        this.setState({[e.target.name]: e.target.value})
    }

    onSubmit(e) {
        this.props.login(
            this.state.username,
            this.state.password,
        );
    }

    render() {
        return (
            <div>
                <label htmlFor="username">Username: </label>
                <input id="username" name="username" onChange={this.onChange.bind(this)} type="text" />

                <br />

                <label htmlFor="password">Password: </label>
                <input id="password" name="password" onChange={this.onChange.bind(this)} type="password" />

                <br />

                <input id="submit" name="submit" type="submit" value="Submit" onClick={this.onSubmit.bind(this)} />
            </div>
        );
    }
}


export default connect(state => ({authenticated: state.login.authenticated}), {login})(Login);
