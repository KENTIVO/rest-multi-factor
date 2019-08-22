import React from "react";
import PropTypes from "prop-types";

import { connect } from "react-redux";

import { get_usr_devices } from "../actions/devices";
import { submit_validation } from "../actions/submit";

class Validate extends React.Component {
    static propTypes = {
        devices: PropTypes.arrayOf(PropTypes.object),
        validated: PropTypes.bool.isRequired,

        get_usr_devices: PropTypes.func.isRequired,
        submit_validation: PropTypes.func.isRequired,
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
        if (this.props.validated) {
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
            this.props.submit_validation(this.state.current, this.state.value)
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
    devices: state.validate.devices,
    validated: state.login.validated,
});

const mapDispatchToProps = {
    get_usr_devices,
    submit_validation,
};

export default connect(mapStateToProps, mapDispatchToProps)(Validate)
