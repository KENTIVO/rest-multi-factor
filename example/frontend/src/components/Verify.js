import React from "react";
import PropTypes from "prop-types";

import { connect } from "react-redux";

import { get_usr_devices } from "../actions/devices";
import { submit_verification } from "../actions/submit";

class Verify extends React.Component {
    static propTypes = {
        devices: PropTypes.arrayOf(PropTypes.object),
        verified: PropTypes.bool.isRequired,

        get_usr_devices: PropTypes.func.isRequired,
        submit_verification: PropTypes.func.isRequired,
    };

    constructor(props) {
        super(props);

        this.state = {
            value: null,
            current: null,
        }
    }

    componentDidMount() {
        this.props.get_usr_devices();
    }

    componentDidUpdate() {
        if (this.props.verified) {
            this.props.history.push("/");
            return;
        }

        if (this.props.devices.length !== 0)
            return;

        this.props.history.push("/register/");
    }

    onSelect(e) {
        this.setState({current: parseInt(e.target.value)});
    }

    onChange(e) {
        this.setState({value: e.target.value})
    }

    onSubmit(e) {
        if (this.state.current !== null && this.state.value !== null)
            this.props.submit_verification(this.state.current, this.state.value)
    }

    render() {
        return (
            <div>
                <select defaultValue={-1} onChange={this.onSelect.bind(this)}>
                    <option disabled value={-1}>Pleace select a device</option>
                    {
                        this.props.devices.map((device, key) => {
                            return <option key={key} value={device.index}>{device.verbose_name}</option>;
                        })
                    }
                </select>

                <input type="text" onChange={this.onChange.bind(this)}/>
                <input type="submit" value="Submit" onClick={this.onSubmit.bind(this)}/>
            </div>
        )
    }
}

const mapStateToProps = state => ({
    devices: state.verify.devices,
    verified: state.login.verified,
});

const mapDispatchToProps = {
    get_usr_devices,
    submit_verification,
};

export default connect(mapStateToProps, mapDispatchToProps)(Verify)
